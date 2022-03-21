import os
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import request
from functools import wraps
import logging
import datetime

class AgentUtils:
    logging.basicConfig(filename="/var/log/vertica-agent/agent.log",level=logging.DEBUG)
    
    AGENT_KEY=os.getenv("AGENT_KEY")
    #Service loading
    def __new__(cls):
        return cls

    @classmethod
    def load_service(cls):
        from pystemd.systemd1 import Unit,manager
        import re
        mng = manager.Manager()
        mng.load()
        regex = re.compile(r"redis.*service|elastic.*service|kafka.*service")
        services= list(filter(lambda x: regex.match(x[0].decode('utf-8')), mng.Manager.ListUnits()))
        cls.services={}
        
        for service in services:
            serv = service[0].decode('utf-8')
            service_name= re.sub(r"[@.]",r"_",serv).upper() 
            unit=Unit(service[0].decode("utf-8"))
            unit.load()
            unit=unit.Unit
            setattr(AgentUtils,service_name,unit)
            #Put unit first so you can get the state of unit synchronously.
    @staticmethod
    def token_loader(token):
        serializer = Serializer(AgentUtils.AGENT_KEY)
        return serializer.loads(token.encode("utf-8"))
    
    @staticmethod
    def token_check(func):
        @wraps(func)
        def wrapper(*args,**kwagrs):
            #confirmation
            if request.method =="POST" : #request.remote_addr 
                #On the other side, it will post things in the following form
                #requests.post("http://nodeip:port/command/restart",json={"token":token})
                byte_token = request.get_json().get("token")
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
        
        
    
    