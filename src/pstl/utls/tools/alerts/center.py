import os.path
import json

from pstl import contacts
from pstl.contacts import individuals
from pstl.contacts import groups
from pstl.tools.alerts import send

cdir=os.path.dirname(contacts.__file__)
idir=os.path.dirname(individuals.__file__)
gdir=os.path.dirname(groups.__file__)

def get_json(filename,suffix=".json",wdir=cdir):
    try: 
        filepath=os.path.join(wdir,filename+suffix)
        with open(filepath) as f:
            data=json.load(f)
    except TypeError:
        print("%s was not inputted as a string"%(str(last)))
    return data


def get_individual(name,/,suffix=".json",wdir=idir):
    return get_json(name,suffix,wdir)

def get_group(name,/,suffix=".json",wdir=gdir):
    return get_json(name,suffix,wdir)

def test_if_known(i,what):
    if i is None or i == "" or i == "unknown"\
            or i == "Unknown" or i == "UNKNOWN":
                print("%s type is not known"%(what))
                return False
    else:
        return True

def method_all():
    return ['text','email','api']
    

def individual(name,method,/,suffix=".json",wdir=None):
    if wdir is None: wdir=idir
    if type(method) is list: pass
    else: method = [method]

    info=get_individual(name,suffix,wdir=wdir)
    try:
        #VIA=[]
        VIA={}
        if "all" in method or "All" in method or "ALL" in method:
            method = method_all()
        if "text" in method:
            if 'phone' in info:
                ip=info['phone']
                if 'number' in ip and 'service' in ip:
                    ips=ip['service']
                    if test_if_known(ips,'Service'):
                        # service data
                        sdata=get_json("sms")
                        if ips in sdata:
                            text_extention=sdata[ips]
                            #VIA.append({'text':ip['number']+text_extention})
                            VIA['text']=ip['number']+text_extention
                        else:
                            print("please update your sms.json file")
        if "email" in method:
            if 'email' in info:
                ie=info['email']
                if test_if_known(ie,'Email'):
                    #VIA.append({'email':ie})
                    VIA['email']=ie

        if "api" in method:
            if 'api' in info:
                ia=info['api']
                if test_if_known(ia,'Api'):
                    #VIA.append({'api':ia})
                    VIA['api']=ia
    except:
        print("error: '%s' could not be performed"%(str(method)))
        print("try: 'text', 'email' or 'api'")

    return {name:VIA}

def group(groupname,method,/,\
        groupsuffix=".json",individualsuffix=".json",\
        wdir=None,widir=None):
    if wdir is None: 
        wdir=gdir
    if widir is None:
        widir=idir
    if type(method) is list: pass
    else: method = [method]

    groupinfo=get_group(groupname,suffix=groupsuffix,wdir=wdir)
    PEOPLE={}
    try:
        if "all" in method or "All" in method or "ALL" in method:
            method = method_all()
        for name in groupinfo['people']:
            METHOD=[]
            for each in method:
                if each in groupinfo['people'][name]:
                    METHOD.append(each)
            person=individual(name,METHOD,suffix=individualsuffix,wdir=widir)
            PEOPLE[name]=person[name]
    except:
        print("Error: in contactGroup")

    return PEOPLE

def contact_individual(Sender,msg,name,method,/,subject=None,suffix=".json",wdir=None):
    """
    User is a class. either User class for text or email,
    or Api class for api
    """
    if wdir is None: wdir=idir
    if type(method) is list: pass
    else: method = [method]

    info=individual(name,method,suffix=suffix,wdir=wdir)
    for name in info:
        for via in info[name]:
            if via == 'text':
                # assign text function here
                func=send.text
            if via == 'email':
                # assign email function here
                func=send.email
            if via == 'api':
                # assign api function here
                func=send.api

            address=info[name][via]
            # call via function
            func(address,subject,msg,Sender)
            print(address)


def contact_group(Sender,msg,groupname,method,/,subject=None,\
        groupsuffix=".json",individualsuffix=".json",wdir=None,widir=None):
    if wdir is None:
        wdir=gdir
    if widir is None:
        widir=idir
    if type(method) is list: pass
    else: method = [method]

    groupinfo=group(groupname,method,\
            groupsuffix=groupsuffix,individualsuffix=individualsuffix,\
            wdir=wdir)
    for name in groupinfo:
        for via in groupinfo[name]:
            if via == 'text':
                # assign text function here
                func=send.text
            if via == 'email':
                # assign email function here
                func=send.email
            if via == 'api':
                # assign api function here
                func=send.api

            address=groupinfo[name][via]
            # call via function
            func(address,subject,msg,Sender)

def email_sender(name,/,suffix=".json",wdir=idir):
    info=get_json(name,suffix=suffix,wdir=wdir)
    if 'email' in info:
        user_email=info['email']
        if 'password' in info:
            if 'app' in info['password']:
                user_password=info['password']['app']
        if 'smtp' in info:
            user_smtp=info['smtp']
    return EMAIL(user_email,user_password,user_smtp)

def api_sender(app,msgtype,/,app_site=False,suffix=".json",wdir=idir):
    if app_site:
        pass
    else:
        info=get_json(app,suffix=suffix,wdir=wdir)
        if 'app' in info:
            app_site=info['app']
    return API(app_site,msgtype)

def sender(name=None,app=None,msgtype='info',/,suffix=".json",wdir=idir):
    if name is not None:
        Email=email_sender(name,suffix=suffix,wdir=wdir)
    else:
        Email=EMAIL(None,None,None,None,None)
    if app is not None:
        Api=api_sender(app,msgtype)
    else:
        Api=API(None,None)
    return SENDER(Email=Email,Api=Api)


class EMAIL():
    def __init__(self,address,password,smtp,port=587):
        self.address=address
        self.password=password
        self.smtp=smtp
        self.port=port

class API():
    def __init__(self,app,msgtype):
        self.app=app
        self.msgtype=msgtype

class SENDER():
    def __init__(self,/,Email=None,Api=None,\
            email=None,password=None,smtp=None,port=587,\
            app=None,msgtype=None):
        if Email is None:
            self.Email=EMAIL(email,password,smtp,port)
        else:
            self.Email=Email
        if Api is None:
            self.Api=API(app,msgtype)
        else:
            self.Api=Api
