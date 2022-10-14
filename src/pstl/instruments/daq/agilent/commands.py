def cmdGetVoltageDC(loc):
    return "MEAS:VOLT:DC? (@%s)"%(loc)

def cmdGetVoltageAC(loc):
    return "MEAS:VOLT:AC? (@%s)"%(loc)

def cmdGetTemperatureTCK(loc):
    return "MEAS:TEMP? TC,K,(@%s)"%(loc)

def cmdGetResistance(loc):
    return "MEAS:RES? (@%s)"%(loc)
