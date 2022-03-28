import dbus #pip install dbus-python
import re

class SystemdManager(object):

    UNIT_INTERFACE = "org.freedesktop.systemd1.Unit"
    SERVICE_UNIT_INTERFACE = "org.freedesktop.systemd1.Service"
    __bus=dbus.SystemBus()

    def __new__(cls):
        return cls
    
    @classmethod
    def Start(cls, unit_name, mode="replace"):
        interface = cls._get_interface()

        if interface is None:
            return False

        try:
            while cls.ActiveState(unit_name) == False:
                interface.StartUnit(unit_name, mode)
            return True
        except dbus.exceptions.DBusException as error:
            print(error)
            return False

    @classmethod
    def Stop(cls, unit_name, mode="replace"):
        interface = cls._get_interface()

        if interface is None:
            return False

        try:
            while cls.ActiveState(unit_name) == True:
                interface.StopUnit(unit_name, mode)
            return True
        except dbus.exceptions.DBusException as error:
            print(error)
            return False

    @classmethod
    def Restart(cls, unit_name, mode="replace"):
        interface = cls._get_interface()
        if interface is None:
            return False

        try:
            interface.RestartUnit(unit_name, mode)
            return True
        except dbus.exceptions.DBusException as error:
            print(error)
            return False

    @classmethod
    def Enable(cls, unit_name):
        interface = cls._get_interface()

        if interface is None:
            return False

        try:
            interface.EnableUnitFiles([unit_name],
                                      dbus.Boolean(False),
                                      dbus.Boolean(True))
            return True
        except dbus.exceptions.DBusException as error:
            print(error)
            return False

    @classmethod
    def Disable(cls, unit_name):
        interface = cls._get_interface()

        if interface is None:
            return False

        try:
            interface.DisableUnitFiles([unit_name], dbus.Boolean(False))
            return True
        except dbus.exceptions.DBusException as error:
            print(error)
            return False
    @classmethod
    def _get_unit_file_state(cls, unit_name):
        interface = cls._get_interface()

        if interface is None:
            return None

        try:
            state = interface.GetUnitFileState(unit_name)
            return state
        except dbus.exceptions.DBusException as error:
            print(error)
            return False
    @classmethod
    def _get_interface(cls):
        try:
            obj = cls.__bus.get_object("org.freedesktop.systemd1",
                                        "/org/freedesktop/systemd1")
            return dbus.Interface(obj, "org.freedesktop.systemd1.Manager")
        except dbus.exceptions.DBusException as error:
            print(error)
            return None
    @classmethod
    def get_active_state(cls, unit_name):
        properties = cls._get_unit_properties(unit_name, cls.UNIT_INTERFACE)

        if properties is None:
            return False

        try:
            state = properties["ActiveState"].encode("utf-8")
            return state
        except KeyError:
            return False

    @classmethod
    def _get_unit_properties(cls, unit_name, unit_interface):
        interface = cls._get_interface()

        if interface is None:
            return None

        try:
            unit_path = interface.LoadUnit(unit_name)

            obj = cls.__bus.get_object(
                "org.freedesktop.systemd1", unit_path)

            properties_interface = dbus.Interface(
                obj, "org.freedesktop.DBus.Properties")

            return properties_interface.GetAll(unit_interface)

        except dbus.exceptions.DBusException as error:
            print(error)
            return None
        
    @classmethod
    def ActiveState(cls, unit_name):
        unit_state = cls.get_active_state(unit_name)
        return unit_state == b"active"
    

            
            
        







