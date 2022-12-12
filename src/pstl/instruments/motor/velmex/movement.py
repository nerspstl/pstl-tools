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

    #init_str = 'F,C,' + 'I1M' + str(x_start) + ',IA1M-0' + ',I2M' + str(y_start) + ',IA2M-0' +',R

    #Switched to motor 3
    init_str = 'F,C,' + 'I3M' + str(x_start) + ',IA3M-0' + ',I2M' + str(y_start) + ',IA2M-0' +',R'
    instr.write(ascii_convert(init_str))  
    

def create_mov_list(x_sweeps,y_inc = 10,x_inc = 0):   

    y_inc = math.floor(y_inc/0.0025)
    x_inc = math.floor(x_inc/0.0025)

    #x_p = 'F,C,' + 'I1M' + str(x_inc) + ',R'
    #x_n = 'F,C,' + 'I1M-' + str(x_inc) + ',R'

    #Switched to motor 3
    x_p = 'F,C,' + 'I3M' + str(x_inc) + ',R'
    x_n = 'F,C,' + 'I3M-' + str(x_inc) + ',R'

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

    increment = len(mov_list)-1

    if take_data:

        for i in range(0,increment,2):

            check_if_ready(myInstr)
            check_pos(myInstr)
            print('Starting data collection...')
            print(mov_list[i])
            instr.write(ascii_convert(mov_list[i])) 

            check_if_ready(myInstr)
            check_pos(myInstr)
            print('Ending data collection...')
            print(mov_list[i+1])
            instr.write(ascii_convert(mov_list[i+1])) 

        check_if_ready(myInstr)
        check_pos(myInstr)
        print(mov_list[-1])
        instr.write(ascii_convert(mov_list[-1])) 
        check_if_ready(myInstr)
        check_pos(myInstr)

        print('Storing data...')        

def check_pos(instr):
    instr.write(ascii_convert('X'))
    print(instr.read_until(b'\r').decode())

    instr.write(ascii_convert('Y'))
    print(instr.read_until(b'\r').decode())

    #print(instr.read(1).decode())
    

#for lab computer:
#port = 'COM8'

port = '/dev/tty.usbserial-110'
num_x_sweeps = 5

myInstr = Instrument(port)

# Send initialization string to move to initial position and zero

#CODE
check_pos(myInstr)
initialize_position(myInstr)
print(check_if_ready(myInstr))
myInstr.write(ascii_convert('F,C,I1M4000,R'))
check_pos(myInstr)
mov_list = create_mov_list(num_x_sweeps)
print(mov_list)
move_and_collect_data(myInstr,mov_list) 


#Testing for video
#myInstr.write(ascii_convert('F,C,I3M4000,R'))
#print(check_if_ready(myInstr))
#check_pos(myInstr)
#myInstr.write(ascii_convert('F,C,I3M-4000,R'))
#print(check_if_ready(myInstr))
#check_pos(myInstr)
#myInstr.write(ascii_convert('F,C,I3M4000,R'))
#print(check_if_ready(myInstr))
#check_pos(myInstr)
#myInstr.write(ascii_convert('F,C,I3M-4000,R'))

#myInstr.write(ascii_convert('F,C,I1M4000,I1M-4000,I1M4000,I1M-4000,R'))
#myInstr.write(ascii_convert('F,C,I3M-4000,I3M4000,I3M-4000,I3M4000,I3M-4000,R'))


#kill(myInstr)

