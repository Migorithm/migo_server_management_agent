
from systemdmanager import SystemdManager


class age:
  
    def __new__(cls):
        return cls
    
    @classmethod
    def LoadService(cls):
        interface = SystemdManager._get_interface()
        regex = re.compile(r"redis.*service|elastic.*service|kafka.*service|vertica.*service")
        unitnames = [str(unit[0]) for unit in interface.ListUnits() if regex.match(unit[0])]
        
        for unit in unitnames:
            service_name = re.sub(r"[@.-]",r"_",unit).upper()
            class kls:
                @staticmethod
                def Restart(unit=unit,mode=b"replace"):
                    res = SystemdManager.Restart(unit,mode)
                    return res
                @staticmethod
                def Start(unit=unit,mode=b"replace"):
                    res = SystemdManager.Start(unit,mode)
                    return res
                @staticmethod
                def Stop(unit=unit,mode=b"replace"):
                    res = SystemdManager.Stop(unit,mode)
                    return res
            setattr(cls,service_name,kls)
    
    
    #Automatic registration of services
    # @classmethod
    # def LoadService(cls):
    #     interface = SystemdManager._get_interface()
    #     regex = re.compile(r"redis.*service|elastic.*service|kafka.*service|vertica.*service")
    #     unitnames = [str(unit[0]) for unit in interface.ListUnits() if regex.match(unit[0])]
        
    #     for unit in unitnames:
    #         service_name = re.sub(r"[@.-]",r"_",unit).upper()
    #         class kls:
    #             @staticmethod
    #             def Restart(unit=unit,mode=b"replace"):
    #                 SystemdManager.Restart(unit,mode)
    #                 return True
    #             @staticmethod
    #             def Start(unit=unit,mode=b"replace"):
    #                 SystemdManager.Start(unit,mode)
    #                 return True
    #             @staticmethod
    #             def Stop(unit=unit,mode=b"replace"):
    #                 SystemdManager.Stop(unit,mode)
    #                 return True
    #         setattr(cls,service_name,kls)
      

    