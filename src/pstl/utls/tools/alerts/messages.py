from pstl.tools.alerts import notification

class MESSAGE():
    def __init__(self,/,subject=None,body=None,msg_type="info"):
        self.subject=subject
        self.body=body
        self.msg_type=msg_type

    def send(self,to:str,sender):

