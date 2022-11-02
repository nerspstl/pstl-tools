import serial
import math

def movement(port, string, func = None, fargs = None):
    myInstr = serial.Serial(port)

    mov_string = string.encode('ascii')
    myInstr.write(mov_string)
    #output = myInstr.read_until(b'\r')
    #print(output.decode())

    if func is not None:
        output = func(fargs)

        return output


def create_mov_string(x_sweeps,y_start = '-0',y_inc = 10,x_start = '-0',x_inc = 0):   

    init_str = 'I1M' + str(x_start) + ',I2M' + str(y_start)

    y_inc = math.floor(y_inc/0.0025)
    x_inc = math.floor(x_inc/0.0025)

    x_p = 'I1M' + str(x_inc)
    x_n = 'I1M-' + str(x_inc)
    y_p = 'I2M' + str(y_inc)

    move_str = ',' + x_p
    neg_int = -1

    increment = x_sweeps-1

    for i in range(increment):
        #move_str = move_str +','+ x_p +','+ y_p +','+ x_n 
        if neg_int < 0:
            move_str = move_str + ',' + y_p +','+ x_n
        else:    
            move_str = move_str + ',' + y_p +','+ x_p

        neg_int*= -1
        #if i < math.ceil(increment/2)-1:
        #    move_str = move_str +','+ y_p

    return 'F,C,' + init_str + move_str + ',R'
    #return 'F,C,' + init_str  + ',R'

def kill(port):    
    movement(port, 'K')

# I1M-0 and I2M-O are desired inital positions
# positive for I2 is away from the thruster
# positive for I1 is towards the wall

#for lab computer:
#port = 'COM8'
port = '/dev/tty.usbserial-110'

move_string = create_mov_string(3)
print(move_string)

movement(port,move_string)
#movement(port,'F,C,IA1M0,I1M0,I1M-0,R')
#movement(port,'F,C,I2M4000,X,I2M-4000,R')

#kill(port)



# start data, run x, stop data, run y
# start data, run x, stop data, run y...
# data collection
# add a time delay???, add in a busy request
# repeat every .1 seconds
# start data collection right before movement start
# how to end data collection right 
# then store matrix?? or get at very end??

