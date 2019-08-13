import time
import argparse
import ConfigParser
import sys
import os
import subprocess
import qc
import YMCounter as ym
import json


def safe_dir(out_dir, year, month):
    """
    Make a directory for this year and month as subdirectories of out_dir

    :param out_dir: base directory in which new directories will be created
    :param year: year for subdirectory
    :param month: month for subdirectory
    :return: None
    """
    syr = str(year)
    smn = "{:02}".format(month)
    d2 = out_dir+'/'+syr+'/'+smn+'/'
    return d2


def checkload(uname):
    """
    Check how many submitted jobs the user uname has in the queue

    :param uname: username of user running the script
    :return: number of submitted jobs
    """
    stream = subprocess.check_output(['squeue', '-l'])
    stream = ''.join(stream)
    count = stream.count(uname)
    return count


def safemake(folder):
    """
    Little script to check if a folder exists and if not, to make it

    :param folder: path of folder to create
    :return: None
    """

    if not os.path.exists(folder):
        os.mkdir(folder)


def write_submission(config, targetid, yr1, mn1, yr2, mn2, edge, runmonthid, outdir, runid):
    """
    Builds a command to run like this:
    python tracking_qc.py -id 51514 -yr1 2004 -mn1 5 -yr2 2006 -mn2 1 -edge start_edge_case -runmonthid 198501-201412
    and submits it to the scheduler to run. It will submit a maximum of 250 jobs. If there are more in the queue
    then it will wait and check again.

    :param config: location of configuration file
    :param targetid: the ID of the buoy to be checked
    :param yr1: the start year of the chunk of data to be QCd
    :param mn1: the start month of the chunk of data to be QCd
    :param yr2: the end year of the chunk of data to be QCd
    :param mn2:  the end month of the chunk of data to be QCd
    :param edge: specifies what kind of case this is
    :param runmonthid: a runmonthid which will be used to label directories for start and end edge cases
    :param outdir: the base directory used to write out log files and store submitted jobs
    :param runid: the name of the run as specified in the parameter file
    :return:
    """

    codedir = '/net/home/h04/hadjj/PyWorkspace/Marine_QC/'

    fname = 'Tracking_job_{}_{}{:02}_{}{:02}_{}_{}'.format(targetid.replace(" ", ""),
                                                           yr1, mn1, yr2, mn2, runmonthid, runid)

    options = {'id': targetid, 'config': config,
               'yr1': yr1, 'mn1': mn1, 'yr2': yr2, 'mn2': mn2,
               'edge': " ".join(edge), 'runmonthid': runmonthid}

    command = 'python {}tracking_qc.py'.format(codedir)
    for op in options:
        command = command + " -{} {}".format(op, options[op])

    logdir = outdir + '/TrackingQC/logs'
    jobdir = outdir + '/TrackingQC/jobs'

    safemake(outdir + '/TrackingQC')
    safemake(logdir)
    safemake(jobdir)

    outfile = open(jobdir+'/'+fname, 'w')

    outfile.write("#!/bin/bash -l\n")
    outfile.write("#SBATCH --mem=8000\n")
    outfile.write("#SBATCH --ntasks=1\n")
    outfile.write("#SBATCH --output={}/SPICE_trackqc_errout{}{:02}{}_{}\n".format(logdir, yr2, mn2,
                                                                                  targetid.replace(" ", ""), runid))
    outfile.write("#SBATCH --time=30\n")
    outfile.write("\n")
    outfile.write("module load scitools/default_legacy-current\n")
    outfile.write(command + " > {}/SPICE_trackqc_genout{}{:02}{}_{}\n".format(logdir, yr2, mn2,
                                                                              targetid.replace(" ", ""), runid))

    outfile.close()

    os.system("sbatch "+jobdir+"/"+fname)

    count = checkload('hadjj')
    while count > 250:
        print("Reached max jobs (250), waiting 20 seconds")
        time.sleep(20)
        count = checkload('hadjj')


def main(argv):
    """
    Tracking_QC_wrapper.py

    script to control the running of the tracking QC. Reads in files containing list of IDs for
    each month and decides when to quality control the observations. Call as, for example

    python Tracking_QC_wrapper.py -config configuration.txt -gap 3 -y1 1985 -y2 2005 -m1 1 -m2 12 -edge new

    -confg specifies the location of the configuration file
    -gap specifies gap in months without obs after which a platform is deemed to have expired and tracking QC can be run
    -y1 -m1 start year and month
    -y2 -m2 end year and month
    -edge specifies how different cases should be treated. 'all' will run QC for all chunks separated by "gap" months of
    data; 'standard' will run for all chunks except for those that start or end fewer than "gap" months from the start
    or end of the series; 'new' will run only those chunks that have a gap of exactly "gap" months from the end of the
    series.

    The three "edge" cases allow for running in different modes. In principle, 'standard' will QC everything that will
    not change from the addition of data to the start or end of the series. It is intended for running all the
    historical QC in preparation for monthly updates. The flag 'new' can be used for real time updates to only QC those
    IDs that have not been eligible for QC in earlier months and have an appropriate gap at the end of the series. The
    flag 'all' will QC everything, including chunks at the start and end of the series which may change with extra data
    appended to either end of the series.

    Note that adding extra data in the middle of the series is liable to change all QC outcomes regardless of whether QC
    was run in 'all', 'standard' or 'new' configurations.
    """

    parser = argparse.ArgumentParser(description='Marine QC system, main program')
    parser.add_argument('-config', type=str, default='configuration.txt', help='name of config file')
    parser.add_argument('-gap', type=int, default=3, help='gap of -gap months needed to trigger QC of ID')
    parser.add_argument('-y1', type=int, default=1985, help='first year to analyse')
    parser.add_argument('-y2', type=int, default=2019, help='last year to analyse')
    parser.add_argument('-m1', type=int, default=1, help='first month to analyse in first year')
    parser.add_argument('-m2', type=int, default=12, help='last month to analyse in last year')
    parser.add_argument('-edge', type=str, default='standard', help='How to deal with edge cases')

    args = parser.parse_args()

    inputfile = args.config
    y1 = args.y1
    y2 = args.y2
    m1 = args.m1
    m2 = args.m2
    gap = args.gap
    edge = args.edge

    runmonthid = "{}{:02}-{}{:02}".format(y1, m1, y2, m2)

    if edge not in ['standard', 'all', 'new', 'noend']:
        raise Exception("edge not one of 'standard', 'all', 'new' or 'noend'")

    config = ConfigParser.ConfigParser()
    config.read(inputfile)
    out_dir = config.get('Directories', 'out_dir')

    with open(config.get('Files', 'parameter_file'), 'r') as f:
        parameters = json.load(f)

    # establish full list of IDs to QC
    id_dictionary = {}

    for year, month in qc.year_month_gen(y1, m1, y2, m2):
        # create directory and file names for the ID list
        extdir = safe_dir(out_dir, year, month)
        idfile = open(extdir + '/ID_file.txt', 'r')

        for line in idfile:
            line = line.rstrip("\n")
            columns = line.split(',')
            if columns[0] in id_dictionary:
                id_dictionary[columns[0]].setym(year, month, 1)
            else:
                id_dictionary[columns[0]] = ym.YMCounter(y1, m1, y2, m2)
                id_dictionary[columns[0]].setym(year, month, 1)

        idfile.close()

    for targetid in id_dictionary:

        g = id_dictionary[targetid]
        print(targetid, g.counter)

        for yy1, mm1, yy2, mm2, cl in g.yield_start_and_end_dates(gap):

            if edge == 'all':
                print('Submit', yy1, mm1, yy2, mm2, cl)
                write_submission(inputfile, targetid, yy1, mm1, yy2, mm2, cl,
                                 runmonthid, out_dir, parameters['runid'])

            if edge == 'standard':
                if 'regular' in cl:
                    print('Submit', yy1, mm1, yy2, mm2, cl)
                    write_submission(inputfile, targetid, yy1, mm1, yy2, mm2, cl,
                                     runmonthid, out_dir, parameters['runid'])
                else:
                    print('Ignore', yy1, mm1, yy2, mm2, cl)

            if edge == 'new':
                if 'new' in cl:
                    print('Submit', yy1, mm1, yy2, mm2, cl)
                    write_submission(inputfile, targetid, yy1, mm1, yy2, mm2, cl,
                                     runmonthid, out_dir, parameters['runid'])
                else:
                    print('Ignore', yy1, mm1, yy2, mm2, cl)

            if edge == 'noend':
                if 'regular' in cl or 'start_edge_case' in cl:
                    print('Submit', yy1, mm1, yy2, mm2, cl)
                    write_submission(inputfile, targetid, yy1, mm1, yy2, mm2, cl,
                                     runmonthid, out_dir, parameters['runid'])
                else:
                    print('Ignore', yy1, mm1, yy2, mm2, cl)

        print()


if __name__ == '__main__':
    main(sys.argv[1:])
