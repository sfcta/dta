__copyright__   = "Copyright 2011 SFCTA"
__license__     = ""
    


import dta
import datetime

        

if __name__ == '__main__':
    
    dta.setupLogging("dtaInfo.log", "dtaDebug.log", logToConsole=True)
    
    # The Geary network was created in an earlier Phase of work, so it already exists as
    # a Dynameq DTA network.  Initialize it from the Dynameq text files.
    gearyscenario = dta.DynameqScenario(dir="C:\Documents and Settings\Varun\Desktop\GIT\dtaFILES", file_prefix="Base_Final")
    gearyscenario.write(dir="C:\Documents and Settings\Varun\Desktop\GIT\dtaFILES", file_prefix="geary_")
    
    gearynet_dta = dta.DynameqNetwork(scenario=gearyscenario)
    gearynet_dta.read(dir="C:\Documents and Settings\Varun\Desktop\GIT\dtaFILES", file_prefix="Base_Final")
    
    #attach counts ?!
    starttime = datetime.time(15,00)
    period = datetime.timedelta(minutes = 15)
    
    number = 12
    tolerance = 5 #feet
    
    CD = dta.CountDracula("172.30.1.120","countdracula", "cdreader", "ReadOnly")
    
    gearynet_dta.retrieveCountListFromCountDracula(CD, starttime, period, number, tolerance)
    
    
    gearynet_dta.writeCountListToFile(dir="C:\Documents and Settings\Varun\Desktop\GIT\dtaFILES")
    
    
    