import os
import subprocess


def process_string(instring, year, month, day):

    sy = "{:04}".format(year)
    sm = "{:02}".format(month)
    sd = "{:02}".format(day)

    outstring = instring.replace('YYYY', sy)
    outstring = outstring.replace('MMMM', sm)
    outstring = outstring.replace('DDDD', sd)

    return outstring


def make_filename(dirstub, filenamestub, year, month, day):

    dirfill = process_string(dirstub, year, month, day)
    filenamefill = process_string(filenamestub, year, month, day)

    filename = os.path.join(dirfill, filenamefill)

    return filename


def get_background_filename(dirstubs, filenamestubs, year, month, day):

    if year is None or month is None or day is None:
        return None

    scratch = os.environ['SCRATCH']

    originalfilenames = []
    newfilenames = []

    for i, dirstub in enumerate(dirstubs):
        filenamestub = filenamestubs[i]
        originalfilenames.append(make_filename(dirstub, filenamestub, year, month, day))
        newfilenames.append(make_filename(scratch, filenamestub, year, month, day))

# find the first original file that exists in the list
    chosen_orig = None
    chosen_new = None
    for i, fname in enumerate(originalfilenames):
        if chosen_orig is None:
            if os.path.isfile(fname) and os.stat(fname).st_size != 0:
                chosen_orig = fname
                chosen_new = newfilenames[i]
            if os.path.isfile(fname + '.bz2') and os.stat(fname + '.bz2').st_size != 0:
                chosen_orig = fname + '.bz2'
                chosen_new = newfilenames[i]

    if chosen_orig is None:
        return None

    outfile = None

# for bzipped files check to see if unzipped file exists
    if '.bz2' in chosen_orig:
        if os.path.isfile(chosen_new):
            outfile = chosen_new
        else:
            subprocess.call('bunzip2 -c ' + chosen_orig + '.bz2 > ' + chosen_new, shell=True)
            outfile = chosen_new
# if it's not bzipped then leave as is and read in place
    else:
        outfile = chosen_orig

    return outfile
