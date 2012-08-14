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
import datetime




USAGE = r"""

 python importCubeDemand.py dynameq_net_dir dynameq_net_prefix cube_demand_table cubeVehicleClass startTime endTime demand_portion timeStep output_demand_table cube_demand_table2 startTime2 endTime2 demand_portion2
 
 e.g.
 
python %DTA_CODE_DIR%\scripts\importCubeDemand.py . sf_trn Y:\dta\SanFrancisco\2010\demand\SanFranciscoSubArea_2010AM.csv Car_NoToll 14:30 18:30 14:30 15:30 01:00 0.33 demand_Car_NoToll.dat Y:\dta\SanFrancisco\2010\demand\SanFranciscoSubArea_2010AM.csv 15:30 18:30 00:30 1.00
 ****IMPORTANT****
 Demand tables must be input in chronological order with the earliest start time first, and they must have non-overlapping time periods.
 *****************
 The command line above will import the CAR trips in the SanFranciscoSubArea_2010AM.csv table and the SanFranciscoSubArea_2010PM.csv table to the dynameq network located in
 %DTA_CODE_DIR% and having the prefix sf_trn.
 The whole time period being read in is from 14:30 to 18:30.
 The time period associated with the SanFranciscoSubArea_2010PM.csv table is from 15:30 to 18:30. The other (AM) *.csv file listed will also be read and added to the 14:30-15:30 period.
 The demand portion variables indicate the fraction of the demand from the input tables that should be added to the Dynameq demand table.
 This is useful when only taking 1 hour of demand from a 3-hour input table.
 The output table will have 8 time periods, given the 4 hours of demand being imported and the 30 minute time slices and will be saved in the %DTA_CODE_DIR% in the dynameq format.
 
 """

def writeDynameqDemandHeader(outputStream, startTime, endTime, vehClassName, format='full'):
        """
        Write the demand header in the dynameq format
        .. todo:: implement linear writing
        """
        
        if format != 'full':
            raise DtaError("Unimplemented Matrix Format specified: %s" % (format))
            
        FORMAT_LINEAR    = 'FORMAT:linear'
        FORMAT_FULL      = 'FORMAT:full'    
        HEADER_LINE1     = '*DEMAND MATRIX ASCII FILE [FULL FORMAT]- GENERATED'
        VEHCLASS_SECTION = 'VEH_CLASS'
        DEFAULT_VEHCLASS = 'Default'
        DATA_SECTION     = 'DATA'
        

        outputStream.write("<DYNAMEQ>\n<VERSION_1.8>\n<MATRIX_FILE>\n")
        outputStream.write('%s %s %s\n' % ("Created by python DTA by SFCTA", 
                                           datetime.datetime.now().strftime("%x"), 
                                           datetime.datetime.now().strftime("%X")))
        if format == 'full':
            outputStream.write('%s\n' % FORMAT_FULL)
        elif format == 'linear':
            outputStream.write('%s\n' % FORMAT_LINEAR)
        else:
             raise DtaError("Don't understand Dynameq Output Matrix Format: %s" % (format))
             
        outputStream.write('%s\n' % VEHCLASS_SECTION)
        outputStream.write('%s\n' % vehClassName)
        outputStream.write('%s\n' % DATA_SECTION)
        outputStream.write("%s\n%s\n" % (startTime.strftime("%H:%M"),
                                         endTime.strftime("%H:%M")))                


if __name__ == "__main__":

    if len(sys.argv) < 12:
        print USAGE
        sys.exit(2)

    INPUT_DYNAMEQ_NET_DIR         = sys.argv[1]
    INPUT_DYNAMEQ_NET_PREFIX      = sys.argv[2]
    CUBE_TABLE                    = sys.argv[3]
    CUBE_VEH_CLASS                = sys.argv[4]
    START_TIME                    = sys.argv[5]
    END_TIME                      = sys.argv[6]
    START_TIME1                   = sys.argv[7]
    END_TIME1                     = sys.argv[8]
    TIME_STEP1                    = sys.argv[9]
    DEMAND_PORTION1                = sys.argv[10]
    OUTPUT_DYNAMEQ_TABLE          = sys.argv[11]

    if len(sys.argv)>12:
        CUBE_TABLE2               = sys.argv[12]
        START_TIME2               = sys.argv[13]
        END_TIME2                 = sys.argv[14]
        TIME_STEP2                = sys.argv[15]
        DEMAND_PORTION2           = sys.argv[16]
    else:
        CUBE_TABLE2               = None 
    if len(sys.argv)>17:
        CUBE_TABLE3               = sys.argv[17]
        START_TIME3               = sys.argv[18]
        END_TIME3                 = sys.argv[19]
        TIME_STEP3                = sys.argv[20]
        DEMAND_PORTION3           = sys.argv[21]
    else:
        CUBE_TABLE3               = None

    dta.VehicleType.LENGTH_UNITS= "feet"
    dta.Node.COORDINATE_UNITS   = "feet"
    dta.RoadLink.LENGTH_UNITS   = "miles"

    dta.setupLogging("importCubeDemand.INFO.log", "importCubeDemand.DEBUG.log", logToConsole=True)

    outputStream = open(OUTPUT_DYNAMEQ_TABLE, "w") 

        
    scenario = dta.DynameqScenario()
    scenario.read(INPUT_DYNAMEQ_NET_DIR, INPUT_DYNAMEQ_NET_PREFIX) 
    net = dta.DynameqNetwork(scenario)
    net.read(INPUT_DYNAMEQ_NET_DIR, INPUT_DYNAMEQ_NET_PREFIX)

    startTime = dta.Utils.Time.readFromString(START_TIME)
    endTime   = dta.Utils.Time.readFromString(END_TIME)

    if startTime < scenario.startTime:
        dta.DtaLogger.error("Demand cannot start before scenario start time.  Demand start = %s, Scenario start = %s" % (startTime.strftime("%H:%M"), scenario.startTime.strftime("%H:%M")))
    if endTime > scenario.endTime:
        dta.DtaLogger.error("Demand cannot end after scenario end time.  Demand end = %s, Scenario end = %s" % (endTime.strftime("%H:%M"), scenario.endTime.strftime("%H:%M")))

    startTime1 = dta.Utils.Time.readFromString(START_TIME1)
    endTime1   = dta.Utils.Time.readFromString(END_TIME1)
    timeStep1  = dta.Utils.Time.readFromString(TIME_STEP1)

    if startTime1 != startTime:
        dta.DtaLogger.error("Demand tables must be listed in chronological order with the earliest one first.")

    # If there are multiple demand tables being used, check to see what the overall start and end times are and make sure the time periods do not overlap with the exising time period
    if CUBE_TABLE2:
        startTime2 = dta.Utils.Time.readFromString(START_TIME2)
        endTime2   = dta.Utils.Time.readFromString(END_TIME2)
        timeStep2  = dta.Utils.Time.readFromString(TIME_STEP2)
        if startTime2 != endTime1:
            dta.DtaLogger.error("Start of second time period (%s) should equal the end of first time period (%s)." % (startTime2.strftime("%H:%M"),endTime1.strftime("%H:%M")))

        if CUBE_TABLE3:
            startTime3 = dta.Utils.Time.readFromString(START_TIME3)
            endTime3   = dta.Utils.Time.readFromString(END_TIME3)
            timeStep3  = dta.Utils.Time.readFromString(TIME_STEP3) 
            if startTime3 != endTime2:
                dta.DtaLogger.error("Start of third time period (%s) should equal the end of second time period (%s)." % (startTime3.strftime("%H:%M"),endTime2.strftime("%H:%M")))
                
    # Write out the header for the dynameq file using the overall start and end times found
    writeDynameqDemandHeader(outputStream, startTime, endTime, CUBE_VEH_CLASS)

    # Create and write out demand for each table in the correct order (earliest first and getting continualy later.)
    demand1 = dta.Demand.readCubeODTable(CUBE_TABLE, net, CUBE_VEH_CLASS, startTime1, endTime1, timeStep1, float(DEMAND_PORTION1))
    demand1.writeDynameqTable(outputStream)
    if CUBE_TABLE2:
        demand2 = dta.Demand.readCubeODTable(CUBE_TABLE2, net, CUBE_VEH_CLASS, startTime2, endTime2, timeStep2, float(DEMAND_PORTION2))
        demand2.writeDynameqTable(outputStream)
    if CUBE_TABLE3:
        demand3 = dta.Demand.readCubeODTable(CUBE_TABLE3, net, CUBE_VEH_CLASS, startTime3, endTime3, timeStep3, float(DEMAND_PORTION3))
        demand3.writeDynameqTable(outputStream)

    outputStream.close()

    #dta.DtaLogger.info("Wrote%10.2f %-16s   to %s" % (demand.getTotalNumTrips(),
    #                                                  "TRIPS", OUTPUT_DYNAMEQ_TABLE))

    
    


    
    
        
        








