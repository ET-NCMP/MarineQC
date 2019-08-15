def trint(inthing):
    """
    Turn something input into an integer if that is possible, otherwise return None

    :param inthing:
    :return: integer or None
    """
    try:
        outhing = int(inthing)
    except:
        outhing = None
    return outhing


def trfloat(inthing, scale):
    """
    Turn something into a float if that is possible, otherwise return None

    :param inthing: thing to be converted
    :param scale: number to scale input by after conversion to float
    :return: float or None
    """
    try:
        outhing = float(inthing) * scale
    except:
        outhing = None
    return outhing


class IMMA:

    def __init__(self):  # Standard instance object
        self.data = {}  # Dictionary to hold the parameter values

    def readstr(self, line):
        line = line.rstrip("\n")
        self.data['YR'] = trint(line[0:4])
        self.data['MO'] = trint(line[4:6])
        self.data['DY'] = trint(line[6:8])
        self.data['HR'] = trfloat(line[8:12], 0.01)
        self.data['LAT'] = trfloat(line[12:17], 0.01)
        self.data['LON'] = trfloat(line[17:23], 0.01)

        self.data['DS'] = trint(line[23:24])
        self.data['VS'] = trint(line[24:25])

        self.data['ID'] = line[25:34]

        self.data['AT'] = trfloat(line[34:38], 0.1)

        self.data['SST'] = trfloat(line[38:42], 0.1)

        self.data['DPT'] = trfloat(line[42:46], 0.1)

        self.data['DCK'] = trint(line[46:49])  # +3
        self.data['SID'] = trint(line[49:52])  # 3
        self.data['PT'] = trint(line[52:54])  # 2

        self.data['UID'] = line[54:60]  # +8
