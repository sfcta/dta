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

import pdb 
import dta
import os
import sys


USAGE = r"""

 python importCubeDemand.py dynameq_net_dir dynameq_net_prefix cube_demand_table cubeVehicleClass startTime endTime timeStep output_demand_table
 
 e.g.
 
 python importCubeDemand.py ../testdata/dynameqNetwork_gearySubset/ smallTestNet ../testdata/dynameqNetwork_gearySubset/cubeTestDemand.txt "TRUCK" 15:30 18:30 00:15 ../testdata/dynameqNetwork_gearySubset/sfTestDemand 

 The command line above will import the TRUCK trips in the cubeTestDemand.txt table to the dynameq network located in ../testdata/dynameqNetwork_gearySubset/ and having the prefix smallTestNet.
 The time period associated with the cubeTestDemand.txt table is from 15:30 to 18:30. The output table will have one time period, the same as the one applied to Cube, and will be saved at  
 ../testdata/dynameqNetwork_gearySubset/sfTestDemand in the dynameq specific format (cell values are hourly trip rates). Currently the timeStep variable (00:15) in our example is not used. 
 
 """

if __name__ == "__main__":

    if len(sys.argv) != 9:
        print USAGE
        sys.exit(2)

    INPUT_DYNAMEQ_NET_DIR         = sys.argv[1]
    INPUT_DYNAMEQ_NET_PREFIX      = sys.argv[2]
    CUBE_TABLE                    = sys.argv[3]
    CUBE_VEH_CLASS                = sys.argv[4]
    START_TIME                    = sys.argv[5]
    END_TIME                      = sys.argv[6]
    TIME_STEP                     = sys.argv[7]
    OUTPUT_DYNAMEQ_TABLE          = sys.argv[8]

    dta.VehicleType.LENGTH_UNITS= "feet"
    dta.Node.COORDINATE_UNITS   = "feet"
    dta.RoadLink.LENGTH_UNITS   = "miles"

    dta.setupLogging("dtaInfo.log", "dtaDebug.log", logToConsole=True)
    
    scenario = dta.DynameqScenario(dta.Time(0,0), dta.Time(23,0))
    scenario.read(INPUT_DYNAMEQ_NET_DIR, INPUT_DYNAMEQ_NET_PREFIX) 
    net = dta.DynameqNetwork(scenario)
    net.read(INPUT_DYNAMEQ_NET_DIR, INPUT_DYNAMEQ_NET_PREFIX)

    startTime = dta.Utils.Time.readFromString(START_TIME)
    endTime   = dta.Utils.Time.readFromString(END_TIME)
    timeStep  = dta.Utils.Time.readFromString(TIME_STEP)

    demand = dta.Demand.readCubeODTable(CUBE_TABLE, net, CUBE_VEH_CLASS, startTime, endTime)

    demand.write(OUTPUT_DYNAMEQ_TABLE)


    dta.DtaLogger.info("Wrote%10.2f %-16s   to %s" % (demand.getTotalNumTrips(),
                                                      "TRIPS", OUTPUT_DYNAMEQ_TABLE))


    
    


    
    
        
        








