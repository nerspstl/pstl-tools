import serial
import os

def movement(port, string, func = None, fargs = None):
    myInstr = serial.Serial(port)

    mov_string = string.encode('ascii')
    myInstr.write(mov_string)

    #for s in string:
        #mov_string = s.encode('ascii')

    if func is not None:
        output = func(fargs)

        return output

def get_data(data_path):

    os.mkdir(data_path)

def create_mov_string(init_string,x_mov_len,y_mov_len,loop):   

    move_str = ''
    x_p = 'I1M' + str(x_mov_len)
    x_n = 'I1M-' + str(x_mov_len)
    y_n = 'I2M-' + str(y_mov_len)

    for i in range(loop):
        move_str = move_str +','+ x_p +','+ y_n +','+ x_n +','+ y_n

    return init_string + move_str + ',R'

def kill(port):    
    movement(port, 'K')

#comments should eventually be used, just don't want to get hooked up on string

# I1M-0 and I2MO are desired inital positions
# positive for I2 is away from the thruster
# positive for I1 is towards the wall

#mov_string = 'E,LMO,I1M-4000,I2M-2000,L-3,R'
#port = 'COM8'


port = '/dev/tty.usbserial-110'
move_string = create_mov_string('F,C,I2M0',8000,8000,1)

print(move_string)

#movement(port,'F,C,I1M-8000,R')
movement(port,move_string)

#movement(port,move_string)

#kill(port)