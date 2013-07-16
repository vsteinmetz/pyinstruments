"""
Provides factory function to work with IVI drivers using Dotnet
"""

COMMUNICATION_OK = False
import sys, os

sys.path.append(os.path.split(__file__)[0])
sys.path.append(os.environ["IVIROOTDIR32"] + \
                "/Bin/Primary Interop Assemblies")

def get_via_dotnet():
    """get factory functions via dotnet"""
    clr.AddReference("Ivi.SessionFactory.Interop")
    clr.AddReference("Ivi.ConfigServer.Interop")
    from Ivi.SessionFactory.Interop import IviSessionFactory
    from Ivi.ConfigServer.Interop import IviConfigStore
    from Ivi.ConfigServer.Interop import IviDriverSession
    from Ivi.ConfigServer.Interop import IviLogicalName

    return (IviSessionFactory, \
            IviConfigStore, \
            IviDriverSession, \
            IviLogicalName)
    
try:
    import clr
    clr.AddReference("Ivi.SessionFactory.Interop")
except Exception as e:
    print "pythondotnet seems not to be installed, you wont be able to use \
    those drivers ..."
else:
    COMMUNICATION_OK = True
    
    (get_session_factory, \
     get_config_store, \
     get_ivi_driver_session, \
     get_ivi_logical_name) = get_via_dotnet()
     
     