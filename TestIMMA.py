
def trint(inthing):
    try:
        outhing = int(inthing)
    except:
        outhing = None
    return outhing

def trfloat(inthing, scale):
    try:
        outhing = float(inthing) * scale
    except:
        outhing = None
    return outhing


class IMMA:

    def __init__(self):          # Standard instance object
        self.data = {}           # Dictionary to hold the parameter values
    

    def readstr(self,line):

        self.data['ID'] = line[0]
        self.data['UID'] = line[1]
        self.data['LAT'] = float(line[2])
        self.data['LON'] = float(line[3])
        self.data['YR'] = int(float(line[4]))
        self.data['MO'] = int(float(line[5]))
        self.data['DY'] = int(float(line[6]))
        self.data['HR'] = float(float(line[7]))
        if self.data['HR'] == -32768.:
            self.data['HR'] = None

        self.data['SST'] = float(float(line[11]))
        if self.data['SST'] == -32768.:
            self.data['SST'] = None
        self.data['DCK'] = 999