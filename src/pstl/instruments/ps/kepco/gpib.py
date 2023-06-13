from pstl.utls.protocol.gpib.pyvisa import Open
from pstl.instruments.ps.kepco import commands as cmds

class BOP(Open):
    """
    class for kepco bipolar operational DC power supply using ieee 488B gpib

    setCurrent() function has not been tested
    """
    def __init__(self,port=None,**kwargs):

        Open.__init__(self,port)

        self.ieee=kwargs.get("ieee","")
        self.class_name=kwargs.get('class_name','kepco_BOP')
        self.name=kwargs.get('name',self.class_name)
        self.type="ps"
        self.vmax=kwargs.get('vmax',None)
        if self.vmax is None: 
            self.vmax=float(input("Please enter max voltage [V]"))
        self.imax=kwargs.get('imax',None)
        if self.imax is None:
            self.imax=float(input("Please enter max current [A]"))

class BOP_100_1M(BOP):
    """
    Builds off the BOP class adds vmax=100 [V] and imax=1 [A]
    """
    def __init__(self,port=None,**kwargs):

        kwargs['class_name']=kwargs.get('class_name','kepco_BOP_100_1M')
        kwargs['name']=kwargs.get('name',kwargs['class_name'])
        kwargs['vmax']=100;kwargs['imax']=1
        BOP.__init__(self,port,**kwargs)

class BOP_100_1M_488B(BOP_100_1M):
    """
    Builds off the BOP_100_1M class adds ieee=488B
    """
    def __init__(self,port=None,**kwargs):

        kwargs['class_name']=kwargs.get('class_name','kepco_BOP_100_1M_488B')
        kwargs['name']=kwargs.get('name',kwargs['class_name'])
        kwargs['ieee']='488B'
        BOP_100_1M.__init__(self,port,**kwargs)

        self.vhexalen=kwargs.get('vhexalen',3)
        self.ihexalen=kwargs.get('ihexalen',2)
        self.vmaxhexa=self.getHex(self.vmax,self.vmax,self.vhexalen)
        self.imaxhexa=self.getHex(self.imax,self.imax,self.ihexalen)
        

    def getHex(self,num,maximum,hexalen):
        return cmds.convert2hex(num,maximum,hexalen)

    def getCMDVoltage(self,voltage,polarity,**kwargs):

        vmax=kwargs.get("vmax",self.vmax)
        vhexalen=kwargs.get("vhexalen",self.vhexalen)
        imax=kwargs.get("imax",self.imax)
        ihexalen=kwargs.get("ihexalen",self.ihexalen)
        
        LOWER=False
        if voltage <= .1*vmax:
            vmax=vmax/10
            LOWER=True

        hexaVoltage=self.getHex(voltage,vmax,vhexalen)
        hexaCurrent=self.getHex(imax,imax,ihexalen)
        polarity=cmds.polarity(polarity)
        if polarity==1:
            if LOWER:
                hexaPolarity="2"
            else:
                hexaPolarity="0"
        elif polarity==-1:
            if LOWER:
                hexaPolarity="3"
            else:
                hexaPolarity="1"
        else:
            raise NotImplementedError("Unknown %s"%(str(polarity)))
        cmd=hexaPolarity+hexaVoltage+hexaCurrent
        return cmd

    def setVoltage(self,voltage,**kwargs):
        polarity=kwargs.get('polarity',None)
        if polarity is None: 
            if voltage>=0: 
                polarity=1 
            else: 
                polarity=-1
                voltage=abs(voltage)
        self.write(self.getCMDVoltage(float(voltage),polarity,**kwargs))

    def getCMDCurrent(self,current,polarity,**kwargs):

        vmax=kwargs.get("vmax",self.vmax)
        vhexalen=kwargs.get("vhexalen",self.vhexalen)
        imax=kwargs.get("imax",self.imax)
        ihexalen=kwargs.get("ihexalen",self.ihexalen)
        
        LOWER=False
        if current <= .1*imax:
            imax=imax/10
            LOWER=True

        hexaVoltage=self.getHex(vmax,vmax,vhexalen)
        hexaCurrent=self.getHex(current,imax,ihexalen)
        polarity=cmds.polarity(polarity)
        if polarity==1:
            if LOWER:
                hexaPolarity="6"
            else:
                hexaPolarity="4"
        elif polarity==-1:
            if LOWER:
                hexaPolarity="7"
            else:
                hexaPolarity="5"
        else:
            raise NotImplementedError("Unknown %s"%(str(polarity)))
        cmd=hexaPolarity+hexaVoltage+hexaCurrent
        return cmd

    def setCurrent(self,current,**kwargs):
        polarity=kwargs.get('polarity',None)
        if polarity is None: 
            if current>=0: 
                polarity=1 
            else: 
                polarity=-1
                current=abs(current)
        self.write(self.getCMDCurrent(float(current),polarity,**kwargs))
