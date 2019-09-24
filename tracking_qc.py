import csv
import qc
import numpy as np
import Extended_IMMA as ex
import BackgroundField as bf
import argparse
import ConfigParser
import json
import sys
import os

class EasyImma:
    """
    This is a quick and dirty class to mimic the IMMA data structure for easy reading
    of the CSV files
    """

    def __init__(self, adict):
        self.data = {}
        for key in adict:
            if adict[key] == '\N':
                adict[key] = None  # np.nan
            self.data[key] = adict[key]
        if 'PT' not in adict:
            self.data['PT'] = 7


def safe_make_tracking_dir(out_dir, year, month):
    """
    Make a directory for QC outcomes from the tracking QC for chunks of data reporting their last ob in this year
    and month

    :param out_dir: directory to use as the base directory for output
    :param year: year for directory name
    :param month: month for directory name
    :type out_dir: string
    :type year: integer
    :type month: integer
    :return: None
    """
    syr = str(year)
    smn = "{:02}".format(month)

    return bf.safe_make_dir_generic(out_dir, ['TrackingQC', syr, smn])


def safe_make_edge_dir(out_dir, year, month, edge, runmonthid):
    """
    Make a directory for the edge cases

    :param out_dir: directory to use as the base directory for output
    :param year: end year for chunk
    :param month: end month for chunk
    :param edge: type of edge case, should be either "start_edge_case" or "end_edge_case"
    :param runmonthid: a tag that identifies this overall run of the QC, should be of form YYYYMM-YYYYMM
    :type out_dir: string
    :type year: integer
    :type month: integer
    :type edge: string
    :type runmonthid: string 
    :return: None
    """
    d3 = safe_make_tracking_dir(out_dir, year, month)

    return bf.safe_make_dir_generic(d3, [edge + '_' + runmonthid])


def main(argv):
    """
    Calls the tracking qc checks for a specified drifting buoy

    Invoked as::

      python tracking_qc.py -config configuration.txt -id BUOYID -yr1 YEAR -mn1 MONTH -yr2 YEAR2 -mn2 MONTH2
      -edge EDGE -runmonthid RUNID

    Inputs

    -config
      specifies the location of the configuration file.

    -id
      ID of the buoy to which tracking QC will be applied

    -yr1
      year of the first month to QC

    -mn1
      month of the first month to QC

    -yr2
      year of the last month to QC

    -mn2
      month of the last month to QC

    -edge
      specific type of edge case, one of: new, regular, start_edge_case, end_edge_case

    -runmonthid
      used to label special directories for start and end edge cases. This is of the form YYYYMM-YYYYMM

    This quality controls drifter data for the chosen ID (which will be end-padded with spaces) over the
    specified time range. The time range should specify a single complete drifter record. The location of the 
    input data and the location of the qc-parameters file are specified in the configuration file. The qc-parameters 
    file specifies the input parameters used by the various tracking checks. Input data are from the marine QC system. 
    These are in 'per-ID per-month' csv format with observation variables, basic QC flags and SST QC flags stored in 
    separate files and linkable via observation UID. 

    A drifting buoy record is first assembled from the input data files and stored as a :class:`.Voyage` of 
    :class:`.MarineReport` s. This record is then passed to the various tracking QC checks. Some observations that
    fail basic or SST QC are not passed to the tracking QC checks and will not receive tracking QC flags. 
    Which observations are filtered out is dependent on tracking QC check.

    Output is written to a file in the track_out_dir specified in the configuration file. Where it is written depends on the
    EDGE flag (EDGE can be 'new', 'regular', 'start_edge_case' or 'end_edge_case'). The RUNID is intended to label
    the directories to which edge cases are sent. It should be of the form YYYMM-YYYMM specifying the start and end
    dates for which the overall QC was run.

    UserWarning is raised for problems with the input files.
    AssertionError is raised if inputs (parameters or MarineReport data) to a QC check are invalid
    """

    parser = argparse.ArgumentParser(description='Marine QC system, main program')
    parser.add_argument('-config', type=str, default='configuration.txt', help='name of config file')
    parser.add_argument('-id', type=str, help='ID to read in and process')
    parser.add_argument('-yr1', type=int, help='First year of data for drifting buoy')
    parser.add_argument('-mn1', type=int, help='First month of data for drifting buoy')
    parser.add_argument('-yr2', type=int, help='Last year of data for drifting buoy')
    parser.add_argument('-mn2', type=int, help='Last month of data for drifting buoy')
    parser.add_argument('-edge', nargs='+', help='list of edge case descriptors')
    parser.add_argument('-runmonthid', type=str, default='',
                        help='string for tagging directories should be of form YYYYMM-YYYYMM')
    args = parser.parse_args()

    edge = args.edge
    runmonthid = args.runmonthid

    oldqc = False # this can be used to switch in the old versions of the aground and speed checks

    target_id = args.id
    while len(target_id) < 9:
        target_id += ' '

    print('Running track QC for ID {}'.format(target_id))
    print('')
    print("Type of case: {}".format(edge[0]))
    print("Specific run id from wrapper script: {}".format(runmonthid))

    config = ConfigParser.ConfigParser()
    config.read(args.config)
    out_dir = config.get('Directories', 'out_dir')
    track_out_dir = config.get('Directories', 'track_out_dir')

    print("{}".format(out_dir))

    with open(config.get('Files', 'parameter_file'), 'r') as f:
        parameters = json.load(f)

    rep_list = []  # this will store input data as MarineReports

    count = 0
    for year, month in qc.year_month_gen(args.yr1, args.mn1, args.yr2, args.mn2):

        sy = str(year)
        sm = "{:02}".format(month)

        # input data files
        filename = "{0}/{1}/{2}/Variables_{1}{2}_{3}_{4}.csv".format(out_dir, sy, sm, target_id, parameters['runid'])
        posqc_filename = "{0}/{1}/{2}/POS_qc_{1}{2}_{3}_{4}.csv".format(out_dir, sy, sm, target_id, parameters['runid'])
        sstqc_filename = "{0}/{1}/{2}/SST_qc_{1}{2}_{3}_{4}.csv".format(out_dir, sy, sm, target_id, parameters['runid'])

        # check if any data exists for this month before continuing
        if not (os.path.isfile(filename) or
                os.path.isfile(posqc_filename) or
                os.path.isfile(sstqc_filename)):
            continue

        print('reading data for: {}/{}'.format(sy, sm))
        # check all files exist, have data and have same amount of data before proceeding
        file_fail = False
        filelines = []
        for infile in [filename, posqc_filename, sstqc_filename]:
            try:
                with open(infile, 'r') as file:
                    linecount = 0
                    for line in file:
                        linecount += 1
                    filelines.append(linecount)
                    if linecount == 0:
                        message = 'empty file: ' + infile
                        file_fail = True
                    if linecount == 1:
                        print('only header in {}'.format(infile))
            except IOError:
                message = 'could not open ' + infile
                file_fail = True
        if not all(x == filelines[0] for x in filelines):
            message = 'file lengths do not match'
            file_fail = True
        if file_fail:
            raise UserWarning('problem with files for {}/{}: '.format(sy, sm), message)

        # read in ID data
        try:
            with open(filename, 'r') as csvfile:
                # get the headers from the CSV file and sort them out:
                # strip trailing carriage return, split by commas, fix duplicates
                headers = csvfile.readline()
                headers = headers[:-1]
                headers = headers.split(',')
                headers[11] = 'AT_anom'  # THIS IS AN AWFUL BODGE, HEADERS SHOULD BE UNIQUE GRRRR
                headers[13] = 'SST_anom'  # THIS IS AN AWFUL BODGE, HEADERS SHOULD BE UNIQUE GRRRR

                # now read the rest of the CSV file using the headers as a dictionary.
                # Need to add OSTIA information as "ext" information in the rep
                reader = csv.DictReader(csvfile, fieldnames=headers)
                nrep = 0
                for line in reader:
                    rep = ex.MarineReportQC(EasyImma(line))
                    # variables not in the Extended_IMMA.py VARLIST are not added by the above step,
                    # so OSTIA, ICE and BGVAR variables now need adding manually
                    rep.setext('OSTIA', None if line['OSTIA'] is None else float(line['OSTIA']))
                    rep.setext('ICE', None if line['ICE'] is None else float(line['ICE']))
                    rep.setext('BGVAR', None if line['BGVAR'] is None else float(line['BGVAR']))
                    rep_list.append(rep)
                    nrep += 1
        except Exception as error:
            print("Something went wrong populating report list")
            raise

        # now read in basic qc data
        try:
            with open(posqc_filename, 'r') as csvfile:
                # get the headers from the CSV file and sort them out:
                # strip trailing carriage return, split by commas, fix duplicates
                headers = csvfile.readline()
                headers = headers[:-1]
                headers = headers.split(',')

                # now read the rest of the CSV file using the headers as a dictionary.
                reader = csv.DictReader(csvfile, fieldnames=headers)
                indx = count
                for line in reader:
                    for key in line:
                        if key == 'UID':
                            uid = rep_list[indx].getvar('UID')
                            if line[key].strip() != uid.strip():
                                raise UserWarning("UIDs don't match: {0}-{1}".format(line[key], uid))
                        else:
                            rep_list[indx].set_qc('POS', key, int(line[key]))
                    indx += 1
        except Exception as error:
            print("Something went wrong adding basic qc to report_list")
            raise

        # now read in sst qc data
        try:
            with open(sstqc_filename, 'r') as csvfile:
                # get the headers from the CSV file and sort them out:
                # strip trailing carriage return, split by commas, fix duplicates
                headers = csvfile.readline()
                headers = headers[:-1]
                headers = headers.split(',')

                # now read the rest of the CSV file using the headers as a dictionary.
                reader = csv.DictReader(csvfile, fieldnames=headers)
                indx = count
                for line in reader:
                    for key in line:
                        if key == 'UID':
                            uid = rep_list[indx].getvar('UID')
                            if line[key].strip() != uid.strip():
                                raise UserWarning("UIDs don't match: {0}-{1}".format(line[key], uid))
                        else:
                            rep_list[indx].set_qc('SST', key, int(line[key]))
                    indx += 1
        except Exception as error:
            print("Something went wrong adding sst qc to report_list")
            raise

        count += nrep

    if len(rep_list) == 0:
        raise UserWarning('no data for buoy ' + target_id)
    print("")
    print("read in {} reports from the buoy {}".format(len(rep_list), target_id))

    # now perform various tracking qc checks
    # note that any obs filtered out ahead of track qc won't receive qc flags
    # get_qc(trackflag) will return 9 for these obs.

    # ---aground QC---

    # pre-filter obs
    filt = ex.QC_filter()
    filt.add_qc_filter('POS', 'isbuoy', 1)  # should already be applied, but just in case
    filt.add_qc_filter('POS', 'date', 0)
    filt.add_qc_filter('POS', 'time', 0)
    filt.add_qc_filter('POS', 'pos', 0)
    filt.add_qc_filter('POS', 'blklst', 0)  # includes rejection of (lon,lat)=(0,0)
    v_filt = ex.Voyage()
    for rep in rep_list:
        if filt.test_report(rep) == 0:
            v_filt.add_report(rep)
    v_filt.sort()  # sort in time
    print("passing {} to aground check".format(len(v_filt)))
    if oldqc:
        v_filt.buoy_aground_check(parameters['buoy_aground_check'],
                                  False)  # raises AssertionError if check inputs are invalid
    else:
        v_filt.new_buoy_aground_check(parameters['new_buoy_aground_check'],
                                      False)  # raises AssertionError if check inputs are invalid

    # ---picked up QC---

    filt = ex.QC_filter()
    filt.add_qc_filter('POS', 'isbuoy', 1)  # should already be applied, but just in case
    filt.add_qc_filter('POS', 'date', 0)
    filt.add_qc_filter('POS', 'time', 0)
    filt.add_qc_filter('POS', 'pos', 0)
    filt.add_qc_filter('POS', 'blklst', 0)  # includes rejection of (lon,lat)=(0,0)
    if oldqc:
        filt.add_qc_filter('POS', 'iquam_track', 0)  # NOTE only use this for original buoy speed check
    v_filt = ex.Voyage()
    for rep in rep_list:
        if filt.test_report(rep) == 0:
            v_filt.add_report(rep)
    v_filt.sort()  # sort in time
    print("passing {} to picked-up check".format(len(v_filt)))
    if oldqc:
        v_filt.buoy_speed_check(parameters['buoy_speed_check'],
                                False)  # raises AssertionError if check inputs are invalid
    else:
        v_filt.new_buoy_speed_check(parameters['IQUAM_track_check'], parameters['new_buoy_speed_check'],
                                    False)  # raises AssertionError if check inputs are invalid

    # ---sst tail QC---

    filt = ex.QC_filter()
    filt.add_qc_filter('POS', 'isbuoy', 1)  # should already be applied, but just in case
    filt.add_qc_filter('POS', 'date', 0)
    filt.add_qc_filter('POS', 'time', 0)
    filt.add_qc_filter('POS', 'pos', 0)
    filt.add_qc_filter('POS', 'blklst', 0)  # includes rejection of (lon,lat)=(0,0)
    filt.add_qc_filter('SST', 'clim', 0)
    filt.add_qc_filter('SST', 'nonorm', 0)
    filt.add_qc_filter('SST', 'freez', 0)
    filt.add_qc_filter('SST', 'noval', 0)
    filt.add_qc_filter('SST', 'rep', 0)  # flags repeated value obs where these are >70% of record (set in parameters)
    filt.add_qc_filter('SST', 'hardlimit', 0)  # limits are -5.0 and 45.0 for SST set in parameters
    filt.add_qc_filter('POS', 'drf_agr', 0)  # remove obs failing preceding track checks
    filt.add_qc_filter('POS', 'drf_spd', 0)  # remove obs failing preceding track checks
    v_filt = ex.Voyage()
    for rep in rep_list:
        if filt.test_report(rep) == 0 and rep.get_qc('SST', 'bbud') < 4:
            v_filt.add_report(rep)
    v_filt.sort()  # sort in time
    print("passing {} to tail check".format(len(v_filt)))
    v_filt.buoy_tail_check(parameters['buoy_tail_check'], False)  # raises AssertionError if check inputs are invalid

    # ---sst biased or noisy buoy QC---

    filt = ex.QC_filter()
    filt.add_qc_filter('POS', 'isbuoy', 1)  # should already be applied, but just in case
    filt.add_qc_filter('POS', 'date', 0)
    filt.add_qc_filter('POS', 'time', 0)
    filt.add_qc_filter('POS', 'pos', 0)
    filt.add_qc_filter('POS', 'blklst', 0)  # includes rejection of (lon,lat)=(0,0)
    filt.add_qc_filter('SST', 'clim', 0)
    filt.add_qc_filter('SST', 'nonorm', 0)
    filt.add_qc_filter('SST', 'freez', 0)
    filt.add_qc_filter('SST', 'noval', 0)
    filt.add_qc_filter('SST', 'rep', 0)  # flags repeated value obs where these are >70% of record (set in parameters)
    filt.add_qc_filter('SST', 'hardlimit', 0)  # limits are -5.0 and 45.0 for SST set in parameters
    filt.add_qc_filter('POS', 'drf_agr', 0)  # remove obs failing preceding track checks
    filt.add_qc_filter('POS', 'drf_spd', 0)  # remove obs failing preceding track checks
    filt.add_qc_filter('SST', 'drf_tail1', 0)  # remove obs failing preceding track checks
    filt.add_qc_filter('SST', 'drf_tail2', 0)  # remove obs failing preceding track checks
    v_filt = ex.Voyage()
    for rep in rep_list:
        if filt.test_report(rep) == 0 and rep.get_qc('SST', 'bbud') < 4:
            v_filt.add_report(rep)
    v_filt.sort()  # sort in time
    print("passing {} to biased-noisy check".format(len(v_filt)))
    v_filt.buoy_bias_noise_check(parameters['buoy_bias_noise_check'],
                                 False)  # raises AssertionError if check inputs are invalid

    # return voyage with track QC flags
    voy = ex.Voyage()
    for rep in rep_list:
        voy.add_report(rep)
    voy.sort()  # sort in time

    # write out the QC outcomes for this chunk for this ID args.yr1,args.mn1,args.yr2,args.mn2)
    # stored in directory corresponding to last month in the chunk
    if 'new' in edge or 'regular' in edge:
        extdir = safe_make_tracking_dir(track_out_dir, args.yr2, args.mn2)
        if oldqc:
            voy.write_tracking_output(parameters['runid']+'oldqc', extdir, args.yr2, args.mn2)
        else:
            voy.write_tracking_output(parameters['runid'], extdir, args.yr2, args.mn2)

    if 'start_edge_case' in edge:
        extdir = safe_make_edge_dir(track_out_dir, args.yr2, args.mn2, 'start_edge_case', runmonthid)
        if oldqc:
            voy.write_tracking_output(parameters['runid']+'oldqc', extdir, args.yr2, args.mn2)
        else:
            voy.write_tracking_output(parameters['runid'], extdir, args.yr2, args.mn2)

    if 'end_edge_case' in edge:
        extdir = safe_make_edge_dir(track_out_dir, args.yr2, args.mn2, 'end_edge_case', runmonthid)
        if oldqc:
            voy.write_tracking_output(parameters['runid']+'oldqc', extdir, args.yr2, args.mn2)
        else:
            voy.write_tracking_output(parameters['runid'], extdir, args.yr2, args.mn2)


#    return voy

if __name__ == '__main__':
    main(sys.argv[1:])
