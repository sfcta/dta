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
import sys
import dta

if __name__ == "__main__":
    
    #if len(sys.argv) < 6:
    #    print USAGE
    #    sys.exit(2)

    #INPUT_DYNAMEQ_NET_DIR                = sys.argv[1]
    #INPUT_DYNAMEQ_NET_PREFIX             = sys.argv[2]
    #COUNT_FILE                           = sys.argv[3]         
        

    INPUT_DYNAMEQ_NET_DIR = "/Users/michalis/Documents/sfcta/06082012"
    INPUT_DYNAMEQ_NET_PREFIX = "sf_jun7_530p"
    COUNT_FILE = "/Users/michalis/Documents/sfcta/06082012/counts_movements_15min_1600_1830.dat"

    
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
    net.readSimResults(simStartTime, simEndTime, 5)
    
    #net.readObsMovementCounts("/Users/michalis/Documents/sfcta/06082012/counts_movements_15min_1600_1830.dat")
    net.readObsMovementCounts("/Users/michalis/Documents/sfcta/06082012/counts_movements_5min_1600_1800.dat")

    for link in net.iterRoadLinks():
        for mov in link.iterOutgoingMovements():
            if not mov.hasCountInfo():
                continue
            for sTime in range(simStartTime, simEndTime-1, simTimeStep):
                if sTime + 15 >= simEndTime:
                    continue
                if mov.hasObsCount(sTime, sTime + 5):
                    print mov.getObsCount(sTime, sTime + 5), mov.getSimOutVolume(sTime, sTime + 5)
                
            

