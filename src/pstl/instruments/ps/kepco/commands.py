def convert2hex(num,maximum,hexalen):
    """Converts decimal integer to hexadecimal and returns the last three
    numbers/letters in uppercase to be passed to kepco_BOP

    num and maximum must be int or floats

    returns a string of length 3 of corresponding hexadecimal format

    FFF/X = 4095/E = Emax/E
    where X is your desired value in hex
    FFF is max hex (4095)
    E is the desired value in decimal
    Emax is the max value in decimal

    X=INT(FFF*(E/Emax))

    Note: 4095 (decimal) == FFF (hex)
    """
    if not isinstance(num,(int,float)):
        error=("'num' variable '%s' is not an integer or float"%(str(num)))
        raise TypeError(error)
    if not isinstance(maximum,(int,float)):
        error=("'maximum' variable '%s' is not an integer or float"%(str(maximum)))
        raise TypeError(error)
    if not isinstance(hexalen,int):
        error=("'hexalen' variable '%s' is not an integer"%(str(hexalen)))
        raise TypeError(error)
    if num==0:
        hexa="0"
    else:
        hexamax=int(pow(16,hexalen)-1) 
        hexa=hex(int(hexamax/(maximum/num)))[2:].upper()
    hexa=extendHexa(hexa,hexalen)
    return hexa

def extendHexa(hexa,strlen):
    hexalen=len(hexa)
    while hexalen<strlen:
        hexa="0"+hexa
        hexalen=len(hexa)
    return hexa

def polarity(string):
    try:    # test if the input is string or number
        val=int(string)
    except: # not number, see if string
        if isinstance(string,str):
            if string=="+" or string=="positive" or string=="pos":
                val=1
            elif string=="-" or string=="negative" or string=="neg":
                val=-1
            else: # produces error
                val=string
        else:
            raise TypeError("Input was not of type int,float, or str"+\
                    "But of type %s"%(str(type(string))))
    finally:
        if val==-1:
            out=val
        elif val==1:
            out=val
        else:
            raise TypeError("'%s' cannot correlate to -1 or 1"%(str(string)))
    return out

