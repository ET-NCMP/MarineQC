#!/usr/local/sci/bin/python2.7
'''
marine_qc.py invoked by typing::

  python2.7 marine_qc.py -config configuration.txt -year1 1850 -year2 1855 -month1 1 -month2 1 [-tracking] 

This quality controls data for the chosen years. The location 
of the data and the locations of the climatology files are 
all to be specified in the configuration files.
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
import os
import subprocess

def safe_make_dir(out_dir, year, month):
    syr = str(year)
    smn = "%02d" % (month)
    d1 = out_dir+'/'+syr
    d2 = out_dir+'/'+syr+'/'+smn+'/'
    try:
        os.mkdir(d1)
        print("Directory " , d1 ,  " Created ") 
    except OSError:
        print("Directory " , d1 ,  " already exists")
    try:
        os.mkdir(d2)
        print("Directory " , d2 ,  " Created ") 
    except OSError:
        print("Directory " , d2 ,  " already exists")
    return d2

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

def ostia_filename(ostia_dir, year, month, day):
    
    if year is None or month is None or day is None:
        return None
    
    sy = str(year)
    sm = "%02d" % (month) 
    sd = "%02d" % (day) 
#/project/ofrd/ostia/reanalysis/v1.0/
#/project/ofrd/ostia/data/netcdf/
    if year > 2007:
        dir = ostia_dir +'/data/netcdf/'+ sy +'/'+ sm +'/'
        fname = sy+sm+sd+'-UKMO-L4HRfnd-GLOB-v01-fv02-OSTIA.nc'
    else:
        dir = ostia_dir +'/reanalysis/v1.0/'+ sy +'/'+ sm +'/'
        fname = sy+sm+sd+'-UKMO-L4HRfnd-GLOB-v01-fv02-OSTIARAN.nc'

#First check if this thing is already unzipped somewhere
    if (os.path.isfile('/scratch/hadjj/'+fname) and 
        os.stat('/scratch/hadjj/'+fname).st_size != 0):
        print("File already exists"+'/scratch/hadjj/'+fname)
        return '/scratch/hadjj/'+fname

    if os.path.isfile(dir+fname+'.bz2'):
        print("Bunzipping the file"+dir+fname+".bz2")
        subprocess.call('bunzip2 -c '+dir+fname+'.bz2 > /scratch/hadjj/'+fname, shell=True)
        return '/scratch/hadjj/'+fname
    else:
        print("no file to bunzip returning None "+dir+fname+".bz2")
        return None

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
    parser.add_argument('-tracking', action='store_true', help='perform tracking QC')
    args = parser.parse_args() 

    inputfile = args.config
    year1 = args.year1
    year2 = args.year2
    month1 = args.month1
    month2 = args.month2
    Tracking = args.tracking

    print "running on ICOADS, this is not a test!"

    print 'Input file is ', inputfile
    print 'Running from ', month1, year1, ' to ', month2, year2
    print ''
    
    config = ConfigParser.ConfigParser()    
    config.read(inputfile)
    icoads_dir = config.get('Directories', 'ICOADS_dir')
    out_dir = config.get('Directories', 'out_dir')
    bad_id_file = config.get('Files', 'IDs_to_exclude')
    if Tracking: ostia_dir = config.get('Directories', 'ostia_dir')
    version = config.get('Icoads', 'icoads_version')

    print 'ICOADS directory =', icoads_dir
    print 'ICOADS version =', version
    print 'Output to',out_dir
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
        lastday = -99

        for readyear, readmonth in qc.year_month_gen(last_year, last_month, next_year, next_month):

            print readyear, readmonth
            syr = str(readyear)
            smn = "%02d" % (readmonth)

            if Tracking:
                ostia_bg_var = clim.Climatology.from_filename(config.get('Climatologies', qc.season(readmonth)+'_ostia_background'), 'bg_var')

            filename = icoads_filename(icoads_dir, readyear, readmonth, version)
            try:
                icoads_file = gzip.open(filename, "r")
            except IOError:
                print "no ICOADS file for ", readyear, readmonth
                continue

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
                    rec.data['YR'] == readyear and
                    rec.data['MO'] == readmonth):

                    rep = ex.MarineReportQC(rec)
                    del rec

                    rep.setvar('AT2', rep.getvar('AT'))

                    #if day has changed then read in OSTIA field if available and append SST and sea-ice fraction
                    #to the observation metadata
                    if Tracking and readyear >= 1985 and rep.getvar('DY') is not None:
                        if rep.getvar('DY') != lastday:
                            lastday = rep.getvar('DY')
                            y_year, y_month, y_day = qc.yesterday(readyear, readmonth, lastday)
                            ofname = ostia_filename(ostia_dir, y_year, y_month, y_day)
                            climlib.add_field('OSTIA', 'background', clim.Climatology.from_filename(ofname, 'analysed_sst'))
                            climlib.add_field('OSTIA', 'ice', clim.Climatology.from_filename(ofname, 'sea_ice_fraction'))

                        rep_clim = climlib.get_field('OSTIA', 'background').get_value_ostia(rep.lat(), rep.lon())
                        if rep_clim is not None: rep_clim -= 273.15
                        rep.setext('OSTIA', rep_clim)
                        rep.setext('ICE', climlib.get_field('OSTIA', 'ice').get_value_ostia(rep.lat(), rep.lon()))
                        rep.setext('BGVAR', ostia_bg_var.get_value_mds_style(rep.lat(), rep.lon(), rep.getvar('MO'), rep.getvar('DY')))

                    for varname in ['SST','AT']:
                        rep_clim = climlib.get_field(varname, 'mean').get_value_mds_style(rep.lat(), rep.lon(), rep.getvar('MO'), rep.getvar('DY'))
                        rep.add_climate_variable(varname, rep_clim)

                    for varname in ['SLP2', 'SHU', 'CRH', 'CWB', 'DPD']:
                        rep_clim = climlib.get_field(varname, 'mean').get_value(rep.lat(), rep.lon(), rep.getvar('MO'), rep.getvar('DY'))
                        rep.add_climate_variable(varname, rep_clim)   

                    for varname in ['DPT', 'AT2', 'SLP']:
                        rep_clim  = climlib.get_field(varname, 'mean').get_value(rep.lat(), rep.lon(), rep.getvar('MO'), rep.getvar('DY'))
                        rep_stdev = climlib.get_field(varname, 'stdev').get_value(rep.lat(), rep.lon(), rep.getvar('MO'), rep.getvar('DY'))
                        rep.add_climate_variable(varname, rep_clim, rep_stdev)   

                    rep.calculate_humidity_variables(['SHU', 'VAP', 'CRH', 'CWB', 'DPD'])

                    rep.perform_base_qc(parameters)

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
            one_ship.iquam_track_check(parameters['IQUAM_track_check'])
            one_ship.spike_check(parameters['IQUAM_spike_check'])
            one_ship.find_saturated_runs(parameters['saturated_runs'])
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

#DPT buddy check #NB no day check for this one
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

#SLP buddy check
        filt = ex.QC_filter()
        filt.add_qc_filter('POS', 'date',   0)
        filt.add_qc_filter('POS', 'time',   0)
        filt.add_qc_filter('POS', 'pos',    0)
        filt.add_qc_filter('POS', 'blklst', 0)
        filt.add_qc_filter('POS', 'trk',    0)
        filt.add_qc_filter('SLP', 'noval',  0)
        filt.add_qc_filter('SLP', 'clim',   0)
        filt.add_qc_filter('SLP', 'nonorm', 0)

        reps.add_filter(filt)

        reps.mds_buddy_check('SLP', climlib.get_field('SLP', 'stdev'), parameters['slp_buddy_check'])

        extdir = safe_make_dir(out_dir, year, month)
        reps.write_output(parameters['runid'], extdir, year, month)

        if Tracking:
#set QC for output by ID - buoys only and passes base SST QC
            filt = ex.QC_filter()
            filt.add_qc_filter('POS', 'isbuoy', 1)
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

            idfile = open(extdir+'/ID_file.txt','w')
            for one_ship in reps.get_one_platform_at_a_time():
                if len(one_ship) > 0:
                    idfile.write(one_ship.getrep(0).getvar('ID')+'\n')
                    one_ship.write_output(parameters['runid'], extdir, year, month)
            idfile.close()

        del reps

if __name__ == '__main__':
    
    main(sys.argv[1:])
