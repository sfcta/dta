__copyright__   = "Copyright 2011 SFCTA"
__license__     = """
    This file is part of DTA.

    DTA is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    DTA is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with DTA.  If not, see <http://www.gnu.org/licenses/>.
"""

USAGE = r"""

 USAGE
 python visualizeDTAResults.py INPUT_DYNAMEQ_NET_DIR 
                               INPUT_DYNAMEQ_NET_PREFIX 
                               REPORTING_TIME_STEP
                               LINK_OUT_FILE 
                               MOVEMENT_OUT_FILE 
                               LINK_COUNT_FILE_15MIN 
                               MOVEMENT_COUNT_FILE_15MIN 
                               MOVEMENT_COUNT_FILE_5MIN 
 
 e.g.
 
 python visualizeDTAResults.py X:/Projects/ModelDev/dtaAnyway/validation2010.1/Reports/Scenarios/sf_jun8_420p/export 
                               sf_jun8_420p 
                               15
                               sf_jun8_420p_link15min.csv 
                               sf_jun8_420p_movement15min.csv 
                               X:/Projects/ModelDev/dtaAnyway/validation2010.1/input/ 
                               counts_links_15min_1600_1830.dat 
                               counts_movements_15min_1600_1830.dat 
                               counts_movements_5min_1600_1800.dat
 

 Creates reports from Dynameq output.  Currently, this includes:
   - Printing a CSV file with a comparison of Dynameq movements versus counts. 
 
 Before running this script, you must export the loaded Dynameq network by going to 
 Network->Export->Dynameq Network.
"""


import sys
import dta
from dta.Logger import DtaLogger
from dta.Utils import Time

if __name__ == "__main__":
    
    if len(sys.argv) != 10:
        print USAGE
        sys.exit(2)

    INPUT_DYNAMEQ_NET_DIR                = sys.argv[1]
    INPUT_DYNAMEQ_NET_PREFIX             = sys.argv[2]
    REPORTING_TIME_STEP                  = sys.argv[3]
    LINK_OUT_FILE                        = sys.argv[4]
    MOVEMENT_OUT_FILE                    = sys.argv[5]
    COUNT_DIR                            = sys.argv[6]  
    LINK_COUNT_FILE_15MIN                = sys.argv[7] 
    MOVEMENT_COUNT_FILE_15MIN            = sys.argv[8]
    MOVEMENT_COUNT_FILE_5MIN             = sys.argv[9]  
        
    
    # The SanFrancisco network will use feet for vehicle lengths and coordinates, and miles for link lengths
    dta.VehicleType.LENGTH_UNITS= "feet"
    dta.Node.COORDINATE_UNITS   = "feet"
    dta.RoadLink.LENGTH_UNITS   = "miles"

    dta.setupLogging("visualizeDTAResults.INFO.log", "visualizeDTAResults.DEBUG.log", logToConsole=True)

    scenario = dta.DynameqScenario(dta.Time(0,0), dta.Time(23,0))
    scenario.read(INPUT_DYNAMEQ_NET_DIR, INPUT_DYNAMEQ_NET_PREFIX) 
    net = dta.DynameqNetwork(scenario)

    net.read(INPUT_DYNAMEQ_NET_DIR, INPUT_DYNAMEQ_NET_PREFIX)
    
    simStartTime = 15 * 60 + 30
    simEndTime = 21 * 60 + 30
    simTimeStep = 5
    reportingTimeStep = int(REPORTING_TIME_STEP)
    net.readSimResults(simStartTime, simEndTime, 5)
    
#    DtaLogger.info("Reading 15-minute link counts")
#    net.readObsLinkCounts(COUNT_DIR + "/" + LINK_COUNT_FILE_15MIN)
#    DtaLogger.info("Reading 15-minute movement counts")
#    net.readObsMovementCounts(COUNT_DIR + "/" + MOVEMENT_COUNT_FILE_15MIN)
    DtaLogger.info("Reading 5-minute movement counts")
    net.readObsMovementCounts(COUNT_DIR + "/" + MOVEMENT_COUNT_FILE_5MIN)

        # print 15-minute link counts           
    DtaLogger.info("Writing %d-minute link counts" % reportingTimeStep)
        
    # start with the header
    outputStream = open(LINK_OUT_FILE, "w") 
    outputStream.write("LinkID,Label,FacilityType,FreeflowSpeed,NumLanes,StartTime,EndTime,CountVolume,ModelVolume\n")
        
    # now loop through all links that have a count    
    for link in net.iterRoadLinks():     
        if not (link.hasCountInfo() or link.hasMovementCountInfo()):
            continue
          
        # writes once every specified interval minutes interval, aggregating  to specified min intervals   
        for sTime in range(simStartTime, simEndTime-1, reportingTimeStep):
            if sTime + reportingTimeStep >= simEndTime:
                continue

            # first try writing any link counts
            if link.hasObsCount(sTime, sTime + reportingTimeStep):   
                outputStream.write("%d," % link.getId())
                outputStream.write("%s," % link.getLabel())
                outputStream.write("%d," % link.getFacilityType())
                outputStream.write("%d," % link.getFreeFlowSpeedInMPH())
                outputStream.write("%d," % link.getNumLanes())
                outputStream.write("%s," % Time.fromMinutes(sTime))
                outputStream.write("%s," % Time.fromMinutes(sTime + reportingTimeStep))
                outputStream.write("%d," % link.getObsCount(sTime, sTime + reportingTimeStep))         
                outputStream.write("%d\n" % link.getSimOutVolume(sTime, sTime + reportingTimeStep))
            # then try summing the movement counts
            elif link.hasAllMovementCounts(sTime, sTime + reportingTimeStep): 
                outputStream.write("%d," % link.getId())
                outputStream.write("%s," % link.getLabel())
                outputStream.write("%d," % link.getFacilityType())
                outputStream.write("%d," % link.getFreeFlowSpeedInMPH())
                outputStream.write("%d," % link.getNumLanes())
                outputStream.write("%s," % Time.fromMinutes(sTime))
                outputStream.write("%s," % Time.fromMinutes(sTime + reportingTimeStep))
                outputStream.write("%d," % link.getSumOfAllMovementCounts(sTime, sTime + reportingTimeStep))         
                outputStream.write("%d\n" % link.getSimOutVolume(sTime, sTime + reportingTimeStep))
                          
    outputStream.close()
        
    # print 15-minute movement counts               
    DtaLogger.info("Writing %d-minute movement counts" % reportingTimeStep)
    
    # start with the header
    outputStream = open(MOVEMENT_OUT_FILE, "w") 
    outputStream.write("LinkID,OutoingLinkID,Label,OutgoingLinkLabel,FacilityType,FreeflowSpeed,NumLanes,StartNode,AtNode,EndNode,TurnType,StartTime,EndTime,CountVolume,ModelVolume\n")
        
    # now loop through all movements that have a count    
    for link in net.iterRoadLinks():
        for mov in link.iterOutgoingMovements():
            if not mov.hasCountInfo():
                continue
                
            # writes once every specified minutes interval, aggregating to specified min intervals   
            for sTime in range(simStartTime, simEndTime-1, reportingTimeStep):
                if sTime + reportingTimeStep >= simEndTime:
                    continue
                if mov.hasObsCount(sTime, sTime + reportingTimeStep):                               
                    outputStream.write("%d," % link.getId())
                    outputStream.write("%d," % mov.getOutgoingLink().getId())
                    outputStream.write("%s," % link.getLabel())
                    outputStream.write("%s," % mov.getOutgoingLink().getLabel())
                    outputStream.write("%d," % link.getFacilityType())
                    outputStream.write("%d," % link.getFreeFlowSpeedInMPH())
                    outputStream.write("%d," % link.getNumLanes())
                    outputStream.write("%d," % mov.getStartNodeId())
                    outputStream.write("%d," % mov.getAtNode().getId())
                    outputStream.write("%d," % mov.getEndNodeId())
                    outputStream.write("%s," % mov.getTurnType())
                    outputStream.write("%s," % Time.fromMinutes(sTime))
                    outputStream.write("%s," % Time.fromMinutes(sTime + reportingTimeStep))
                    outputStream.write("%d," % mov.getObsCount(sTime, sTime + reportingTimeStep))
                    outputStream.write("%d\n" % mov.getSimOutVolume(sTime, sTime + reportingTimeStep))
    
    outputStream.close()                    
        
    DtaLogger.info("Finished!")                 