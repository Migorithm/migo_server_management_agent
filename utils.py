import os
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import request
from functools import wraps
import logging
import datetime
from .systemdmanager import SystemdManager
import re




class AgentUtils:
    logging.basicConfig(filename="/var/log/vertica-agent/agent.log",level=logging.DEBUG)
    
    AGENT_KEY=os.getenv("AGENT_KEY")
    #Service loading
    def __new__(cls):
        return cls
            
    #Automatic registration of services
    @classmethod
    def LoadService(cls):
        interface = SystemdManager._get_interface()
        regex = re.compile(r"redis.*service|elastic.*service|kafka.*service|vertica.*service")
        unitnames = [str(unit[0]) for unit in interface.ListUnits() if regex.match(unit[0])]
        
        for unit in unitnames:
            service_name = re.sub(r"[@.-]",r"_",unit).upper()
            sub_class = type(service_name,(object,),{
                #constructor
                "Restart": lambda mode="replace": SystemdManager.Restart(unit, mode=mode),
                "Start": lambda mode="replace": SystemdManager.Start(unit, mode=mode),
                "Stop": lambda mode="replace": SystemdManager.Stop(unit,mode=mode)})
            setattr(cls,service_name,sub_class)
    
            
    @staticmethod
    def token_loader(token:str):
        serializer = Serializer(AgentUtils.AGENT_KEY)
        return serializer.loads(token.encode("utf-8"))
    
    @staticmethod
    def token_check(func):
        """
        On the other side, it will post things in the following form
        requests.post(url,json={"token":token})
        
        If it's in transferring files, the token will be posted inside the files object
        request.post(url,files={"file1":open("file1_path","rb"),{"token":"tokens"}})
        """
        @wraps(func)
        def wrapper(*args,**kwagrs):
            #confirmation
            if request.method =="POST" : #request.remote_addr 
                byte_token=""
                if request.get_json():
                    byte_token = request.get_json().get("token")
                else:
                    byte_token = request.files.get("token").read().decode('utf-8') #supposed to be bytes type
                if byte_token:
                    try:
                        token= AgentUtils.token_loader(byte_token) #Error point
                        if token.get("confirm"):
                            AgentUtils.log("Token matched!")
                            return func(*args,**kwagrs)
                        else:
                            AgentUtils.error_log(400,"Token not matched")
                            return "Failed", 400
                    except Exception as e:
                        AgentUtils.error_log(400,"BadSignature!")
                        logging.exception("Bad Signature!")
                        return "Failed",400   
                else:
                    AgentUtils.error_log(400,"Token not given!")
                    print("Token not given!")
                    return "Failed",400
        return wrapper
    
    @staticmethod
    def log(message):
        dt= datetime.datetime.now()
        log_date=dt.strftime("%y%m%d_%H:%M:%S")
        log_message = f"{log_date}: [{message}]"
        logging.info(log_message)
    
    @staticmethod
    def error_log(error_code,error_message):
        dt= datetime.datetime.now()
        log_date=dt.strftime("%y%m%d_%H:%M:%S")
        log_message= f"{log_date}: [{error_code}] [{error_message}]"
        logging.error(log_message)
            
    
    @staticmethod
    def redis_config(port):
        filepath= f"/etc/redis/redis_{port}.conf"
        if os.path.isfile(filepath):
            with open(filepath) as handle:
                for line in handle:
                    if line != "\n" and not line.startswith("#"):
                        key,value = line.lstrip().split(" ",1)
                        value = value.replace("\n","")
                        yield key,value
    
    
        
    
    