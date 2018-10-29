import numpy as np
from netCDF4 import Dataset
import math
import qc

class Climatology():
    
    '''
    Class for dealing with climatologies, reading, extracting values etc. 
    Automatically detects if this is a single field, pentad or daily climatology
    '''
    
    def __init__(self, infield):
        '''
        Read in the climatology for variable var from infile
        
        :param infield: numpy array containing the climatology
        :type infield: numpy array
        '''
        self.field = infield
        self.n = self.field.shape[0]
        assert self.n in [1,73,365],'weird shaped field'
        self.res = 180./self.field.shape[1]

    @classmethod
    def from_filename(cls, infile, var):
        '''
        Read in the climatology for variable var from infile

        :param infile: filename of a netcdf file
        :param var: the variable name to be extracted from the netcdf file
        :type infile: string
        :type var: string
        '''
        if infile is not None:
            climatology = Dataset(infile)
            field = climatology.variables[var][:]
            climatology.close()

            if (field.shape[0] == 1 and 
                field.shape[1] == 360 and 
                field.shape[2] == 180):
                field = field.transpose(0,2,1)

            if field.ndim == 4:
                field = field[:,0,:,:]
        else:
            field = np.ma.array(np.zeros((1,180*20,360*20)), mask=True)

        return cls(field)

    def get_tindex(self, month, day):
        '''
        Get the time index of the input month and day
        
        :param month: month for which the time index is required
        :param day: day for which the time index is required
        :type month: integer
        :type day: integer
        :return: time index for specified month and day.
        :rtype: integer
        '''
        if self.n == 1:
            tindex = 0
        if self.n == 73:
            tindex = qc.which_pentad(month, day) - 1
        if self.n == 365:
            tindex = qc.day_in_year(month, day) - 1

        return tindex        

    def get_value_ostia(self, lat, lon):

        yindex = qc.mds_lat_to_yindex(lat, res=0.05)
        xindex = qc.mds_lon_to_xindex(lon, res=0.05)
        tindex = 0

        result = self.field[tindex, yindex, xindex]

        if type(result) is np.float64 or type(result) is np.float32:
            pass
        else:
            if result.mask:
                result = None
            else:
                result = result.data[0]

        return result
        

    def get_value_mds_style(self, lat, lon, month, day):
        '''
        Get the value from the climatology at the give position and time using the MDS 
        method for deciding which grid cell borderline cases fall into
        
        :param lat: latitude of location to extract value from in degrees
        :param lon: longitude of location to extract value from in degrees
        :param month: month for which the value is required
        :param day: day for which the value is required
        :type lat: float
        :type lon: float
        :type month: integer
        :type day: integer
        :return: climatology value at specified location and time.
        :rtype: float
        '''
        if month < 1 or month > 12:
            return None
        ml = qc.month_lengths(2004)
        if day < 1 or day > ml[month-1]:
            return None

        yindex = qc.mds_lat_to_yindex(lat)
        xindex = qc.mds_lon_to_xindex(lon)
        tindex = self.get_tindex(month, day)

        result = self.field[tindex, yindex, xindex]

        if type(result) is np.float64 or type(result) is np.float32:
            pass
        else:
            if result.mask:
                result = None
            else:
                result = result.data[0]

        return result

    def get_value(self, lat, lon, month, day):
        '''
        Get the value from the climatology at the give position and time
        
        :param lat: latitude of location to extract value from in degrees
        :param lon: longitude of location to extract value from in degrees
        :param month: month for which the value is required
        :param day: day for which the value is required
        :type lat: float
        :type lon: float
        :type month: integer
        :type day: integer
        :return: climatology value at specified location and time.
        :rtype: float
        '''
        if month < 1 or month > 12:
            return None
        ml = qc.month_lengths(2004)
        if day < 1 or day > ml[month-1]:
            return None

        yindex = qc.lat_to_yindex(lat, self.res)
        xindex = qc.lon_to_xindex(lon, self.res)
        tindex = self.get_tindex(month, day)

        result = self.field[tindex, yindex, xindex]

        if type(result) is np.float64 or type(result) is np.float32:
            pass
        else:
            if result.mask:
                result = None
            else:
                result = result.data[0]

        return result
    
    def get_interpolated_value(self, lat, lon, mo, dy):
        '''
        Get the value from the climatology interpolated to the precise location of 
        the observation in time and space
        
        :param lat: latitude of location to extract value from in degrees
        :param lon: longitude of location to extract value from in degrees
        :param month: month for which the value is required
        :param day: day for which the value is required
        :type lat: float
        :type lon: float
        :type month: integer
        :type day: integer
        :return: climatology value at specified location and time.
        :rtype: float
        '''
#check that the lat lon point falls in a grid cell with a value or on 
#the border of one        
        if lat+0.001 < 90:
            pert1 = self.get_value(lat+0.001, lon+0.001, mo, dy)
            pert2 = self.get_value(lat+0.001, lon-0.001, mo, dy)
        else:
            pert1 = None
            pert2 = None
        if lat-0.001 > -90:
            pert3 = self.get_value(lat-0.001, lon+0.001, mo, dy)
            pert4 = self.get_value(lat-0.001, lon-0.001, mo, dy)
        else:
            pert3 = None
            pert4 = None

        if (pert1 == None and pert2 == None and 
            pert3 == None and pert4 == None):
            return None
        
        x1, x2, y1, y2 = qc.get_four_surrounding_points(lat, lon, 1)   
    
        try:
            Q11 = self.get_value(y1, x1, mo, dy)
        except:
            Q11 = None
        if Q11 != None:
            Q11 = float(Q11)
    
        try:
            Q22 = self.get_value(y2, x2, mo, dy)
        except:
            Q22 = None
        if Q22 != None:
            Q22 = float(Q22)
    
        try:
            Q12 = self.get_value(y2, x1, mo, dy)
        except:
            Q12 = None
        if Q12 != None:
            Q12 = float(Q12)
    
        try:
            Q21 = self.get_value(y1, x2, mo, dy)
        except:
            Q21 = None
        if Q21 != None:
            Q21 = float(Q21)
    
        Q11,Q12,Q21,Q22 = qc.fill_missing_vals(Q11,Q12,Q21,Q22)
    
        x1, x2, y1, y2 = qc.get_four_surrounding_points(lat, lon, 0)   
    
        return qc.bilinear_interp(x1, x2, y1, y2,
                                  lon, lat,
                                  Q11, Q12, Q21, Q22)



