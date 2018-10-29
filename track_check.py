'''
The New Track Check QC module provides the functions needed to perform the 
track check. The main routine is mds_full_track_check which takes a 
list of :class:`.MarineReport` from a single ship and runs the track check on them. 
This is an update of the MDS system track check in that it assumes the Earth is a 
sphere. In practice it gives similar results to the cylindrical earth formerly 
assumed.
'''

import math
import qc
import Extended_IMMA as ex
import numpy as np
import spherical_geometry as sph

def modesp(awork):
    '''
    Calculate the modal speed from the input array in 3 knot bins. Returns the 
    bin-centre for the modal group.
    
    :param awork: list of input speeds in km/hr
    :type awork: float
    :return: bin-centre speed (expressed in km/ht) for the 3 knot bin which contains most speeds in 
             input array, or 8.5, whichever is higher
    :rtype: float
    
    The data are binned into 3-knot bins with the first from 0-3 knots having a 
    bin centre of 1.5 and the highest containing all speed in excess of 33 knots 
    with a bin centre of 34.5. The bin with the most speeds in it is found. The higher of 
    the modal speed or 8.5 is returned::

      Bins-   0-3, 3-6, 6-9, 9-12, 12-15, 15-18, 18-21, 21-24, 24-27, 27-30, 30-33, 33-36
      Centres-1.5, 4.5, 7.5, 10.5, 13.5,  16.5,  19.5,  22.5,  25.5,  28.5,  31.5,  34.5
    '''

# if there is one or no observations then return None
# if the speed is on a bin edge then it rounds up to higher bin
# if the modal speed is less than 8.50 then it is set to 8.50 
# anything exceeding 36 knots is assigned to the top bin

    km_to_nm = 0.539957

    ikmode = -32768
    acint = []
    ifreq = []
    for i in range(1, 13):
        acint.append(i*3.0)
        ifreq.append(0.0)

    ntime = len(awork)

    if ntime > 1:
        for i in range(1, ntime):
            #fixed so that indexing starts at zero
            index = int(math.floor(km_to_nm * awork[i]/3.0))  
            if index < 0:
                index = 0
            elif index > 11:
                index = 11
            ifreq[index] = ifreq[index] + 1

        for index in range(0, 12):
            if ifreq[index] > ikmode:
                ikmode = ifreq[index]
                icmode = 1
                atmode = acint[index] - 1.50

        amode = atmode/icmode
        if amode <= 8.50:
            amode = 8.50
    
    else:
        amode = None
    
    if amode != None:
        amode /= km_to_nm
    
    return amode

def set_speed_limits(amode):
    '''
    Takes a modal speed and calculates speed limits for the track checker
    
    :param amode: modal speed
    :type amode: float
    :return: max speed, max max speed and min speed
    :rtype: float
    '''
    km_to_nm = 0.539957
    
    amax  = 15.00/km_to_nm
    amaxx = 20.00/km_to_nm
    amin  = 0.00/km_to_nm

    if amode != None:
        if amode <= 8.51/km_to_nm:
            amax  = 15.00/km_to_nm
            amaxx = 20.00/km_to_nm
            amin  = 0.00/km_to_nm
        else:
            amax = amode * 1.25
            amaxx = 30.00/km_to_nm
            amin = amode * 0.75
        
    return amax, amaxx, amin

def increment_position(alat1, alon1, avs, ads, timdif):
    '''
    Increment_position takes two latitudes at the start 
    and end points of a line segment, a speed, a direction and a time difference and 
    returns increments of latitude and longitude which correspond to half the time difference.
    
    :param alat1: Latitude at starting point
    :param alon1: Longitude at starting point
    :param avs: speed of ship in km/hr
    :param ads: heading of ship in degrees
    :param timdif: time difference between the points in hours
    :type alat1: float
    :type alon1: float
    :type avs: float
    :type ads: float
    :type timdif: float
    '''
    
    if timdif != None:
        distance = avs * timdif / 2.
        lat,lon = sph.lat_lon_from_course_and_distance(alat1,alon1,ads,distance)
        lat -= alat1
        lon -= alon1        
    else:
        lat = None
        lon = None
    
    return lat, lon

def distr1(invoyage):
    '''
    Given an object of :class:`.Voyage`, 
    calculate what the distance is between the projected position (based on the reported 
    speed and heading at the current and previous time steps) and the actual position. The 
    observations are taken in time order.
    
    :param invoyage: Object of :class:`.Voyage`
    :type invoyage: :class:`.Voyage`
    :return: list of distances from estimated positions
    :rtype: list of floats
    
    This takes the speed and direction reported by the ship and projects it forwards half a 
    time step, it then projects it forwards another half time step using the speed and 
    direction for the next report, to which the projected location 
    is then compared. The distances between the projected and actual locations is returned
    '''
#Compute difference between actual and expected positions after
#two observations.
#Each vessel travels at its reported speed and direction for
#half the time interval; the difference (in miles) between
#the calculated and observed positions is calculatered.
    
    km_to_nm = 0.539957
    
    nobs = len(invoyage)

    distance_from_est_location = [None]

    for i in range(1, nobs):
        
        if (invoyage.getvar(i,   'vsi') != None and 
            invoyage.getvar(i-1, 'vsi') != None and
            invoyage.getvar(i,   'dsi') != None and 
            invoyage.getvar(i-1, 'dsi') != None and 
            invoyage.getvar(i,   'time_diff') != None):

#get increment from initial position
            lat1, lon1 = increment_position(invoyage.getvar(i-1, 'LAT'), 
                                            invoyage.getvar(i-1, 'LON'), 
                                            invoyage.getvar(i-1, 'vsi')/km_to_nm, 
                                            invoyage.getvar(i-1, 'dsi'), 
                                            invoyage.getvar(i,   'time_diff'))

            lat2, lon2 = increment_position(invoyage.getvar(i, 'LAT'), 
                                            invoyage.getvar(i, 'LON'), 
                                            invoyage.getvar(i, 'vsi')/km_to_nm, 
                                            invoyage.getvar(i, 'dsi'), 
                                            invoyage.getvar(i, 'time_diff'))
#apply increments to the lat and lon at i-1            
            alatx = invoyage.getvar(i-1, 'LAT') + lat1 + lat2
            alonx = invoyage.getvar(i-1, 'LON') + lon1 + lon2

#calculate distance between calculated position and the second reported position
            discrepancy = sph.sphere_distance(invoyage.getvar(i, 'LAT'),
                                              invoyage.getvar(i, 'LON'),
                                              alatx, alonx)

            distance_from_est_location.append(discrepancy)

        else:
#in the absence of reported speed and direction set to None
            distance_from_est_location.append(None)
 
    return distance_from_est_location

def distr2(invoyage):
    '''
    Given a list of :class:`.Voyage` , calculate what the 
    distance is between the projected position (based on the reported speed and 
    heading at the current and 
    previous time steps) and the actual position. The calculation proceeds from the 
    final, later observation to the 
    first (in contrast to distr1 which runs in time order)
    
    :param invoyage: List of :class:`.Voyage`
    :type invoyage: :class:`.Voyage`
    :return: list of distances from estimated positions
    :rtype: list of floats
    
    This takes the speed and direction reported by the ship and projects it forwards half a time step, it then projects 
    it forwards another half time step using the speed and direction for the next report, to which the projected location 
    is then compared. The distances between the projeted and actual locations is returned
    '''
#Compute difference between actual and expected positions after
#two observations IN REVERSE ORDER
#Each vessel travels at its reported speed and direction for
#half the time interval; the difference (in miles) between
#the calculated and observed positions is calculatered.

    km_to_nm = 0.539957
    
    nobs = len(invoyage)
    
    distance_from_est_location = [None]
    
    for i in range(nobs-1, 0, -1):
        
        if (invoyage.getvar(i,   'vsi') != None and 
            invoyage.getvar(i-1, 'vsi') != None and
            invoyage.getvar(i,   'dsi') != None and 
            invoyage.getvar(i-1, 'dsi') != None and
            invoyage.getvar(i,   'time_diff') != None):

#get increment from initial position - backwards in time 
#means reversing the direction by 180 degrees
            lat1, lon1 = increment_position(invoyage.getvar(i, 'LAT'), 
                                            invoyage.getvar(i, 'LON'), 
                                            invoyage.getvar(i, 'vsi') / km_to_nm, 
                                            invoyage.getvar(i, 'dsi') - 180.,
                                            invoyage.getvar(i, 'time_diff'))
                                            
            lat2, lon2 = increment_position(invoyage.getvar(i-1, 'LAT'), 
                                            invoyage.getvar(i-1, 'LON'), 
                                            invoyage.getvar(i-1, 'vsi') / km_to_nm, 
                                            invoyage.getvar(i-1, 'dsi') - 180.,
                                            invoyage.getvar(i,   'time_diff'))

#apply increments to the lat and lon at i-1            
            alatx = invoyage.getvar(i, 'LAT') + lat1 + lat2
            alonx = invoyage.getvar(i, 'LON') + lon1 + lon2

#calculate distance between calculated position and the second reported position
            discrepancy = sph.sphere_distance(invoyage.getvar(i-1, 'LAT'), 
                                              invoyage.getvar(i-1, 'LON'), 
                                              alatx, alonx)
            distance_from_est_location.append(discrepancy)

        else:
#in the absence of reported speed and direction set to None
            distance_from_est_location.append(None)

#that fancy bit at the end reverses the array  
    return distance_from_est_location[::-1]

def midpt(invoyage):
    '''
    Given an object of :class:`.Voyage` interpolate between alternate reports 
    and compare the 
    interpolated location to the actual location. e.g. take difference between 
    reports 2 and 4 and interpolate to get an estimate for the position at the time 
    of report 3. Then compare the estimated and actual positions at the time of 
    report 3.
    
    :param invoyage: Ship :class:`.Voyage`
    :type invoyage: :class:`.Voyage`
    :return: list of distances from estimated positions in km
    :rtype: list of floats
    
    The calculation linearly interpolates the latitudes and longitudes (allowing for 
    wrapping around the dateline and so on).
    '''    
#    Compute distance from time-proportional position between          
#       outside reported positions to middle reported position.

    nobs = len(invoyage)
    
    midpoint_discrepancies = [None]
    
    for i in range(1, nobs-1):
        
        t0 = invoyage.getvar(i,   'time_diff')
        t1 = invoyage.getvar(i+1, 'time_diff')
        
        if (t0 != None and t1 != None):
            if t0 + t1 != 0:
                fraction_of_time_diff = t0 / (t0 + t1)
            else:
                fraction_of_time_diff = 0.0
        else:
            fraction_of_time_diff = 0.0

        if fraction_of_time_diff > 1.0:
            print fraction_of_time_diff,t0,t1

        estimated_lat_at_midpt, estimated_lon_at_midpt =\
        sph.intermediate_point(invoyage.getvar(i-1, 'LAT'),invoyage.getvar(i-1, 'LON'),
                               invoyage.getvar(i+1, 'LAT'),invoyage.getvar(i+1, 'LON'),
                               fraction_of_time_diff)
        
#      Time-proportional position is at AT3 (N/S) and AN3 (E/W)         
#      Reported mid-point will be at    AT4 (N/S) and AN4 (E/W)         
#      Compute distance between time/prop posn and reported mid-point.  
#        SIDE1 is distance travelled North/South                        
        discrepancy = sph.sphere_distance(invoyage.getvar(i, 'LAT'), 
                                          invoyage.getvar(i, 'LON'),
                                          estimated_lat_at_midpt,
                                          estimated_lon_at_midpt)

        midpoint_discrepancies.append(discrepancy)

    midpoint_discrepancies.append(None)

    return midpoint_discrepancies

def direction_continuity(dsi, dsi_previous, ship_directions, 
                         max_direction_change=60.0):
    '''
    Check that the reported direction at the previous time step and the actual 
    direction taken are within max_direction_change degrees of one another.

    :param dsi: heading at current time step in degrees
    :param dsi_previous: heading at previous time step in degrees
    :param ship_directions: calculated ship direction from reported positions in degrees
    :param max_direction_change: largest deviations that will not be flagged
    :type dsi: float
    :type dsi_previous: float
    :type ship_directions: float
    :type max_direction_change: float
    :return: 10.0 if the difference between reported and calculated direction is greater than 60 degrees, 0.0 otherwise
    :rtype: float
    '''
#Check for continuity of direction                              
#          Error if actual direction is not within 60 degrees           
#            of reported direction of travel or previous reported       
#            direction of travel.
    result = 0.0

    assert dsi in [0, 45, 90, 135, 180, 225, 270, 315, 360, None]
    assert dsi_previous in [0, 45, 90, 135, 180, 225, 270, 315, 360, None]

    if dsi != None and dsi_previous != None and ship_directions != None:        
        if ((abs(dsi - ship_directions) > max_direction_change and
             abs(dsi - ship_directions) < 360-max_direction_change ) or
             (abs(dsi_previous - ship_directions) > max_direction_change and
              abs(dsi_previous - ship_directions) < 360-max_direction_change )):
            result = 10.0

    return result

def speed_continuity(vsi, vsi_previous, speeds, max_speed_change=10.0):
    '''
    Check if reported speed at this and previous time step is within max_speed_change 
    knots of calculated speed between those two time steps
    
    :param vsi: Reported speed in knots at current time step
    :param vsi_previous: Reported speed in knots at previous time step
    :param speeds: Speed of ship calculated from locations at current and previous time steps in km/hr
    :param max_speed_change: largest change of speed that will not raise flag, default 10
    :type vsi: float
    :type vsi_previous: float
    :type speeds: float
    :type max_speed_change: float
    
    :return: 10 if the reported and calculated speeds differ by more than 10 knots, 0 otherwise
    :rtype: float
    '''

    km_to_nm = 0.539957
    
    result = 0.0
    if vsi != None and vsi_previous != None and speeds != None:
        if (abs(vsi/km_to_nm          - speeds) > max_speed_change/km_to_nm and 
            abs(vsi_previous/km_to_nm - speeds) > max_speed_change/km_to_nm):
            result = 10.0
    
    return result

def check_distance_from_estimate(vsi, vsi_previous, 
                                 time_differences, 
                                 fwd_diff_from_estimated, 
                                 rev_diff_from_estimated):
    '''
    Check that distances from estimated positions (calculated forward 
    and backwards in time) are less than time difference multiplied by 
    the average reported speeds
    
    :param vsi: reported speed in knots at current time step
    :param vsi_previous: reported speed in knots at previous time step
    :param time_differences: calculated time differences between reports in hours
    :param fwd_diff_from_estimated: distance in km from estimated position, estimates made forward in time 
    :param rev_diff_from_estimated: distance in km from estimated position, estimates made backward in time
    :type vsi: float
    :type vsi_previous: float
    :type time_differences: float
    :type fwd_diff_from_estimated: float 
    :type rev_diff_from_estimated: float
    :return: 10 if estimated and reported positions differ by more than the reported 
             speed multiplied by the calculated time difference, 0 otherwise
    :rtype: float
    '''
# Quality-control by examining the distance between
# the calculated and reported second position.
    km_to_nm = 0.539957
    
    result = 0.0
    if vsi > 0 and vsi_previous > 0 and time_differences > 0:
        
        alwdis = time_differences * ((vsi + vsi_previous)/2.) / km_to_nm
        
        if (fwd_diff_from_estimated > alwdis and
            rev_diff_from_estimated > alwdis):
            
            result = 10.0

    return result

def mds_track_check(invoyage):

    '''
    Perform one pass of the track check
    
    :param invoyage: A list of :class:`.Voyage` that you want track checked
    :type invoyage: :class:`.Voyage`
    :return: list of QC flags 0 for pass and 1 for fail
    :rtype: integer
    
    This is an implementation of the MDS track check code 
    which was originally written in the 1990s. I don't know why this piece of 
    historic trivia so exercises my mind, but it does: the 1990s! I wish my code 
    would last so long.
    '''
    
    km_to_nm = 0.539957
    nobs = len(invoyage)

#no obs in, no qc outcomes out
    if nobs == 0:
        return []

#Generic ids get a free pass on the track check
    if qc.id_is_generic(invoyage.getvar(0, 'ID'), invoyage.getvar(0, 'YR')):
        qcs = []
        nobs = len(invoyage)
        for i in range(0, nobs):
            invoyage.set_qc(i, 'POS', 'bad_track', 0)
            qcs.append(0)
        return qcs

#fewer than three obs - set the fewsome flag
#deck 720 gets a pass prior to 1891 see Carella, Kent, Berry 2015 Appendix A3
    if nobs < 3 and not(invoyage.getvar(0, 'DCK') == 720 and invoyage.getvar(0 ,'YR') < 1891):
        qcs = []
        nobs = len(invoyage)
        for i in range(0, nobs):
            invoyage.set_qc(i, 'POS', 'fewsome_check', 1)
            qcs.append(0)
        return qcs

#work out speeds and distances between alternating points
    invoyage.calc_alternate_speeds()

#what are the mean and mode speeds?
    mean_speed = invoyage.meansp()
    modal_speed = modesp(invoyage.get_speed())
#set speed limits based on modal speed
    amax, amaxx, amin = set_speed_limits(modal_speed)

#compare reported speeds and positions if we have them
    forward_diff_from_estimated  = distr1(invoyage)
    reverse_diff_from_estimated  = distr2(invoyage)
    midpoint_diff_from_estimated =  midpt(invoyage)

#do QC
    qcs = [0]
    all_alwdis = [0]
    invoyage.set_qc(0, 'POS', 'bad_track', 0)
    invoyage.set_qc(0, 'POS', 'fewsome_check', 0)

    for i in range(1, nobs-1):
        
        thisqc_a = 0
        thisqc_b = 0

#together these cover the speeds calculate from point i        
        if   (invoyage.getvar(i, 'speed')       > amax and 
              invoyage.getvar(i-1 ,'alt_speed') > amax):
            thisqc_a += 1.00
        elif (invoyage.getvar(i+1, 'speed')     > amax and 
              invoyage.getvar(i+1, 'alt_speed') > amax):
            thisqc_a += 2.00
        elif (invoyage.getvar(i, 'speed')       > amax and 
              invoyage.getvar(i+1, 'speed')     > amax):
            thisqc_a += 3.00 

# Quality-control by examining the distance 
#between the calculated and reported second position.
        thisqc_b += check_distance_from_estimate(invoyage.getvar(i ,  'vsi'), 
                                                 invoyage.getvar(i-1, 'vsi'), 
                                                 invoyage.getvar(i,   'time_diff'), 
                                                 forward_diff_from_estimated[i],
                                                 reverse_diff_from_estimated[i])
#Check for continuity of direction                              
        thisqc_b += direction_continuity(invoyage.getvar(i,   'dsi'), 
                                         invoyage.getvar(i-1, 'dsi'), 
                                         invoyage.getvar(i,   'course'))
#Check for continuity of speed.                                 
        thisqc_b += speed_continuity(invoyage.getvar(i,   'vsi'), 
                                     invoyage.getvar(i-1, 'vsi'), 
                                     invoyage.getvar(i,   'speed'))

#check for speeds in excess of 40.00 knots
        if invoyage.getvar(i, 'speed') > 40.00/km_to_nm:
            thisqc_b += 10.0

#make the final decision
        if (midpoint_diff_from_estimated[i] > 150.0/km_to_nm and 
            thisqc_a > 0 and 
            thisqc_b > 0):
            qcs.append(1)
            invoyage.set_qc(i, 'POS', 'bad_track', 1)
            invoyage.set_qc(i, 'POS', 'fewsome_check', 0)
        else:
            qcs.append(0)
            invoyage.set_qc(i, 'POS', 'bad_track', 0)
            invoyage.set_qc(i, 'POS', 'fewsome_check', 0)

    qcs.append(0)
    invoyage.set_qc(nobs-1, 'POS', 'bad_track', 0)
    invoyage.set_qc(nobs-1, 'POS', 'fewsome_check', 0)

    return qcs

def mds_full_track_check(invoyage):
    '''
    Do the full 5-pass track check (which sounds like a kung-fu move requiring years 
    of dedication and eating nothing but rainwater, but is, in fact, just doing the 
    track check repeatedly)
    
    :param inreps: object :class:`.Voyage` to be track checked
    :type inreps: :class:`.Voyage`
    
    The basic 1-pass track check is repeated 5 times, with obs failing track check 
    excluded from subsequent passes.
    '''
    master_qc = mds_track_check(invoyage)
    
    repititions = 0
    
    qcs = master_qc
    
    if len(qcs) > 0:
        while max(qcs) > 0 and repititions < 4:
            tempreps = ex.Voyage()
            qc_refs = []

            i = 0
            for rep in invoyage.rep_feed():
                if master_qc[i] == 0:
                    tempreps.add_report(rep)
                    qc_refs.append(i)
                i += 1

            qcs = mds_track_check(tempreps)

            for i, qc_ref in enumerate(qc_refs):
                master_qc[qc_ref] = qcs[i]

            repititions += 1

    i=0
    for rep in invoyage.rep_feed():
        if master_qc[i] == 0:
            invoyage.set_qc(i, 'POS', 'bad_track', 0)
        if master_qc[i] == 1:
            invoyage.set_qc(i, 'POS', 'bad_track', 1)
        i += 1

    return invoyage
