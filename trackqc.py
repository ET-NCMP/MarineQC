import numpy as np
from spherical_geometry import sphere_distance
from qc import sunangle, dayinyear
import copy
import Extended_IMMA as ex
import math

"""
The trackqc module contains a set of functions for performing the tracking QC
first described in Atkinson et al. [2013]. The general procedures described 
in Atkinson et al. [2013] were later revised and improved for the SST CCI 2 project.
Documentation and IDL code for the revised (and original) procedures can be found 
in the CMA FCM code repository. The code in this module represents a port of the
revised IDL code into the python marine QC suite. New versions of the aground
and speed checks have also been added.

These functions perform tracking QC checks on a :class:`.Voyage` 

References:

Atkinson, C.P., N.A. Rayner, J. Roberts-Jones, R.O. Smith, 2013: 
Assessing the quality of sea surface temperature observations from 
drifting buoys and ships on a platform-by-platform basis (doi:10.1002/jgrc.20257).  

CMA FCM code repository:
http://fcm9/projects/ClimateMonitoringAttribution/browser/Track_QC?order=name

"""


def track_day_test(year, month, day, hour, lat, lon, elevdlim=-2.5):
    """
    Given date, time, lat and lon calculate if the sun elevation is > elevdlim.
    If so return daytime is True
       
    This is the "day" test used by tracking QC to decide whether an SST measurement is night or day. 
    This is important because daytime diurnal heating can affect comparison with an SST background.
    It uses the function sunangle to calculate the elevation of the sun. A default solar_zenith angle 
    of 92.5 degrees (elevation of -2.5 degrees) delimits night from day. 
   
    :param year: Year
    :param month: Month
    :param day: Day
    :param hour: Hour expressed as decimal fraction (e.g. 20.75 = 20:45 pm)
    :param lat: Latitude in degrees
    :param lon: Longitude in degrees
    :param elevdlim: Elevation day/night delimiter in degrees above horizon
    :type year: integer
    :type month: integer
    :type day: integer
    :type hour: float
    :type lat: float
    :type lon: float
    :type elevdlim: float
    :return: True if daytime, else False.
    :rtype: boolean
 
    """
    assert year is not None, 'year is missing'
    assert month is not None, 'month is missing'
    assert day is not None, 'day is missing'
    assert hour is not None, 'hour is missing'
    assert lat is not None, 'latitude is missing'
    assert lon is not None, 'longitude is missing'
    assert 1 <= month <= 12, 'month is invalid'
    assert 1 <= day <= 31, 'day is invalid'
    assert 0 <= hour <= 24, 'hour is invalid'
    assert 90 >= lat >= -90, 'latitude is invalid'

    daytime = False

    year2 = year
    day2 = dayinyear(year, month, day)
    hour2 = math.floor(hour)
    minute2 = (hour - math.floor(hour)) * 60.0
    lat2 = lat
    lon2 = lon
    if lat == 0:
        lat2 = 0.0001
    if lon == 0:
        lon2 = 0.0001

    azimuth, elevation, rta, hra, sid, dec = \
        sunangle(year2, day2, hour2, minute2, 0, 0, 0, lat2, lon2)

    if elevation > elevdlim:
        daytime = True

    return daytime


def trim_mean(inarr, trim):
    """
    Calculate a resistant (aka robust) mean of an input array given a trimming criteria.

    :param inarr: array of numbers
    :param trim: trimming criteria. A value of 10 trims one tenth of the values off each end of the sorted array before calculating the mean.
    :type inarr: array of floats
    :type trim: integer
    :return: trimmed mean
    :rtype: float
    """
    arr = np.array(inarr)
    if trim == 0:
        return np.mean(arr)

    length = len(arr)
    arr.sort()

    index1 = (length / trim)

    trim = np.mean(arr[index1:length - index1])

    return trim


def trim_std(inarr, trim):
    """
    Calculate a resistant (aka robust) standard deviation of an input array given a trimming criteria.

    :param inarr: array of numbers
    :param trim: trimming criteria. A value of 10 trims one tenth of the values off each end of the sorted array before
      calculating the standard deviation.
    :type inarr: array of floats
    :type trim: integer
    :return: trimmed standard deviation
    :rtype: float
    """
    arr = np.array(inarr)
    if trim == 0:
        return np.std(arr)

    length = len(arr)
    arr.sort()

    index1 = (length / trim)

    trim = np.std(arr[index1:length - index1])

    return trim


def aground_check(reps, smooth_win=41, min_win_period=8, max_win_period=10):
    """
    Check to see whether a drifter has run aground based on 1/100th degree precision positions. 
    A flag 'drf_agr' is set for each input report: flag=1 for reports deemed aground, else flag=0.
    
    Positional errors introduced by lon/lat 'jitter' and data precision can be of order several km's.
    Longitude and latitude timeseries are smoothed prior to assessment to reduce position 'jitter'. 
    Some post-smoothing position 'jitter' may remain and its expected magnitude is set within the 
    function by the 'tolerance' parameter. A drifter is deemed aground when, after a period of time, 
    the distance between reports is less than the 'tolerance'. The minimum period of time over which this 
    assessment is made is set by 'min_win_period'. This period must be long enough such that slow moving 
    drifters are not falsely flagged as aground given errors in position (e.g. a buoy drifting at around 
    1 cm/s will travel around 1 km/day; given 'tolerance' and precision errors of a few km's the 'min_win_period'
    needs to be several days to ensure distance-travelled exceeds the error so that motion is reliably 
    detected and the buoy is not falsely flagged as aground). However, min_win_period should not be longer
    than necessary as buoys that run aground for less than min_win_period will not be detected.  

    Because temporal sampling can be erratic the time period over which an assessment is made is specified 
    as a range (bound by 'min_win_period' and 'max_win_period') - assesment uses the longest time separation 
    available within this range. If a drifter is deemed aground and subsequently starts moving (e.g. if a drifter
    has moved very slowly for a prolonged period) incorrectly flagged reports will be reinstated.

    :param reps: a time-sorted list of drifter observations in format :class:`.Voyage`, each report must have a valid longitude, latitude and time-difference   
    :param smooth_win: length of window (odd number) in datapoints used for smoothing lon/lat
    :param min_win_period: minimum period of time in days over which position is assessed for no movement (see description)
    :param max_win_period: maximum period of time in days over which position is assessed for no movement (this should be greater than min_win_period and allow for erratic temporal sampling e.g. min_win_period+2 to allow for gaps of up to 2-days in sampling).  
    :type reps: a :class:`.Voyage`
    :type smooth_win: integer
    :type min_win_period: integer 
    :type max_win_period: integer
    """
    tolerance = sphere_distance(0, 0, 0.01, 0.01)
    # displacement resulting from 1/100th deg 'position-jitter' at equator (km)

    try:
        smooth_win = int(smooth_win)
        min_win_period = int(min_win_period)
        max_win_period = int(max_win_period)
        assert smooth_win >= 1, 'smooth_win must be >= 1'
        assert smooth_win % 2 != 0, 'smooth_win must be an odd number'
        assert min_win_period >= 1, 'min_win_period must be >= 1'
        assert max_win_period >= 1, 'max_win_period must be >= 1'
        assert max_win_period >= min_win_period, 'max_win_period must be >= min_win_period'
    except AssertionError as error:
        raise AssertionError('invalid input parameter: ' + str(error))

    half_win = (smooth_win - 1) / 2
    min_win_period_hours = min_win_period * 24.0
    max_win_period_hours = max_win_period * 24.0

    nrep = len(reps)
    if nrep <= smooth_win:  # records shorter than smoothing-window can't be evaluated
        print('Voyage too short for QC, setting flags to pass')
        for rep in reps:
            rep.set_qc('POS', 'drf_agr', 0)
        return

    # retrieve lon/lat/time_diff variables from marine reports
    lon = np.empty(nrep)
    lon[:] = np.nan
    lat = np.empty(nrep)
    lat[:] = np.nan
    hrs = np.empty(nrep)
    hrs[:] = np.nan
    try:
        for ind, rep in enumerate(reps):
            lon[ind] = rep.getvar('LON')  # returns None if missing
            lat[ind] = rep.getvar('LAT')  # returns None if missing
            if ind == 0:
                hrs[ind] = 0
            else:
                hrs[ind] = rep.getext('time_diff')  # raises assertion error if 'time_diff' not found
        assert not any(np.isnan(lon)), 'Nan(s) found in longitude'
        assert not any(np.isnan(lat)), 'Nan(s) found in latitude'
        assert not any(np.isnan(hrs)), 'Nan(s) found in time differences'
        assert not any(hrs < 0), 'times are not sorted'
    except AssertionError as error:
        raise AssertionError('problem with report values: ' + str(error))

    hrs = np.cumsum(hrs)  # get time difference in hours relative to first report

    # create smoothed lon/lat timeseries
    nrep_smooth = nrep - smooth_win + 1  # length of series after smoothing
    lon_smooth = np.empty(nrep_smooth)
    lon_smooth[:] = np.nan
    lat_smooth = np.empty(nrep_smooth)
    lat_smooth[:] = np.nan
    hrs_smooth = np.empty(nrep_smooth)
    hrs_smooth[:] = np.nan
    try:
        for i in range(0, nrep_smooth):
            lon_smooth[i] = np.median(lon[i:i + smooth_win])
            lat_smooth[i] = np.median(lat[i:i + smooth_win])
            hrs_smooth[i] = hrs[i + half_win]
        assert not any(np.isnan(lon_smooth)), 'Nan(s) found in smoothed longitude'
        assert not any(np.isnan(lat_smooth)), 'Nan(s) found in smoothed latitude'
        assert not any(np.isnan(hrs_smooth)), 'Nan(s) found in smoothed time differences'
    except AssertionError as error:
        raise AssertionError('problem with smoothed report values: ' + str(error))

    # loop through smoothed timeseries to see if drifter has run aground
    i = 0
    is_aground = False  # keeps track of whether drifter is deemed aground
    i_aground = np.nan  # keeps track of index when drifter first ran aground
    time_to_end = hrs_smooth[-1] - hrs_smooth[i]
    while time_to_end >= min_win_period_hours:
        f_win = (hrs_smooth <= hrs_smooth[i] + max_win_period_hours)
        win_len = hrs_smooth[f_win][-1] - hrs_smooth[i]
        if win_len < min_win_period_hours:
            i += 1
            time_to_end = hrs_smooth[-1] - hrs_smooth[i]
            continue

        displace = sphere_distance(lat_smooth[i], lon_smooth[i],
                                   lat_smooth[f_win][-1], lon_smooth[f_win][-1])
        if displace <= tolerance:
            if is_aground:
                i += 1
                time_to_end = hrs_smooth[-1] - hrs_smooth[i]
                continue
            else:
                is_aground = True
                i_aground = i
                i += 1
                time_to_end = hrs_smooth[-1] - hrs_smooth[i]
        else:
            is_aground = False
            i_aground = np.nan
            i += 1
            time_to_end = hrs_smooth[-1] - hrs_smooth[i]

            # set flags
    if is_aground:
        if i_aground > 0:
            i_aground += half_win
        # this gets the first index the drifter is deemed aground for the original (un-smoothed) timeseries
        # n.b. if i_aground=0 then the entire drifter record is deemed aground and flagged as such 
    for ind, rep in enumerate(reps):
        if is_aground:
            if ind < i_aground:
                rep.set_qc('POS', 'drf_agr', 0)
            else:
                rep.set_qc('POS', 'drf_agr', 1)
        else:
            rep.set_qc('POS', 'drf_agr', 0)


def new_aground_check(reps, smooth_win=41, min_win_period=8):
    """
    Check to see whether a drifter has run aground based on 1/100th degree precision positions. 
    A flag 'drf_agr' is set for each input report: flag=1 for reports deemed aground, else flag=0.

    Positional errors introduced by lon/lat 'jitter' and data precision can be of order several km's.
    Longitude and latitude timeseries are smoothed prior to assessment to reduce position 'jitter'. 
    Some post-smoothing position 'jitter' may remain and its expected magnitude is set within the 
    function by the 'tolerance' parameter. A drifter is deemed aground when, after a period of time, 
    the distance between reports is less than the 'tolerance'. The minimum period of time over which this 
    assessment is made is set by 'min_win_period'. This period must be long enough such that slow moving 
    drifters are not falsely flagged as aground given errors in position (e.g. a buoy drifting at around 
    1 cm/s will travel around 1 km/day; given 'tolerance' and precision errors of a few km's the 'min_win_period'
    needs to be several days to ensure distance-travelled exceeds the error so that motion is reliably 
    detected and the buoy is not falsely flagged as aground). However, min_win_period should not be longer
    than necessary as buoys that run aground for less than min_win_period will not be detected.  

    The check progresses by comparing each report with the final report (i.e. the first report with the 
    final report, the second report with the final report and so on) until the time separation between reports 
    is less than 'min_win_period'. If a drifter is deemed aground and subsequently starts moving (e.g. if a drifter
    has followed a circular path) incorrectly flagged reports will be reinstated.

    :param reps: a time-sorted list of drifter observations in format :class:`.Voyage`,
      each report must have a valid longitude, latitude and time-difference   
    :param smooth_win: length of window (odd number) in datapoints used for smoothing lon/lat
    :param min_win_period: minimum period of time in days over which position is assessed for no movement (see
      description)
    :type reps: a :class:`.Voyage`
    :type smooth_win: integer
    :type min_win_period: integer 
    """
    tolerance = sphere_distance(0, 0, 0.01, 0.01)
    # displacement resulting from 1/100th deg 'position-jitter' at equator (km)

    try:
        smooth_win = int(smooth_win)
        min_win_period = int(min_win_period)
        assert smooth_win >= 1, 'smooth_win must be >= 1'
        assert smooth_win % 2 != 0, 'smooth_win must be an odd number'
        assert min_win_period >= 1, 'min_win_period must be >= 1'
    except AssertionError as error:
        raise AssertionError('invalid input parameter: ' + str(error))

    half_win = (smooth_win - 1) / 2
    min_win_period_hours = min_win_period * 24.0

    nrep = len(reps)
    if nrep <= smooth_win:  # records shorter than smoothing-window can't be evaluated
        print('Voyage too short for QC, setting flags to pass')
        for rep in reps:
            rep.set_qc('POS', 'drf_agr', 0)
        return

    # retrieve lon/lat/time_diff variables from marine reports
    lon = np.empty(nrep)
    lon[:] = np.nan
    lat = np.empty(nrep)
    lat[:] = np.nan
    hrs = np.empty(nrep)
    hrs[:] = np.nan
    try:
        for ind, rep in enumerate(reps):
            lon[ind] = rep.getvar('LON')  # returns None if missing
            lat[ind] = rep.getvar('LAT')  # returns None if missing
            if ind == 0:
                hrs[ind] = 0
            else:
                hrs[ind] = rep.getext('time_diff')  # raises assertion error if 'time_diff' not found
        assert not any(np.isnan(lon)), 'Nan(s) found in longitude'
        assert not any(np.isnan(lat)), 'Nan(s) found in latitude'
        assert not any(np.isnan(hrs)), 'Nan(s) found in time differences'
        assert not any(hrs < 0), 'times are not sorted'
    except AssertionError as error:
        raise AssertionError('problem with report values: ' + str(error))

    hrs = np.cumsum(hrs)  # get time difference in hours relative to first report

    # create smoothed lon/lat timeseries
    nrep_smooth = nrep - smooth_win + 1  # length of series after smoothing
    lon_smooth = np.empty(nrep_smooth)
    lon_smooth[:] = np.nan
    lat_smooth = np.empty(nrep_smooth)
    lat_smooth[:] = np.nan
    hrs_smooth = np.empty(nrep_smooth)
    hrs_smooth[:] = np.nan
    try:
        for i in range(0, nrep_smooth):
            lon_smooth[i] = np.median(lon[i:i + smooth_win])
            lat_smooth[i] = np.median(lat[i:i + smooth_win])
            hrs_smooth[i] = hrs[i + half_win]
        assert not any(np.isnan(lon_smooth)), 'Nan(s) found in smoothed longitude'
        assert not any(np.isnan(lat_smooth)), 'Nan(s) found in smoothed latitude'
        assert not any(np.isnan(hrs_smooth)), 'Nan(s) found in smoothed time differences'
    except AssertionError as error:
        raise AssertionError('problem with smoothed report values: ' + str(error))

    # loop through smoothed timeseries to see if drifter has run aground
    i = 0
    is_aground = False  # keeps track of whether drifter is deemed aground
    i_aground = np.nan  # keeps track of index when drifter first ran aground
    time_to_end = hrs_smooth[-1] - hrs_smooth[i]
    while time_to_end >= min_win_period_hours:

        displace = sphere_distance(lat_smooth[i], lon_smooth[i],
                                   lat_smooth[-1], lon_smooth[-1])
        if displace <= tolerance:
            if is_aground:
                i += 1
                time_to_end = hrs_smooth[-1] - hrs_smooth[i]
                continue
            else:
                is_aground = True
                i_aground = i
                i += 1
                time_to_end = hrs_smooth[-1] - hrs_smooth[i]
        else:
            is_aground = False
            i_aground = np.nan
            i += 1
            time_to_end = hrs_smooth[-1] - hrs_smooth[i]

            # set flags
    if is_aground:
        if i_aground > 0:
            i_aground += half_win
        # this gets the first index the drifter is deemed aground for the original (un-smoothed) timeseries
        # n.b. if i_aground=0 then the entire drifter record is deemed aground and flagged as such 
    for ind, rep in enumerate(reps):
        if is_aground:
            if ind < i_aground:
                rep.set_qc('POS', 'drf_agr', 0)
            else:
                rep.set_qc('POS', 'drf_agr', 1)
        else:
            rep.set_qc('POS', 'drf_agr', 0)


def speed_check(reps, speed_limit=2.5, min_win_period=0.8, max_win_period=1.0):
    """
    Check to see whether a drifter has been picked up by a ship (out of water) based on 1/100th degree 
    precision positions. A flag 'drf_spd' is set for each input report: flag=1 for reports deemed picked up, 
    else flag=0.

    A drifter is deemed picked up if it is moving faster than might be expected for a fast ocean current
    (a few m/s). Unreasonably fast movement is detected when speed of travel between report-pairs exceeds
    the chosen 'speed_limit' (speed is estimated as distance between reports divided by time separation - 
    this 'straight line' speed between the two points is a minimum speed estimate given a less-direct
    path may have been followed). Positional errors introduced by lon/lat 'jitter' and data precision 
    can be of order several km's. Reports must be separated by a suitably long period of time (the 'min_win_period') 
    to minimise the effect of these errors when calculating speed e.g. for reports separated by 24 hours
    errors of several cm/s would result which are two orders of magnitude less than a fast ocean current
    which seems reasonable. Conversley, the period of time chosen should not be too long so as to resolve 
    short-lived burst of speed on manouvering ships. Larger positional errors may also trigger the check.  
    Because temporal sampling can be erratic the time period over which this assessment is made is specified
    as a range (bound by 'min_win_period' and 'max_win_period') - assesment uses the longest time separation 
    available within this range.

    IMPORTANT - for optimal performance, drifter records with observations failing this check should be
    subsequently manually reviewed. Ships move around in all sorts of complicated ways that can readily
    confuse such a simple check (e.g. pausing at sea, crisscrossing its own path) and once some erroneous 
    movement is detected it is likely a human operator can then better pick out the actual bad data. False
    fails caused by positional errors (particularly in fast ocean currents) will also need reinstating. 

    :param reps: a time-sorted list of drifter observations in format :class:`.Voyage`,
      each report must have a valid longitude, latitude and time-difference   
    :param speed_limit: maximum allowable speed for an in situ drifting buoy (metres per second) 
    :param min_win_period: minimum period of time in days over which position is assessed for speed estimates (see
      description)
    :param max_win_period: maximum period of time in days over which position is assessed for speed estimates
      (this should be greater than min_win_period and allow for some erratic temporal sampling e.g. min_win_period+0.2
      to allow for gaps of up to 0.2-days in sampling).
    :type reps: a :class:`.Voyage`
    :type speed_limit: float
    :type min_win_period: float 
    :type max_win_period: float 
    """

    try:
        speed_limit = float(speed_limit)
        min_win_period = float(min_win_period)
        max_win_period = float(max_win_period)
        assert speed_limit >= 0, 'speed_limit must be >= 0'
        assert min_win_period >= 0, 'min_win_period must be >= 0'
        assert max_win_period >= 0, 'max_win_period must be >= 0'
        assert max_win_period >= min_win_period, 'max_win_period must be >= min_win_period'
    except AssertionError as error:
        raise AssertionError('invalid input parameter: ' + str(error))

    min_win_period_hours = min_win_period * 24.0
    max_win_period_hours = max_win_period * 24.0

    nrep = len(reps)
    if nrep <= 1:  # pairs of records are needed to evaluate speed
        print('Voyage too short for QC, setting flags to pass')
        for rep in reps:
            rep.set_qc('POS', 'drf_spd', 0)
        return

    # retrieve lon/lat/time_diff variables from marine reports
    lon = np.empty(nrep)
    lon[:] = np.nan
    lat = np.empty(nrep)
    lat[:] = np.nan
    hrs = np.empty(nrep)
    hrs[:] = np.nan
    try:
        for ind, rep in enumerate(reps):
            lon[ind] = rep.getvar('LON')  # returns None if missing
            lat[ind] = rep.getvar('LAT')  # returns None if missing
            if ind == 0:
                hrs[ind] = 0
            else:
                hrs[ind] = rep.getext('time_diff')  # raises assertion error if 'time_diff' not found
        assert not any(np.isnan(lon)), 'Nan(s) found in longitude'
        assert not any(np.isnan(lat)), 'Nan(s) found in latitude'
        assert not any(np.isnan(hrs)), 'Nan(s) found in time differences'
        assert not any(hrs < 0), 'times are not sorted'
    except AssertionError as error:
        raise AssertionError('problem with report values: ' + str(error))

    hrs = np.cumsum(hrs)  # get time difference in hours relative to first report

    # begin by setting all reports to pass
    for rep in reps:
        rep.set_qc('POS', 'drf_spd', 0)

    # loop through timeseries to see if drifter is moving too fast
    # and flag any occurences
    index_arr = np.array(range(0, nrep))
    i = 0
    time_to_end = hrs[-1] - hrs[i]
    while time_to_end >= min_win_period_hours:
        f_win = (hrs <= hrs[i] + max_win_period_hours)
        win_len = hrs[f_win][-1] - hrs[i]
        if win_len < min_win_period_hours:
            i += 1
            time_to_end = hrs[-1] - hrs[i]
            continue

        displace = sphere_distance(lat[i], lon[i], lat[f_win][-1], lon[f_win][-1])
        speed = displace / win_len  # km per hr
        speed = speed * 1000. / (60. * 60)  # metres per sec

        if speed > speed_limit:
            for ix in range(i, index_arr[f_win][-1] + 1):
                if reps[ix].get_qc('POS', 'drf_spd') == 0:
                    reps[ix].set_qc('POS', 'drf_spd', 1)
            i += 1
            time_to_end = hrs[-1] - hrs[i]
        else:
            i += 1
            time_to_end = hrs[-1] - hrs[i]


def new_speed_check(reps, iquam_parameters, speed_limit=3.0, min_win_period=0.375):
    """
    Check to see whether a drifter has been picked up by a ship (out of water) based on 1/100th degree 
    precision positions. A flag 'drf_spd' is set for each input report: flag=1 for reports deemed picked up, 
    else flag=0.
    
    A drifter is deemed picked up if it is moving faster than might be expected for a fast ocean current
    (a few m/s). Unreasonably fast movement is detected when speed of travel between report-pairs exceeds
    the chosen 'speed_limit' (speed is estimated as distance between reports divided by time separation - 
    this 'straight line' speed between the two points is a minimum speed estimate given a less-direct
    path may have been followed). Positional errors introduced by lon/lat 'jitter' and data precision 
    can be of order several km's. Reports must be separated by a suitably long period of time (the 'min_win_period') 
    to minimise the effect of these errors when calculating speed e.g. for reports separated by 9 hours
    errors of order 10 cm/s would result which are a few percent of fast ocean current speed. Conversley, 
    the period of time chosen should not be too long so as to resolve short-lived burst of speed on 
    manouvering ships. Larger positional errors may also trigger the check.  

    For each report, speed is assessed over the shortest available period that exceeds 'min_win_period'.
    
    Prior to assessment the drifter record is screened for positional errors using the iQuam track check
    method (from :class:`.Voyage`). When running the iQuam check the record is treated as a ship (not a
    drifter) so as to avoid accidentally filtering out observations made aboard a ship (which is what we 
    are trying to detect). This iQuam track check does not overwrite any existing iQuam track check flags. 

    IMPORTANT - for optimal performance, drifter records with observations failing this check should be
    subsequently manually reviewed. Ships move around in all sorts of complicated ways that can readily
    confuse such a simple check (e.g. pausing at sea, crisscrossing its own path) and once some erroneous 
    movement is detected it is likely a human operator can then better pick out the actual bad data. False
    fails caused by positional errors (particularly in fast ocean currents) will also need reinstating.     

    :param reps: a time-sorted list of drifter observations in format :class:`.Voyage`,
      each report must have a valid longitude, latitude and time-difference
    :param iquam_parameters: Parameter dictionary for Voyage.iquam_track_check() function.   
    :param speed_limit: maximum allowable speed for an in situ drifting buoy (metres per second) 
    :param min_win_period: minimum period of time in days over which position is assessed for speed estimates (see
      description)
    :type reps: a :class:`.Voyage`
    :type iquam_parameters: dictionary 
    :type speed_limit: float
    :type min_win_period: float 
    """

    try:
        speed_limit = float(speed_limit)
        min_win_period = float(min_win_period)
        assert speed_limit >= 0, 'speed_limit must be >= 0'
        assert min_win_period >= 0, 'min_win_period must be >= 0'
    except AssertionError as error:
        raise AssertionError('invalid input parameter: ' + str(error))

    min_win_period_hours = min_win_period * 24.0

    nrep = len(reps)
    if nrep <= 1:  # pairs of records are needed to evaluate speed
       print('Voyage too short for QC, setting flags to pass') 
       for rep in reps:
            rep.set_qc('POS', 'drf_spd', 0)
       return

    # retrieve lon/lat/time_diff variables from marine reports
    lon = np.empty(nrep)
    lon[:] = np.nan
    lat = np.empty(nrep)
    lat[:] = np.nan
    hrs = np.empty(nrep)
    hrs[:] = np.nan
    try:
        for ind, rep in enumerate(reps):
            lon[ind] = rep.getvar('LON')  # returns None if missing
            lat[ind] = rep.getvar('LAT')  # returns None if missing
            if ind == 0:
                hrs[ind] = 0
            else:
                hrs[ind] = rep.getext('time_diff')  # raises assertion error if 'time_diff' not found
        assert not any(np.isnan(lon)), 'Nan(s) found in longitude'
        assert not any(np.isnan(lat)), 'Nan(s) found in latitude'
        assert not any(np.isnan(hrs)), 'Nan(s) found in time differences'
        assert not any(hrs < 0), 'times are not sorted'
    except AssertionError as error:
        raise AssertionError('problem with report values: ' + str(error))

    hrs = np.cumsum(hrs)  # get time difference in hours relative to first report

    # perform iQuam track check as if a ship
    # a deep copy of reps is made so metadata can be safely modified ahead of iQuam check
    # an array of qc flags (iquam_track_ship) is the result
    reps_copy = copy.deepcopy(reps)
    v = ex.Voyage()
    qc_list = []
    for rep in reps_copy:
        rep.setvar('PT', 5)  # ship
        rep.set_qc('POS', 'iquam_track', 0)  # reset iquam parameters
        v.add_report(rep)
    v.iquam_track_check(iquam_parameters)
    for rep in v.rep_feed():
        qc_list.append(rep.get_qc('POS', 'iquam_track'))
    iquam_track_ship = np.array(qc_list)
    del reps_copy, v, qc_list

    # begin by setting all reports to pass
    for rep in reps:
        rep.set_qc('POS', 'drf_spd', 0)

    # loop through timeseries to see if drifter is moving too fast
    # and flag any occurences
    index_arr = np.array(range(0, nrep))
    i = 0
    time_to_end = hrs[-1] - hrs[i]
    while time_to_end >= min_win_period_hours:
        if iquam_track_ship[i] == 1:
            i += 1
            time_to_end = hrs[-1] - hrs[i]
            continue
        f_win = (hrs >= hrs[i] + min_win_period_hours) & \
                (iquam_track_ship == 0)
        if not any(f_win):
            i += 1
            time_to_end = hrs[-1] - hrs[i]
            continue

        win_len = hrs[f_win][0] - hrs[i]
        displace = sphere_distance(lat[i], lon[i], lat[f_win][0], lon[f_win][0])
        speed = displace / win_len  # km per hr
        speed = speed * 1000. / (60. * 60)  # metres per sec

        if speed > speed_limit:
            for ix in range(i, index_arr[f_win][0] + 1):
                if reps[ix].get_qc('POS', 'drf_spd') == 0:
                    reps[ix].set_qc('POS', 'drf_spd', 1)
            i += 1
            time_to_end = hrs[-1] - hrs[i]
        else:
            i += 1
            time_to_end = hrs[-1] - hrs[i]


def sst_tail_check(reps, long_win_len=121, long_err_std_n=3.0, short_win_len=30, short_err_std_n=3.0,
                   short_win_n_bad=2, drif_inter=0.29, drif_intra=1.00, background_err_lim=0.3):
    """
    Check to see whether there is erroneous sea surface temperature data at the beginning or end of a drifter record
    (referred to as 'tails'). The flags 'drf_tail1' and 'drf_tail2' are set for each input report: flag=1 for reports
    with erroneous data, else flag=0, 'drf_tail1' is used for bad data at the beginning of a record, 'drf_tail2' is
    used for bad data at the end of a record.

    The tail check makes an assessment of the quality of data at the start and end of a drifting buoy record by
    comparing to a background reference field. Data found to be unacceptably biased or noisy relative to the
    background are flagged by the check. When making the comparison an allowance is made for background error
    variance and also normal drifter error (both bias and random measurement error). The correlation of the
    background error is treated as unknown and takes on a value which maximises background error dependent on the
    assesment being made. A background error variance limit is also specified, beyond which the background is deemed
    unreliable. Observations made during the day, in icy regions or where the background value is missing are
    excluded from the comparison.

    The check proceeds in two steps; a 'long tail-check' followed by a 'short tail-check'. The idea is that the short
    tail-check has finer resolution but lower sensitivity than the long tail-check and may pick off noisy data not
    picked up by the long tail check. Only observations that pass the long tail-check are passed to the short
    tail-check. Both of these tail checks proceed by moving a window over the data and assessing the data in each
    window. Once good data are found the check stops and any bad data preceeding this are flagged. If unreliable
    background data are encountered the check stops. The checks are run forwards and backwards over the record so as
    to assess data at the start and end of the record. If the whole record fails no observations are flagged as there
    are then no 'tails' in the data (this is left for other checks). The long tail check looks for groups of
    observations that are too biased or noisy as a whole. The short tail check looks for individual observations
    exceeding a noise limit within the window.

    :param reps: a time-sorted list of drifter observations in format :class:`.Voyage`, each report must have a 
      valid longitude, latitude and time and matched values for OSTIA, ICE and BGVAR in its extended data
    :param long_win_len: length of window (in data-points) over which to make long tail-check (must be an odd number)
    :param long_err_std_n: number of standard deviations of combined background and drifter bias error, beyond which
      data fail bias check
    :param short_win_len: length of window (in data-points) over which to make the short tail-check
    :param short_err_std_n: number of standard deviations of combined background and drifter error, beyond which data
      are deemed suspicious
    :param short_win_n_bad: minimum number of suspicious data points required for failure of short check window
    :param drif_inter: spread of biases expected in drifter data (standard deviation, degC)
    :param drif_intra: maximum random measurement uncertainty reasonably expected in drifter data (standard deviation,
      degC)
    :param background_err_lim: background error variance beyond which the SST background is deemed unreliable (degC
      squared)
    :type reps: a :class:`.Voyage`
    :type long_win_len: integer
    :type long_err_std_n: float
    :type short_win_len: integer
    :type short_err_std_n: float
    :type short_win_n_bad: integer
    :type drif_inter: float
    :type drif_intra: float
    :type background_err_lim: float
    """

    try:
        long_win_len = int(long_win_len)
        long_err_std_n = float(long_err_std_n)
        short_win_len = int(short_win_len)
        short_err_std_n = float(short_err_std_n)
        short_win_n_bad = int(short_win_n_bad)
        drif_inter = float(drif_inter)
        drif_intra = float(drif_intra)
        background_err_lim = float(background_err_lim)
        assert long_win_len >= 1, 'long_win_len must be >= 1'
        assert long_win_len % 2 != 0, 'long_win_len must be an odd number'
        assert long_err_std_n >= 0, 'long_err_std_n must be >= 0'
        assert short_win_len >= 1, 'short_win_len must be >= 1'
        assert short_err_std_n >= 0, 'short_err_std_n must be >= 0'
        assert short_win_n_bad >= 1, 'short_win_n_bad must be >= 1'
        assert drif_inter >= 0, 'drif_inter must be >= 0'
        assert drif_intra >= 0, 'drif_intra must be >= 0'
        assert background_err_lim >= 0, 'background_err_lim must be >= 0'
    except AssertionError as error:
        raise AssertionError('invalid input parameter: ' + str(error))

    # test and filter out obs with unsuitable background matches
    reps_ind = []
    sst_anom = []
    bgvar = []
    for ind, rep in enumerate(reps):
        try:
            bg_val = rep.getext('OSTIA')  # raises assertion error if not found
            ice_val = rep.getext('ICE')  # raises assertion error if not found
            bgvar_val = rep.getext('BGVAR')  # raises assertion error if not found
        except AssertionError as error:
            raise AssertionError('matched report value is missing: ' + str(error))

        if ice_val is None:
            ice_val = 0.0
        assert ice_val is not None and 0.0 <= ice_val <= 1.0, 'matched ice proportion is invalid'

        try:
            daytime = track_day_test(rep.getvar('YR'), rep.getvar('MO'), rep.getvar('DY'),
                                     rep.getvar('HR'), rep.getvar('LAT'), rep.getvar('LON'), -2.5)
        except AssertionError as error:
            raise AssertionError('problem with report value: ' + str(error))
        if ind > 0:
            try:
                time_diff = rep.getext('time_diff')  # raises assertion error if 'time_diff' not found
                assert time_diff >= 0, 'times are not sorted'
            except AssertionError as error:
                raise AssertionError('problem with report value: ' + str(error))

        land_match = True if bg_val is None else False
        ice_match = True if ice_val > 0.15 else False
        if daytime or land_match or ice_match:
            pass
        else:
            assert bg_val is not None and -5.0 <= bg_val <= 45.0, 'matched background sst is invalid'
            assert bgvar_val is not None and 0.0 <= bgvar_val <= 10, 'matched background error variance is invalid'
            reps_ind.append(ind)
            sst_anom.append(rep.getvar('SST') - bg_val)
            bgvar.append(bgvar_val)

    # set start and end tail flags to pass to ensure all obs receive flag
    # then exit if there are no obs suitable for assessment
    for rep in reps:
        rep.set_qc('SST', 'drf_tail1', 0)
        rep.set_qc('SST', 'drf_tail2', 0)
    if len(sst_anom) == 0:
        return

    # prepare numpy arrays and variables needed for tail checks
    reps_ind = np.array(reps_ind)  # indices of obs suitable for assessment
    sst_anom = np.array(sst_anom)  # ob-background differences
    bgerr = np.sqrt(np.array(bgvar))  # standard deviation of background error
    nrep = len(sst_anom)
    start_tail_ind = -1  # keeps track of index where start tail stops
    end_tail_ind = nrep  # keeps track of index where end tail starts

    # do long tail check
    mid_win_ind = (long_win_len - 1) / 2
    if nrep < long_win_len:  # records shorter than long-window length aren't evaluated
        pass
    else:
        for forward in [True, False]:  # run forwards then backwards over timeseries
            if forward:
                sst_anom_temp = sst_anom
                bgerr_temp = bgerr
            else:
                sst_anom_temp = np.flipud(sst_anom)
                bgerr_temp = np.flipud(bgerr)
            # this is the long tail check
            for ix in range(0, nrep - long_win_len + 1):
                sst_anom_winvals = sst_anom_temp[ix:ix + long_win_len]
                bgerr_winvals = bgerr_temp[ix:ix + long_win_len]
                if np.any(bgerr_winvals > np.sqrt(background_err_lim)):
                    break
                sst_anom_avg = trim_mean(sst_anom_winvals, 100)
                sst_anom_stdev = trim_std(sst_anom_winvals, 100)
                bgerr_avg = np.mean(bgerr_winvals)
                bgerr_rms = np.sqrt(np.mean(bgerr_winvals ** 2))
                if (abs(sst_anom_avg) > long_err_std_n * np.sqrt(drif_inter ** 2 + bgerr_avg ** 2)) \
                        or (sst_anom_stdev > np.sqrt(drif_intra ** 2 + bgerr_rms ** 2)):
                    if forward:
                        start_tail_ind = ix + mid_win_ind
                    else:
                        end_tail_ind = (nrep - 1) - ix - mid_win_ind
                else:
                    break

    # do short tail check on records that pass long tail check
    if start_tail_ind >= end_tail_ind:  # whole record already failed long tail check
        pass
    else:
        first_pass_ind = start_tail_ind + 1  # first index passing long tail check
        last_pass_ind = end_tail_ind - 1  # last index passing long tail check
        npass = last_pass_ind - first_pass_ind + 1
        assert npass > 0, 'short tail check: npass not > 0'
        if npass < short_win_len:  # records shorter than short-window length aren't evaluated
            pass
        else:
            for forward in [True, False]:  # run forwards then backwards over timeseries
                if forward:
                    sst_anom_temp = sst_anom[first_pass_ind:last_pass_ind + 1]
                    bgerr_temp = bgerr[first_pass_ind:last_pass_ind + 1]
                else:
                    sst_anom_temp = np.flipud(sst_anom[first_pass_ind:last_pass_ind + 1])
                    bgerr_temp = np.flipud(bgerr[first_pass_ind:last_pass_ind + 1])
                # this is the short tail check
                for ix in range(0, npass - short_win_len + 1):
                    sst_anom_winvals = sst_anom_temp[ix:ix + short_win_len]
                    bgerr_winvals = bgerr_temp[ix:ix + short_win_len]
                    if np.any(bgerr_winvals > np.sqrt(background_err_lim)):
                        break
                    limit = short_err_std_n * np.sqrt(bgerr_winvals ** 2 + drif_inter ** 2 + drif_intra ** 2)
                    exceed_limit = np.logical_or(sst_anom_winvals > limit, sst_anom_winvals < -limit)
                    if np.sum(exceed_limit) >= short_win_n_bad:
                        if forward:
                            if ix == (npass - short_win_len):  # if all windows have failed, flag everything
                                start_tail_ind += short_win_len
                            else:
                                start_tail_ind += 1
                        else:
                            if ix == (npass - short_win_len):  # if all windows have failed, flag everything
                                end_tail_ind -= short_win_len
                            else:
                                end_tail_ind -= 1
                    else:
                        break

                        # now flag reps
    if start_tail_ind >= end_tail_ind:  # whole record failed tail checks, dont flag
        start_tail_ind = -1
        end_tail_ind = nrep
    if not start_tail_ind == -1:
        for ind, rep in enumerate(reps):
            if ind <= reps_ind[start_tail_ind]:
                rep.set_qc('SST', 'drf_tail1', 1)
    if not end_tail_ind == nrep:
        for ind, rep in enumerate(reps):
            if ind >= reps_ind[end_tail_ind]:
                rep.set_qc('SST', 'drf_tail2', 1)

    return


def sst_biased_noisy_check(reps, n_eval=30, bias_lim=1.10, drif_intra=1.0, drif_inter=0.29, err_std_n=3.0, n_bad=2,
                           background_err_lim=0.3):
    """
    Check to see whether a drifter sea surface temperature record is unacceptably biased or noisy as a whole.  

    The check makes an assessment of the quality of data in a drifting buoy record by comparing to a background
    reference field. If the record is found to be unacceptably biased or noisy relative to the background all
    observations are flagged by the check. For longer records the flags 'drf_bias' and 'drf_noise' are set for each
    input report: flag=1 for records with erroneous data, else flag=0. For shorter records 'drf_short' is set for
    each input report: flag=1 for reports with erroneous data, else flag=0.

    When making the comparison an allowance is made for background error variance and also normal drifter error (both
    bias and random measurement error). A background error variance limit is also specified, beyond which the
    background is deemed unreliable and is excluded from comparison. Observations made during the day, in icy regions
    or where the background value is missing are also excluded from the comparison.

    The check has two separate streams; a 'long-record check' and a 'short-record check'. Records with at least
    n_eval observations are passed to the long-record check, else they are passed to the short-record check. The
    long-record check looks for records that are too biased or noisy as a whole. The short record check looks for
    individual observations exceeding a noise limit within a record. The purpose of n_eval is to ensure records with
    too few observations for their bias and noise to be reliably estimated are handled separately by the short-record
    check.
 
    The correlation of the background error is treated as unknown and handled differently for each assessment. For
    the long-record noise-check and the short-record check the background error is treated as uncorrelated,
    which maximises the possible impact of background error on these assessments. For the long-record bias-check a
    limit (bias_lim) is specified beyond which the record is considered biased. The default value for this limit was
    chosen based on histograms of drifter-background bias. An alternative approach would be to treat the background
    error as entirely correlated across a long-record, which maximises its possible impact on the bias assessment. In
    this case the histogram approach was used as the limit could be tuned to give better results.

    :param reps: a time-sorted list of drifter observations in format from :class:`.Voyage`,
      each report must have a valid longitude, latitude and time and matched values for OSTIA, ICE and BGVAR in its
      extended data
    :param n_eval: the minimum number of drifter observations required to be assessed by the long-record check
    :param bias_lim: maximum allowable drifter-background bias, beyond which a record is considered biased (degC)
    :param drif_intra: maximum random measurement uncertainty reasonably expected in drifter data (standard
      deviation, degC)
    :param drif_inter: spread of biases expected in drifter data (standard deviation, degC)
    :param err_std_n: number of standard deviations of combined background and drifter error, beyond which
      short-record data are deemed suspicious
    :param n_bad: minimum number of suspicious data points required for failure of short-record check 
    :param background_err_lim: background error variance beyond which the SST background is deemed unreliable
      (degC squared)
    :type reps: a :class:`.Voyage`
    :type n_eval: integer 
    :type bias_lim: float 
    :type drif_intra: float
    :type drif_inter: float
    :type err_std_n: float
    :type n_bad: integer
    :type background_err_lim: float
    """

    try:
        n_eval = int(n_eval)
        bias_lim = float(bias_lim)
        drif_intra = float(drif_intra)
        drif_inter = float(drif_inter)
        err_std_n = float(err_std_n)
        n_bad = int(n_bad)
        background_err_lim = float(background_err_lim)
        assert n_eval > 0, 'n_eval must be > 0'
        assert bias_lim >= 0, 'bias_lim must be >= 0'
        assert drif_intra >= 0, 'drif_intra must be >= 0'
        assert drif_inter >= 0, 'drif_inter must be >= 0'
        assert err_std_n >= 0, 'err_std_n must be >= 0'
        assert n_bad >= 1, 'n_bad must be >= 1'
        assert background_err_lim >= 0, 'background_err_lim must be >= 0'
    except AssertionError as error:
        raise AssertionError('invalid input parameter: ' + str(error))

    # test and filter out obs with unsuitable background matches
    sst_anom = []
    bgvar = []
    bgvar_is_masked = False
    for ind, rep in enumerate(reps):
        try:
            bg_val = rep.getext('OSTIA')  # raises assertion error if not found
            ice_val = rep.getext('ICE')  # raises assertion error if not found
            bgvar_val = rep.getext('BGVAR')  # raises assertion error if not found
        except AssertionError as error:
            raise AssertionError('matched report value is missing: ' + str(error))

        if ice_val is None:
            ice_val = 0.0
        assert ice_val is not None and 0.0 <= ice_val <= 1.0, 'matched ice proportion is invalid'

        try:
            daytime = track_day_test(rep.getvar('YR'), rep.getvar('MO'), rep.getvar('DY'),
                                     rep.getvar('HR'), rep.getvar('LAT'), rep.getvar('LON'), -2.5)
        except AssertionError as error:
            raise AssertionError('problem with report value: ' + str(error))
        if ind > 0:
            try:
                time_diff = rep.getext('time_diff')  # raises assertion error if 'time_diff' not found
                assert time_diff >= 0, 'times are not sorted'
            except AssertionError as error:
                raise AssertionError('problem with report value: ' + str(error))

        land_match = True if bg_val is None else False
        ice_match = True if ice_val > 0.15 else False
        bgvar_mask = True if bgvar_val is not None and bgvar_val > background_err_lim else False
        if bgvar_mask:
            bgvar_is_masked = True
        if daytime or land_match or ice_match or bgvar_mask:
            pass
        else:
            assert bg_val is not None and -5.0 <= bg_val <= 45.0, 'matched background sst is invalid'
            assert bgvar_val is not None and 0.0 <= bgvar_val <= 10, 'matched background error variance is invalid'
            sst_anom.append(rep.getvar('SST') - bg_val)
            bgvar.append(bgvar_val)

    # set bias and noise flags to pass to ensure all obs receive flag
    # then exit if there are no obs suitable for assessment
    for rep in reps:
        rep.set_qc('SST', 'drf_bias', 0)
        rep.set_qc('SST', 'drf_noise', 0)
        rep.set_qc('SST', 'drf_short', 0)
    if len(sst_anom) == 0:
        return

    # prepare numpy arrays and variables needed for checks
    sst_anom = np.array(sst_anom)  # ob-background differences
    bgerr = np.sqrt(np.array(bgvar))  # standard deviation of background error

    nrep = len(sst_anom)
    long_record = True
    if nrep < n_eval:
        long_record = False

    # assess long records
    if long_record:
        sst_anom_avg = np.mean(sst_anom)
        sst_anom_stdev = np.std(sst_anom)
        bgerr_rms = np.sqrt(np.mean(bgerr ** 2))
        if abs(sst_anom_avg) > bias_lim:
            for rep in reps:
                rep.set_qc('SST', 'drf_bias', 1)
        if sst_anom_stdev > np.sqrt(drif_intra ** 2 + bgerr_rms ** 2):
            for rep in reps:
                rep.set_qc('SST', 'drf_noise', 1)
    else:
        if bgvar_is_masked:
            pass  # short record may still have unreliable values
        else:
            limit = err_std_n * np.sqrt(bgerr ** 2 + drif_inter ** 2 + drif_intra ** 2)
            exceed_limit = np.logical_or(sst_anom > limit, sst_anom < -limit)
            if np.sum(exceed_limit) >= n_bad:
                for rep in reps:
                    rep.set_qc('SST', 'drf_short', 1)

    return
