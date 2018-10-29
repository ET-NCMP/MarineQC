import dateutil.parser

class NRT:
  
    '''
    A class for reading and writing CMEMS NRT data from NetCDF files and 
    outputting data in the IMMA like format used by marine QC
    '''
  
    def __init__(self):
        self.data = {}           # Dictionary to hold the parameter values
        self.data['ID'] = None

    def __getitem__(self, key): return self.data[key]
    def __setitem__(self, key, item): self.data[key] = item

    def readstr(self,line):
        '''
        Read in a record from a file
        
        :param fh: file handle
        :type fh: file handle
        '''
        
        if(line == ""): return   # EOF
        line=line.rstrip("\n")       # Remove trailing newline
        
        id,dud,isodate,lat,lon,sst = line.split(",")
        
        date = dateutil.parser.parse(isodate)

#bad data fixes. not necessary any more as these are fixed in file pre-processing
        lat = float(lat)
        if lat > 200: lat = 200.
        lon = float(lon)
        if lon > 400: lon = 400.
        if sst == 'nan':
            sst= None
        else:
            sst = float(sst)
        
        self.data['UID'] = 'NRT'+id+isodate
        self.data['ID'] = id
        self.data['YR'] = date.year
        self.data['MO'] = date.month
        self.data['DY'] = date.day
        self.data['HR'] = date.hour + date.minute/60.
        self.data['LAT'] = lat
        self.data['LON'] = lon
        self.data['SST'] = sst
        self.data['AT'] = None
        self.data['DCK'] = 9999
        self.data['PT'] = 7
#dummy values for QC checks        
        self.data['SIM'] = None
        self.data['DS'] = None
        self.data['VS'] = None
        self.data['DPT'] = None
        self.data['SID'] = 9999
        self.data['C1'] = None
        self.data['SI'] = None

        
        
        
        
        
        
        
        
        
        
        
        
        
        