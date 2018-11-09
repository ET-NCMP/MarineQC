#!/usr/local/sci/bin/python2.7
'''
tracking_qc.py invoked by typing::

  python2.7 tracking_qc.py -config configuration.txt -id "SHIPNAME" 

This quality controls data for the chosen ID (which will be end-padded with spaces). The location 
of the data and the locations of the climatology files are all to be specified in the configuration files.
'''

import csv
import qc
import numpy as np
import Extended_IMMA as ex
import argparse
import ConfigParser
import json
import sys

class easy_imma():
    '''
    This is a quick and dirty class to mimic the IMMA data structure for easy reading
    of the CSV files
    '''
    def __init__(self, dict):
        self.data = {}
        for key in dict:
            if dict[key] == '\N': dict[key] = np.nan
            self.data[key] = dict[key]

def main(argv):
    
    '''
    tracking_qc.py invoked by typing::

    python2.7 tracking_qc.py -config configuration.txt -id "SHIPNAME" 

    This quality controls data for the chosen ID (which will be end-padded with spaces). The location 
    of the data and the locations of the climatology files are all to be specified in the configuration files.
    '''
    
    print '########################'
    print 'Running tracking_qc'
    print '########################'

    parser = argparse.ArgumentParser(description='Marine QC system, main program')
    parser.add_argument('-config', type=str, default='configuration.txt', help='name of config file')
    parser.add_argument('-id', type=str, help='ID to read in and process')
    args = parser.parse_args() 

    id = args.id
    while len(id) < 9: id += ' '

    print "running on ICOADS, this is not a test!"

    print 'Input file is ', args.config
    print 'Running for ID ',id
    print ''
    
    config = ConfigParser.ConfigParser()    
    config.read(args.config)
    icoads_dir = config.get('Directories', 'ICOADS_dir')
    out_dir = config.get('Directories', 'out_dir')
    
    with open(config.get('Files','parameter_file'), 'r') as f:
        parameters = json.load(f)
        
    print 'ICOADS directory =', icoads_dir
    print 'Output to',out_dir
    print ''

    v = ex.Voyage()

    for year, month in qc.year_month_gen(1985, 1, 2014, 12):
        
        sy = str(year)
        sm = "%02d" % (month)  

        filename = out_dir+'/'+sy+'/'+sm+'/Variables_'+sy+sm+'_'+id+'_standard.csv'
        print(filename)
#try top open file containing ID data
        try:
            with open(filename,'r') as csvfile:

#get the headers from the CSV file and sort them out: strip trailing carriage return, split by commas, fix duplicates 
                headers = csvfile.readline()
                headers = headers[:-1]
                headers = headers.split(',')
                headers[11] = 'AT_anom'  #THIS IS AN AWFUL BODGE, HEADERS SHOULD BE UNIQUE GRRRR
                headers[13] = 'SST_anom' #THIS IS AN AWFUL BODGE, HEADERS SHOULD BE UNIQUE GRRRR
    
#now read the rest of the CSV file using the headers as a dictionary. Need to add OSTIA information as "ext" information in the rep
                reader = csv.DictReader(csvfile, fieldnames=headers)
                for line in reader:
                    rep = ex.MarineReportQC(easy_imma(line))
                    rep.setext('OSTIA', line['OSTIA'])
                    rep.setext('ICE', line['ICE'])
                    rep.setext('BGVAR', line['BGVAR'])
    
                    v.add_report(rep)
#Now do soemthing if it goes wrong
        except:
            print("Something went wrong. Does the file "+filename+" exist?")

    print ""
    print "read in "+str(len(v))+" reports from the good ship "+id

#all the data now read in do something with it. This isn't very exciting, but we can...print out all the obs
    for rep in v.rep_feed():
        print rep.getvar('ID'),rep.getvar('YR'), rep.getvar('MO'), rep.getvar('LAT'), rep.getvar('LON')

#Or, we can run a positional track check on the combined track...
    v.track_check(parameters['track_check'])
#and print out the results
    for rep in v.rep_feed():
        print rep.get_qc('POS', 'trk')



if __name__ == '__main__':
    
    main(sys.argv[1:])
