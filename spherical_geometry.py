import numpy as np
import math

"""
The spherical geometry module is a simple collection of calculations on a sphere
Sourced from http://williams.best.vwh.net/avform.htm
"""
earths_radius = 6371.0088
radians_per_degree = np.pi / 180.


def sphere_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points on the sphere designated 
    by their latitude and longitude
    
    :param lat1: latitude of first point
    :param lon1: longitude of first point 
    :param lat2: latitude of second point
    :param lon2: longitude of second point 
    :type lat1: float
    :type lon1: float
    :type lat2: float
    :type lon2: float
    :return: return the great circle distance in kilometres between the two points
    :rtype: float
    
    The great circle distance is the shortest distance between any two points on the Earths surface. 
    The calculation is done by first calulating the angular distance between the points and then 
    multiplying that by the radius of the Earth. The angular distance calculation is handled by 
    another function.
    """

    delta = angular_distance(lat1, lon1, lat2, lon2) * earths_radius
    return delta


def angular_distance(lat1, lon1, lat2, lon2):
    """
    calculate distance between two points on a sphere
    input latitudes and longitudes should be in degrees
    output is in radians
    
    :param lat1: latitude of first point
    :param lon1: longitude of first point 
    :param lat2: latitude of second point
    :param lon2: longitude of second point 
    :type lat1: float
    :type lon1: float
    :type lat2: float
    :type lon2: float
    :return: return the angular great circle distance between the two points in radians
    :rtype: float
    """

    assert lat1 is not None and not (math.isnan(lat1))
    assert lon1 is not None and not (math.isnan(lon1))
    assert lat2 is not None and not (math.isnan(lat2))
    assert lon2 is not None and not (math.isnan(lon2))

    # convert degrees to radians
    lat1 = lat1 * radians_per_degree
    lon1 = lon1 * radians_per_degree
    lat2 = lat2 * radians_per_degree
    lon2 = lon2 * radians_per_degree

    delta_lambda = abs(lon1 - lon2)
    bit1 = (np.cos(lat2) * np.sin(delta_lambda))
    bit1 = bit1 * bit1
    bit2 = (np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(delta_lambda))
    bit2 = bit2 * bit2
    topbit = bit1 + bit2
    topbit = np.sqrt(topbit)
    bottombit = np.sin(lat1) * np.sin(lat2) + np.cos(lat1) * np.cos(lat2) * np.cos(delta_lambda)
    delta = np.arctan2(topbit, bottombit)

    return delta


def lat_lon_from_course_and_distance(lat1, lon1, tc, d):
    """
    calculate a latitude and longitude given a starting point, course (in radian) and 
    angular distance (also in radians) #http://williams.best.vwh.net/avform.htm#LL
    
    :param lat1: latitude of first point in degrees
    :param lon1: longitude of first point in degrees
    :param tc: true course measured clockwise from north in degrees
    :param d: distance travelled in kilometres
    :type lat1: float
    :type lon1: float
    :return: return the new latitude and longitude
    :rtype: float
    """

    lat1 = lat1 * radians_per_degree
    lon1 = lon1 * radians_per_degree
    tcr = tc * radians_per_degree

    dr = d / earths_radius

    lat = np.arcsin(np.sin(lat1) * np.cos(dr) + np.cos(lat1) * np.sin(dr) * np.cos(tcr))
    dlon = np.arctan2(np.sin(tcr) * np.sin(dr) * np.cos(lat1), np.cos(dr) - np.sin(lat1) * np.sin(lat))
    lon = math.fmod(lon1 + dlon + np.pi, 2. * np.pi) - np.pi

    lat = lat / radians_per_degree
    lon = lon / radians_per_degree

    return lat, lon


def course_between_points(lat1, lon1, lat2, lon2):
    """
    given two points find the initial true course at point1
    inputs are in degrees and output is in degrees
    
    :param lat1: latitude of first point in degrees
    :param lon1: longitude of first point in degrees
    :param lat2: latitude of second point in degrees
    :param lon2: longitude of second point in degrees
    :type lat1: float
    :type lon1: float
    :type lat2: float
    :type lon2: float
    :return: return the initial true course in degrees at point one along the great circle between point
        one and point two
    :rtype: float
    """

    d = angular_distance(lat1, lon1, lat2, lon2)

    if d != 0:

        lat1 = lat1 * radians_per_degree
        lon1 = lon1 * radians_per_degree
        lat2 = lat2 * radians_per_degree
        lon2 = lon2 * radians_per_degree

        if np.cos(lat1) < 0.0000001:
            if lat1 > 0:
                tc1 = np.pi
            else:
                tc1 = 2. * np.pi
        else:
            if np.sin(lon2 - lon1) > 0:
                if 1.0 >= (np.sin(lat2) - np.sin(lat1) * np.cos(d)) / (np.sin(d) * np.cos(lat1)) >= -1.0:
                    tc1 = np.arccos(
                        (np.sin(lat2) - np.sin(lat1) * np.cos(d)) /
                        (np.sin(d) * np.cos(lat1))
                    )
                else:
                    tc1 = float('nan')
            else:
                if 1.0 >= (np.sin(lat2) - np.sin(lat1) * np.cos(d)) / (np.sin(d) * np.cos(lat1)) >= -1.0:
                    tc1 = 2. * np.pi - np.arccos(
                        (np.sin(lat2) - np.sin(lat1) * np.cos(d)) /
                        (np.sin(d) * np.cos(lat1))
                    )
                else:
                    tc1 = float('nan')

        if math.isnan(tc1):
            tc1 = math.fmod(np.arctan2(np.sin(lon1 - lon2) * np.cos(lat2),
                                       np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(lon1 - lon2)),
                            2 * np.pi)

    else:

        tc1 = 0.0

    return tc1 / radians_per_degree


def intermediate_point(lat1, lon1, lat2, lon2, f):
    """
    given two lat,lon point find the latitude and longitude that are a fraction f
    of the great circle distance between them http://williams.best.vwh.net/avform.htm#Intermediate

    :param lat1: latitude of first point in degrees
    :param lon1: longitude of first point in degrees
    :param lat2: latitude of second point in degrees
    :param lon2: longitude of second point in degrees
    :param f: fraction of distance between the two points
    :type lat1: float
    :type lon1: float
    :type lat2: float
    :type lon2: float
    :type f: float
    :return: return the latitude and longitude of the point a fraction f along the great circle between the
        first and second points.
    :rtype: float
    """

    assert f <= 1.0, f

    d = angular_distance(lat1, lon1, lat2, lon2)

    if d != 0.0:
        # convert degrees to radians
        lat1 = lat1 * radians_per_degree
        lon1 = lon1 * radians_per_degree
        lat2 = lat2 * radians_per_degree
        lon2 = lon2 * radians_per_degree

        a = np.sin((1 - f) * d) / np.sin(d)
        b = np.sin(f * d) / np.sin(d)
        x = a * np.cos(lat1) * np.cos(lon1) + b * np.cos(lat2) * np.cos(lon2)
        y = a * np.cos(lat1) * np.sin(lon1) + b * np.cos(lat2) * np.sin(lon2)
        z = a * np.sin(lat1) + b * np.sin(lat2)
        lat = np.arctan2(z, np.sqrt(x * x + y * y)) / radians_per_degree
        lon = np.arctan2(y, x) / radians_per_degree
    else:
        lat = lat1
        lon = lon1

    return lat, lon
