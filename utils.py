import os
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


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
            setattr(Config,service_name,unit)
            #Put unit first so you can get the state of unit synchronously.
    
    @staticmethod
    def token_loader(token):
        serializer = Serializer(Config.AGENT_KEY)
        return serializer.loads(token.encode("utf-8"))
            
    

        
                

    
        
    
    