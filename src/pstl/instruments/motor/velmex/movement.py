import serial
import math

#def movement(port, string, func = None, fargs = None):
#    myInstr = serial.Serial(port)
#
#    mov_string = string.encode('ascii')
#    myInstr.write(mov_string)
#
#    #output = myInstr.read_until(b'\r')
#    #print(output.decode())
#
#    if func is not None:
#        output = func(fargs)
#
#        return output

# I1M-0 and I2M-O are desired inital positions
# positive for I2 is away from the thruster
# positive for I1 is towards the wall


# start data, run x, stop data, run y
# start data, run x, stop data, run y...
# data collection
# add a time delay???, add in a busy request
# repeat every .1 seconds
# start data collection right before movement start
# how to end data collection right 
# then store matrix?? or get at very end??

# input port, number of x_sweeps
# optional inputs y_start, y_increment, x_start, x_increments

# send initialization string to turn on and move to initial position
# create a string for every x and y move
# interspace start and stop data commands 
#      check if still moving before doing anything like this
# store data collection


#-------------#
class Instrument:
    def __init__(self, port):
        self.port = port
        self.instr = serial.Serial(port)

        self.write = self.instr.write
        self.read = self.instr.read
        self.read_until = self.instr.read_until

def kill(instr):    
    instr.write(ascii_convert('K'))

def ascii_convert(string):
    return string.encode('ascii')

def check_if_ready(instr):

    while True:

        instr.write(ascii_convert('V'))
        output = instr.read(1).decode()

        if output == 'R':
            break
        elif output == 'B' or output == '^':    
            pass   
        else:
            raise ValueError("Unexpected '%s' while checking if ready"%(output))  

    return True              

def initialize_position(instr,y_start = '-0',x_start = '-0'):  

    init_str = 'F,C,' + 'I1M' + str(x_start) + ',IA1M-0' + ',I2M' + str(y_start) + ',IA2M-0' +',R'
    instr.write(ascii_convert(init_str))  
    

def create_mov_list(x_sweeps,y_inc = 10,x_inc = 0):   

    y_inc = math.floor(y_inc/0.0025)
    x_inc = math.floor(x_inc/0.0025)

    x_p = 'F,C,' + 'I1M' + str(x_inc) + ',R'
    x_n = 'F,C,' + 'I1M-' + str(x_inc) + ',R'
    y_p = 'F,C,' + 'I2M' + str(y_inc) + ',R'

    move_list = [x_p]
    neg_int = -1

    increment = x_sweeps-1

    for i in range(increment):
        if neg_int < 0:
            move_list.append(y_p)
            move_list.append(x_n)
        else:  
            move_list.append(y_p)
            move_list.append(x_p)  

        neg_int*= -1

    return move_list         

def move_and_collect_data(instr,mov_list,take_data=True):

    increment = math.floor(len(mov_list)/2)+1

    if take_data:

        for i in range(0,increment,2):

            check_if_ready(myInstr)
            print('Starting data collection...')
            print(mov_list[i])
            instr.write(ascii_convert(mov_list[i])) 

            check_if_ready(myInstr)
            print('Ending data collection...')
            print(mov_list[i+1])
            instr.write(ascii_convert(mov_list[i+1])) 

        check_if_ready(myInstr)
        print('Storing data...')        

def check_x_pos(instr):
    instr.write(ascii_convert('?'))
    #print(instr.read_until(b'\r').decode())
    print(instr.read(1).decode())
    

#for lab computer:
#port = 'COM8'

port = '/dev/tty.usbserial-110'
num_x_sweeps = 3

myInstr = Instrument(port)

# Send initialization string to move to initial position and zero

#CODE
#initialize_position(myInstr)
#mov_list = create_mov_list(num_x_sweeps)
#move_and_collect_data(myInstr,mov_list) 



#TESTING
#myInstr.write(ascii_convert('F,C,I1M-0,R'))
#print(check_if_ready(myInstr))
#check_x_pos(myInstr)
#
#myInstr.write(ascii_convert('F,C,IA1M-0,R'))
#print(check_if_ready(myInstr))
#check_x_pos(myInstr)
#
#myInstr.write(ascii_convert('F,C,IA1M40000,R'))
#print(check_if_ready(myInstr))
#check_x_pos(myInstr)
#myInstr.write(ascii_convert('F,C,I1M-4000,R'))
#print(check_if_ready(myInstr))
#check_x_pos(myInstr)

check_x_pos(myInstr)

#kill(myInstr)

