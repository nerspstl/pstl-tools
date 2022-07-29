test = 'Hello'
#fname = "out.csv"
fname = "mip_daq_pressure.csv"
port = "COM5"
baudrate = 9600
#delay = 1.0
delay = None
header = ['time [secs]', 'voltage [V]']
channel = 2
card = 1
convert = True


# loc
if channel < 10:
    channel = '0'+str(channel)
else:
    channel = str(channel)
loc = str(card)+channel

# commad
# 1
cmd = "MEAS:VOLT:DC? (@%s)"%(loc)
