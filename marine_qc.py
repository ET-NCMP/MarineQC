#!/usr/local/sci/bin/python2.7
'''
marine_qc.py invoked by typing::

  python2.7 marine_qc.py -config configuration.txt -year1 1850 -year2 1855 -month1 1 -month2 1 [-test]

This quality controls data for the chosen years. The location 
of the data and the locations of the climatology files are 
all to be specified in the configuration files. Benchmarks can 
be run using -test.
'''

import gzip
import csv
from netCDF4 import Dataset
import qc
from IMMA1 import IMMA
from NRT import NRT
import TestIMMA as timma
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

def nrt_filename(nrt_dir, readyear, readmonth):

#    assert readyear > 2016
    
    syr = str(readyear)
    smn = "%02d" % (readmonth) 
    
    return nrt_dir+'/OSMC_'+syr+smn+'.csv.gz'

def icoads_filename(icoads_dir, readyear, readmonth, version):

    assert version in ['2.5','3.0'], "name not 2.5 or 3.0"

    syr = str(readyear)
    smn = "%02d" % (readmonth) 
    
    if version == '2.5':
        filename = icoads_dir+'/R2.5.1.'+syr+'.'+smn+'.gz'
        if ((readyear > 2007) & (readyear < 2015)):
            filename = icoads_dir+'/R2.5.2.'+syr+'.'+smn+'.gz'

    if version == '3.0':
        if readyear <= 2014:
            filename = icoads_dir+'/IMMA1_R3.0.0_'+syr+'-'+smn+'.gz'
        if readyear >= 2015:
            filename = icoads_dir+'/../ICOADS.3.0.1/IMMA1_R3.0.1_'+syr+'-'+smn+'.gz'

    return filename

def main(argv):
    '''
    This program reads in data from ICOADS.3.0.0/ICOADS.3.0.1 and applies quality control processes to it, flagging data as 
    good or bad according to a set of different criteria. Optionally it will replace drifting buoy SST data in ICOADS.3.0.1 
    with drifter data taken from the GDBC portal.

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
    parser.add_argument('-nrt',  action='store_true', help='run on NRT drifters')
    args = parser.parse_args() 

    inputfile = args.config
    year1 = args.year1
    year2 = args.year2
    month1 = args.month1
    month2 = args.month2
    Test = args.test 
    nrt = args.nrt

    if Test: print "running on benchmarks. This is a test."
    else: print "running on ICOADS, this is not a test!"

    print 'Input file is ', inputfile
    print 'Running from ', month1, year1, ' to ', month2, year2
    print ''
    
    config = ConfigParser.ConfigParser()    
    config.read(inputfile)
    icoads_dir = config.get('Directories', 'ICOADS_dir')
    nrt_dir = config.get('Directories', 'nrt_dir')
    bad_id_file = config.get('Files', 'IDs_to_exclude')
    test_dir = config.get('Directories', 'test_dir')
    version = config.get('Icoads', 'icoads_version')

    if nrt:
        print 'NRT directory =',nrt_dir

    print 'ICOADS directory =', icoads_dir
    print 'ICOADS version =', version
    print 'List of bad IDs =', bad_id_file
    print 'Parameter file =', config.get('Files','parameter_file')
    print ''

    ids_to_exclude = process_bad_id_file(bad_id_file)

#read in climatology files
    sst_pentad_stdev = clim.Climatology.from_filename(config.get('Climatologies', 'Old_SST_stdev_climatology'), 'sst')

    sst_stdev_1 = clim.Climatology.from_filename(config.get('Climatologies', 'SST_buddy_one_box_to_buddy_avg'), 'sst')
    sst_stdev_2 = clim.Climatology.from_filename(config.get('Climatologies', 'SST_buddy_one_ob_to_box_avg'), 'sst')
    sst_stdev_3 = clim.Climatology.from_filename(config.get('Climatologies', 'SST_buddy_avg_sampling'), 'sst')

    with open(config.get('Files','parameter_file'), 'r') as f:
        parameters = json.load(f)
    
    print "Reading climatologies from parameter file"
    climlib = ex.ClimatologyLibrary()
    for entry in parameters['climatologies']:
        print entry[0],entry[1]
        climlib.add_field(entry[0], entry[1], clim.Climatology.from_filename(entry[2], entry[3]))

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

            if Test:
                filename = test_dir+'test_data_'+syr+smn
                try:
                    f = open(filename, "r")
                    icoads_file = csv.reader(f)
                except IOError:
                    print "no test file for ", readyear, readmonth
                    continue                    
            else:
                filename = icoads_filename(icoads_dir, readyear, 
                                           readmonth, version)
                try:
                    icoads_file = gzip.open(filename, "r")
                except IOError:
                    print "no ICOADS file for ", readyear, readmonth
                    continue

            if Test:
                rec = timma.IMMA()
            else:   
                rec = IMMA()

            for line in icoads_file:

                try:
                    rec.readstr(line)
                    readob = True
                except:
                    readob = False
                    print "Rejected ob", line

                if (not(rec.data['ID'] in ids_to_exclude) and 
                    readob and 
                    not(nrt and rec.data['PT'] == 7) and
                    rec.data['YR'] == readyear and
                    rec.data['MO'] == readmonth):

                    rep = ex.MarineReportQC(rec)
                    del rec

                    rep.setvar('AT2', rep.getvar('AT'))

                    for varname in ['SST','AT']:
                        rep_clim = climlib.get_field(varname, 'mean').get_value_mds_style(rep.lat(), rep.lon(), rep.getvar('MO'), rep.getvar('DY'))
                        rep.add_climate_variable(varname, rep_clim)

                    for varname in ['SLP', 'SHU', 'CRH', 'CWB', 'DPD']:
                        rep_clim = climlib.get_field(varname, 'mean').get_value(rep.lat(), rep.lon(), rep.getvar('MO'), rep.getvar('DY'))
                        rep.add_climate_variable(varname, rep_clim)   

                    for varname in ['DPT', 'AT2']:
                        rep_clim  = climlib.get_field(varname, 'mean').get_value(rep.lat(), rep.lon(), rep.getvar('MO'), rep.getvar('DY'))
                        rep_stdev = climlib.get_field(varname, 'stdev').get_value(rep.lat(), rep.lon(), rep.getvar('MO'), rep.getvar('DY'))
                        rep.add_climate_variable(varname, rep_clim, rep_stdev)   

                    rep.calculate_humidity_variables(['SHU', 'VAP', 'CRH', 'CWB', 'DPD'])

                    rep.perform_base_qc(parameters)

                    reps.append(rep)
                    count += 1

                if Test:
                    rec = timma.IMMA()
                else:   
                    rec = IMMA()

            if Test:
                f.close()
            else:
                icoads_file.close()

#next read the NRT if needed
            if nrt:                                     
                filename = nrt_filename(nrt_dir, readyear, readmonth)
                try:
                    icoads_file = gzip.open(filename, "r")
                except IOError:
                    print "no NRT file for ", readyear, readmonth,filename
                    continue
                rec = NRT()
                for line in icoads_file:
                    try:
                        rec.readstr(line)
                        readob = True
                    except:
                        readob = False
                        print "Rejected ob", line
                    if (not(rec.data['ID'] in ids_to_exclude) and readob):
                        rep = ex.MarineReportQC(rec)
                        del rec
                        rep.setvar('AT2', rep.getvar('AT'))
                        rep_clim = climlib.get_field('SST', 'mean').get_value_mds_style(rep.lat(), rep.lon(), rep.getvar('MO'), rep.getvar('DY'))
                        rep.add_climate_variable('SST', rep_clim)
                        rep.perform_base_qc(parameters)
                        reps.append(rep)
                        count2 += 1
                    rec = NRT()
                icoads_file.close()

        print "Read ", count, " ICOADS records and ",count2," NRT records"

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
            one_ship.iquam_track_check(parameters['IQUAM_track_check'])
            one_ship.spike_check(parameters['IQUAM_spike_check'])
            one_ship.find_supersaturated_runs(parameters['supersaturated_runs'])
            one_ship.find_multiple_rounded_values(parameters['multiple_rounded_values'])

            for varname in ['SST', 'AT', 'AT2', 'DPT']:
                one_ship.find_repeated_values(parameters['find_repeated_values'], 
                                              intype=varname)

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

        if not nrt:

    #NMAT buddy check
            filt = ex.QC_filter()
            filt.add_qc_filter('POS', 'isship', 1) #only do ships mat_blacklist
            filt.add_qc_filter('AT',  'mat_blacklist', 0)
            filt.add_qc_filter('POS', 'date',   0)
            filt.add_qc_filter('POS', 'time',   0)
            filt.add_qc_filter('POS', 'pos',    0)
            filt.add_qc_filter('POS', 'blklst', 0)
            filt.add_qc_filter('POS', 'trk',    0)
            filt.add_qc_filter('POS', 'day',    0)
            filt.add_qc_filter('AT',  'noval',  0)
            filt.add_qc_filter('AT',  'clim',   0)
            filt.add_qc_filter('AT',  'nonorm', 0)

            reps.add_filter(filt)

            reps.bayesian_buddy_check('AT', sst_stdev_1, sst_stdev_2, sst_stdev_3, parameters)
            reps.mds_buddy_check('AT', sst_pentad_stdev, parameters['mds_buddy_check'])

    #DPT buddy check
            filt = ex.QC_filter()
            filt.add_qc_filter('DPT', 'hum_blacklist', 0)
            filt.add_qc_filter('POS', 'date',   0)
            filt.add_qc_filter('POS', 'time',   0)
            filt.add_qc_filter('POS', 'pos',    0)
            filt.add_qc_filter('POS', 'blklst', 0)
            filt.add_qc_filter('POS', 'trk',    0)
            filt.add_qc_filter('DPT', 'noval',  0)
            filt.add_qc_filter('DPT', 'clim',   0)
            filt.add_qc_filter('DPT', 'nonorm', 0)

            reps.add_filter(filt)

            reps.mds_buddy_check('DPT', climlib.get_field('DPT', 'stdev'), parameters['mds_buddy_check'])

        if nrt:
            reps.write_output(parameters['runid'], nrt_dir, year, month, Test)
        else:
            reps.write_output(parameters['runid'], icoads_dir, year, month, Test)

        del reps

if __name__ == '__main__':
    
    main(sys.argv[1:])
