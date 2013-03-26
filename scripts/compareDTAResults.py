__copyright__   = "Copyright 2013 SFCTA"
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
 python visualizeDTAResults.py INPUT_DYNAMEQ_NET_DIR_1 
                               INPUT_DYNAMEQ_NET_PREFIX_1 
                               INPUT_DYNAMEQ_NET_DIR_2
                               INPUT_DYNAMEQ_NET_PREFIX_2 
                               REPORTING_TIME_STEP(min)
                               REPORT_START_TIME(min)
                               REPORT_END_TIME(min)
                               LINK_OUT_FILE (CSV)

 e.g.
 
 python visualizeDTAResults.py X:/Projects/ModelDev/dtaAnyway/validation2010.1/Reports/Scenarios/sf_jun8_420p/export 
                               sf_2012_Base
                               X:/Projects/ModelDev/dtaAnyway/validation2010.1/Reports/Scenarios/sf_jun8_420p/export 
                               sf_2012_MarketStreet
                               15
                               1020
                               1110
                               compareMarketStreet_link_5_630pm.csv 
                               

 **Currently this script assumes that scenario 1 contains the universe of links and that link ids are static between scenariso
 Creates reports from Dynameq output.  Currently, this includes:
   - Printing a CSV file with a comparison of Dynameq links and movements between scenarios
 
 Before running this script, you must export the loaded Dynameq network by going to 
 Network->Export->Dynameq Network.
"""


import sys
import dta
from dta.Logger import DtaLogger
from dta.Utils import Time

SIM_TIME_STEP = 5
SIM_START_TIME= 14 * 60 + 30
SIM_END_TIME  = 21 * 60 + 30

if __name__ == "__main__":
    if len(sys.argv) != 9:
        print USAGE
        sys.exit(2)
    INPUT_DYNAMEQ_NET_DIR_1              = sys.argv[1]
    INPUT_DYNAMEQ_NET_PREFIX_1           = sys.argv[2]
    INPUT_DYNAMEQ_NET_DIR_2              = sys.argv[3]
    INPUT_DYNAMEQ_NET_PREFIX_2           = sys.argv[4]
    REPORTING_TIME_STEP                  = sys.argv[5]
    REPORTING_START_TIME                 = sys.argv[6]
    REPORTING_END_TIME                   = sys.argv[7]
    LINK_OUT_FILE                        = sys.argv[8]
           
    # The SanFrancisco network will use feet for vehicle lengths and coordinates, and miles for link lengths
    dta.VehicleType.LENGTH_UNITS= "feet"
    dta.Node.COORDINATE_UNITS   = "feet"
    dta.RoadLink.LENGTH_UNITS   = "miles"
    simStartTime                = SIM_START_TIME
    simEndTime                  = SIM_END_TIME
    simTimeStep                 = SIM_TIME_STEP
    reportingTimeStep           = int(REPORTING_TIME_STEP)
    reportingStartTime          = int(REPORTING_START_TIME)
    reportingEndTime            = int(REPORTING_END_TIME)

    dta.setupLogging("visualizeDTAResults.INFO.log", "visualizeDTAResults.DEBUG.log", logToConsole=True)

    scenario_1 = dta.DynameqScenario()
    scenario_1.read(INPUT_DYNAMEQ_NET_DIR_1, INPUT_DYNAMEQ_NET_PREFIX_1) 
    net_1 = dta.DynameqNetwork(scenario_1)
    net_1.read(INPUT_DYNAMEQ_NET_DIR_1, INPUT_DYNAMEQ_NET_PREFIX_1)
    net_1.readSimResults(simStartTime, simEndTime, simTimeStep)
    
    scenario_2 = dta.DynameqScenario()
    scenario_2.read(INPUT_DYNAMEQ_NET_DIR_2, INPUT_DYNAMEQ_NET_PREFIX_2) 
    net_2 = dta.DynameqNetwork(scenario_2)
    net_2.read(INPUT_DYNAMEQ_NET_DIR_2, INPUT_DYNAMEQ_NET_PREFIX_2)
    net_2.readSimResults(simStartTime, simEndTime, simTimeStep)
    
    # start with the header
    outputStream = open(LINK_OUT_FILE, "w") 
    
    headStr = "LinkID,Label,FacilityType,FreeflowSpeed,NumLanes,PerMVol1,PerMVol2,PerMVolDif,PerMVolPDif"
    reportingSpan             = reportingEndTime - reportingStartTime
    numReportingPeriods       = reportingSpan / reportingTimeStep
    reportingPeriodsStartTime = [ reportingStartTime + (p*reportingTimeStep) for p in range(numReportingPeriods) ]
    reportingPeriodsEndTime   = [ reportingStartTime + ((p+1)*reportingTimeStep) for p in range(numReportingPeriods) ]

    for st,end in zip(reportingPeriodsStartTime,reportingPeriodsEndTime):
        headStr+=",MV1%s_%s,MV2%s_%s,MVD%s_%s,MVP_%s_%s" % (st,end,st,end,st,end,st,end) 
    
    outputStream.write(headStr+"\n")
    
    # now loop through all links that in scenario 1
    for link_1 in net_1.iterRoadLinks():     
   
        link_1_id  = link_1.getId()
        link_2     = net_2.getLinkForId(link_1_id)
        PerMVol1   = link_1.getSimOutVolume(reportingStartTime, reportingEndTime)
        PerMVol2   = link_2.getSimOutVolume(reportingStartTime, reportingEndTime)
        PerMVolDif = PerMVol2 - PerMVol1
        try:
            PerMVolPDif = PerMVolDif / PerMVol1
        except:
            PerMVolPDif = -9999

        # write links
        outputStream.write("%d," % link_1.getId())
        outputStream.write(",%s" % link_1.getLabel())
        outputStream.write(",%d" % link_1.getFacilityType())
        outputStream.write(",%d" % link_1.getFreeFlowSpeedInMPH())
        outputStream.write(",%d" % link_1.getNumLanes()) 
        outputStream.write(",%d" % PerMVol1)
        outputStream.write(",%d" % PerMVol2)
        outputStream.write(",%d" % PerMVolDif)
        outputStream.write(",%d" % PerMVolPDif)
        for st,end in zip(reportingPeriodsStartTime,reportingPeriodsEndTime):
            temp_mv1 = link_1.getSimOutVolume(st, end)
            temp_mv2 = link_2.getSimOutVolume(st, end)
            temp_dif = temp_mv2 - temp_mv1
            try:
                temp_pdif = temp_dif / temp_mv1
            except:
                temp_pdif = -9999
            outputStream.write(",%d" % temp_mv1 )
            outputStream.write(",%d" % temp_mv2 )
            outputStream.write(",%d" % temp_dif )
            outputStream.write(",%d" % temp_pdif)
        outputStream.write("\n")
                          
    outputStream.close()
 
    # write the shape file   
    DtaLogger.info("Writing shape files")  
    
    net_1.writeLinksToShp("sf_links_base")
    net_2.writeLinksToShp("sf_links_build")
        
    DtaLogger.info("Finished!")
