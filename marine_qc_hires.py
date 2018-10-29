#!/usr/local/sci/bin/python2.7
'''
marine_qc_hires.py invoked by typing::

  python2.7 marine_qc_hires.py -config configuration.txt -year1 1850 -year2 1855 -month1 1 -month2 12

This quality controls the data for the chosen years using the high 
resolution SST climatology. The location of the data base, the locations 
of the climatology files are to be specified in the configuration files.

'''

import gzip
import csv
from netCDF4 import Dataset
import qc
from IMMA1 import IMMA
import Extended_IMMA as ex
import Climatology as clim
import argparse
import ConfigParser
import json
import sys

def process_bad_id_file(bad_id_file):
    '''
    Read in each entry in the bad id file and if it is shorter than 9 characters 
    pad with white space at the end of the string
    '''
    idfile = open(bad_id_file, 'r')
    ids_to_exclude = []
    for line in idfile:
        line = line.rstrip()
        while len(line) < 9:
            line = line+' '
        if line != '         ':
            ids_to_exclude.append(line)
    idfile.close()
    return ids_to_exclude

def icoads_filename(icoads_dir, readyear, readmonth, version):

    assert version in ['2.5','3.0'], "name not 2.5 or 3.0"

    syr = str(readyear)
    smn = "%02d" % (readmonth) 
    
    if version == '2.5':
        filename = icoads_dir+'/ICOADS.2.5.1/R2.5.1.'+syr+'.'+smn+'.gz'
        if ((readyear > 2007) & (readyear < 2015)):
            filename = icoads_dir+'/R2.5.2.'+syr+'.'+smn+'.gz'

    if version == '3.0':
        if readyear <= 2014:
            filename = icoads_dir+'/ICOADS.3.0.0/IMMA1_R3.0.0_'+syr+'-'+smn+'.gz'
        if readyear >= 2015:
            filename = icoads_dir+'/ICOADS.3.0.1/IMMA1_R3.0.1_'+syr+'-'+smn+'.gz'
            
    return filename

def main(argv):
    '''
    This program reads in data from ICOADS.2.5.1 and applies quality control processes to it, flagging data as 
    good or bad according to a set of different criteria.

    The first step of the process is to read in various SST and MAT climatologies from file. These are 1degree latitude 
    by 1 degree longitude by 73 pentad fields in NetCDF format.
    
    The program then loops over all specified years and months reads in the data needed to QC that month and then 
    does the QC. There are three stages in the QC
    
    basic QC - this proceeds one observation at a time. Checks are relatively simple and detect gross errors
    
    track check - this works on Voyages consisting of all the observations from a single ship (or at least a single ID) 
    and identifies observations which make for an implausible ship track
    
    buddy check - this works on Decks which are large collections of observations and compares observations to their neighbours
    '''
    
    print '########################'
    print 'Running make_and_full_qc'
    print '########################'

    parser = argparse.ArgumentParser(description='Marine QC system, main program')
    parser.add_argument('-config', type=str, default='configuration.txt', help='name of config file')
    parser.add_argument('-year1', type=int, default=1850, help='First year for processing')
    parser.add_argument('-year2', type=int, default=1850, help='Final year for processing')
    parser.add_argument('-month1', type=int, default=1, help='First month for processing')
    parser.add_argument('-month2', type=int, default=1, help='Final month for processing')
    parser.add_argument('-test', action='store_true', help='run test suite')
    args = parser.parse_args() 

    inputfile = args.config
    year1 = args.year1
    year2 = args.year2
    month1 = args.month1
    month2 = args.month2
    Test = args.test 

    print 'Input file is ', inputfile
    print 'Running from ', month1, year1, ' to ', month2, year2
    print ''

    config = ConfigParser.ConfigParser()    
    config.read(inputfile)

    sst_climatology_file  = '/project/mds/HADISST2/OIv2_clim_MDS_6190_0.25x0.25xdaily_365.nc'

    icoads_dir = config.get('Directories', 'ICOADS_dir')
    out_dir = config.get('Directories', 'out_dir')
    bad_id_file = config.get('Files', 'IDs_to_exclude')
    version = config.get('Icoads', 'icoads_version')

    print 'ICOADS directory =', icoads_dir
    print 'ICOADS version =', version
    print 'List of bad IDs =', bad_id_file 
    print ''

    ids_to_exclude = process_bad_id_file(bad_id_file)

#read in climatology files
    sst_pentad_stdev = clim.Climatology.from_filename(config.get('Climatologies', 'Old_SST_stdev_climatology'), 'sst')

    sst_stdev_1 = clim.Climatology.from_filename(config.get('Climatologies', 'SST_buddy_one_box_to_buddy_avg'), 'sst')
    sst_stdev_2 = clim.Climatology.from_filename(config.get('Climatologies', 'SST_buddy_one_ob_to_box_avg'), 'sst')
    sst_stdev_3 = clim.Climatology.from_filename(config.get('Climatologies', 'SST_buddy_avg_sampling'), 'sst')

    with open(config.get('Files','parameter_file'), 'r') as f:
        parameters = json.load(f)

    climlib = ex.ClimatologyLibrary()
    climlib.add_field('SST', 'mean', clim.Climatology.from_filename(sst_climatology_file, 'temperature'))

    for year, month in qc.year_month_gen(year1, month1, year2, month2):

        print year, month

        last_year, last_month = qc.last_month_was(year, month)
        next_year, next_month = qc.next_month_is(year, month)

        reps = ex.Deck()
        count = 0
        count2 = 0

        for readyear, readmonth in qc.year_month_gen(last_year, 
                                                     last_month, 
                                                     next_year, 
                                                     next_month):

            print readyear, readmonth
            syr = str(readyear)
            smn = "%02d" % (readmonth)

            filename = icoads_filename(icoads_dir, readyear, 
                                       readmonth, version)

            try:
                icoads_file = gzip.open(filename, "r")
            except IOError:
                print "no ICOADS file ",filename," for ", readyear, readmonth
                continue

            rec = IMMA()

            for line in icoads_file:

                try:
                    rec.readstr(line)
                    readob = True
                except:
                    readob = False
                    print "Rejected ob", line
                    
#if this is not on the exclusion list, readable and not a buoy in the NRT runs
                if (not(rec.data['ID'] in ids_to_exclude) and 
                    readob and
                    rec.data['YR'] == readyear and
                    rec.data['MO'] == readmonth):

                    rep = ex.MarineReportQC(rec)
                    del rec
                    rep_clim = climlib.get_field('SST', 'mean').get_value(rep.lat(), rep.lon(), rep.getvar('MO'), rep.getvar('DY')) 
                    rep.add_climate_variable('SST', rep_clim)
                    rep.perform_base_sst_qc(parameters)
                    reps.append(rep)
                    count += 1
                rec = IMMA()
            icoads_file.close()

        print "Read ", count, " ICOADS records"

#filter the obs into passes and fails of basic positional QC        
        filt = ex.QC_filter()
        filt.add_qc_filter('POS', 'date',   0)
        filt.add_qc_filter('POS', 'time',   0)
        filt.add_qc_filter('POS', 'pos',    0)
        filt.add_qc_filter('POS', 'blklst', 0)
         
        reps.add_filter(filt)

#track check the passes one ship at a time
        count_ships = 0
        for one_ship in reps.get_one_platform_at_a_time():

            one_ship.track_check(parameters['track_check'])
            one_ship.find_repeated_values(parameters['find_repeated_values'], intype='SST')
            count_ships += 1

        print "Track checked ", count_ships, " ships"

#SST buddy check
        filt = ex.QC_filter()
        filt.add_qc_filter('POS', 'is780',  0)
        filt.add_qc_filter('POS', 'date',   0)
        filt.add_qc_filter('POS', 'time',   0)
        filt.add_qc_filter('POS', 'pos',    0)
        filt.add_qc_filter('POS', 'blklst', 0)
        filt.add_qc_filter('POS', 'trk',    0)
        filt.add_qc_filter('SST', 'noval',  0)
        filt.add_qc_filter('SST', 'freez',  0)
        filt.add_qc_filter('SST', 'clim',   0)
        filt.add_qc_filter('SST', 'nonorm', 0)

        reps.add_filter(filt)

        reps.bayesian_buddy_check('SST', sst_stdev_1, sst_stdev_2, sst_stdev_3, parameters)
        reps.mds_buddy_check('SST', sst_pentad_stdev, parameters['mds_buddy_check'])

        varnames_to_print = {'SST':['bud', 'clim', 'nonorm', 'freez', 'noval', 'nbud', 'bbud', 'rep', 'spike', 'hardlimit']}
        
        reps.write_qc('hires_'+parameters['runid'], out_dir, year, month, varnames_to_print)

        del reps

if __name__ == '__main__':
    
    main(sys.argv[1:])
