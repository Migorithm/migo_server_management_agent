import os
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import request,jsonify
from functools import wraps

class AgentUtils:
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
                            return func(*args,**kwagrs)
                        else:
                            print("Token not matched")
                            return "Failed", 400
                    except Exception as e:
                        print("BadSignature!")
                        print(e)
                        return "Failed",400   
                else:
                    print("Token not given!")
                    return "Failed",400
        return wrapper
        
            
                    

    
        
    
    