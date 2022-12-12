import numpy as np


def do_nothing():
    pass

class Base():
    def __init__(self,
            send_alert=None,send_alert_fargs=None,
            sent_alerts=0,
            repeat=3,delays=[20,60],
            start_time=True,
            recover=False,send_alert_bool=False,
            **kwargs):
        # save values to self
        self.send_alert_bool=send_alert_bool
        self.sent_alerts=sent_alerts
        self.repeat=repeat
        self.delays=delays
        self.start_time=start_time
        self.recover=recover
        self.restarts=0

        # if send alert is None
        if send_alert is None:
            send_alert=do_nothing
        self.send_alert=send_alert
        if send_alert_fargs is None:
            send_alert_fargs=(None,)
        self.send_alert_fargs=send_alert_fargs


    def check(x):
        """
        actually checks if x is between lower and upper and
        returns True or False
        """
        # get bool if between
        OK=self._check(x)

        ## if now between 
        if all(ok is True for ok in OK):
            # check if send_alert_bool is true
            if self.send_alert_bool is True:
                ## DONOT send the alert here from self
                # just means it has been inbetween before
                # and is currently safe
                if self.recover is True and self.sent_alerts!=0:
                    # add count to number of times it restarts
                    # restarts is a running count since
                    # sent_alerts will be 
                    self.restarts+=1
                    self.sent_alerts=0
                elif self.recover is True:
                    # no alerts have been sent all good
                    pass
                elif self.recover is False:
                    # dont count recoveries
                    pass
                else:
                    raise ValueError("Unknown 'recover' %s"%(self.recover))
            elif self.send_alert_bool is False:
                ## first time its inbetween so reset send_alert_bool
                # but DONOT send alert
                self.send_alert_bool=True
            else:
                raise ValueError("Unknown 'send_alert_bool' %s"%(self.send_alert_bool))
        elif any(ok is False for ok in OK):
            # check if send_alert_bool is True
            if self.send_alert_bool is True:
                ## DO send the alert here from self
                # means it has been inbetween before
                # and is currently not

                ## see how many alerts have been sent
                if self.sent_alerts < self.repeat:
                    now=time.time()
                    if self.start_time is True:
                        self.start_time=now

                    # time since last alert
                    time_since_last=self.start_time-now

                    # check time delay
                    if time_since_last>=repeat[self.sent_alerts]:
                        ## send the alert
                        self.send_alert(x,*self.send_alert_fargs)   ### DEFINE THIS
                        self.sent_alerts+=1
                    else:
                        ## not enough time has passed since last alert
                        pass

            elif self.send_alert_bool is False:
                ## Has not made it for the first time
                # inbetween so just pass
                # but DONOT send alert
                pass
            else:
                raise ValueError("Unknown 'send_alert_bool' %s"%(self.send_alert_bool))
        else:
            raise ValueError("Unknown returned 'OK' %s"%(OK))


class Between(Base):
    def __init__(self,lower,upper,**kwargs):

        Base.__init__(self,**kwargs)

        self.lower=lower
        self.upper=upper

    def _check(self,X):
        """
        bool if x is between lower and upper and
        returns True or False
        """
        lower=self.lower
        upper=self.upper

        # check
        if isinstance(X,(list,tuple,np.ndarray)):
            ok=[None]*len(X)
            for i,x in enumerate(X):
                if x>=lower and x<=upper:
                    ok[i]=True
                else:
                    ok[i]=False
        else:
            if x>=lower and x<=upper:
                ok=[True]
            else:
                ok=[False]

        return ok


class Above(Base):
    def __init__(self,upper,**kwargs):

        Base.__init__(self,**kwargs)

        self.upper=upper

    def _check(self,x):
        """
        bool if x is less than the upper bound
        returns True or False
        """
        upper=self.upper

        # check
        if isinstance(X,(list,tuple,np.ndarray)):
            ok=[None]*len(X)
            for i,x in enumerate(X):
                if x<=upper:
                    ok[i]=True
                else:
                    ok[i]=False
        else:
            if x<=upper:
                ok=[True]
            else:
                ok=[False]

        return ok

class Below(Base):
    def __init__(self,lower,**kwargs):

        Base.__init__(self,**kwargs)

        self.lower=lower

    def _check(self,x):
        """
        bool if x is greater thand lower bound
        returns True or False
        """
        lower=self.lower

        # check
        if isinstance(X,(list,tuple,np.ndarray)):
            ok=[None]*len(X)
            for i,x in enumerate(X):
                if x>=lower:
                    ok[i]=True
                else:
                    ok[i]=False

        else:
            if x>=lower:
                ok=[True]
            else:
                ok=[False]

        return ok
