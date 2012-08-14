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

import getopt
import pdb 
import dta
import os
import sys
import datetime
import csv




USAGE = r"""

 python importCubeDemand.py dynameq_net_dir dynameq_net_prefix cubeVehicleClass output_demand_table startTime endTime cube_demand_table1 startTime1 endTime1 demand_portion1 timeStep1 cube_demand_table2 startTime2 endTime2 demand_portion2
 
 e.g.
 
python %DTA_CODE_DIR%\scripts\importCubeDemand.py . sf_trn Car_NoToll demand_Car_NoToll.dat 14:30 18:30 Y:\dta\SanFrancisco\2010\demand\SanFranciscoSubArea_2010_MD.csv 14:30 15:30 01:00 0.15  Y:\dta\SanFrancisco\2010\demand\SanFranciscoSubArea_2010_PM.csv 15:30 18:30 00:30 1.00
 ****IMPORTANT****
 Demand tables must be input in chronological order with the earliest start time first, and they must have non-overlapping time periods.
 *****************
 The command line above will import the Car_NoToll trips in the SanFranciscoSubArea_2010_MD.csv table and the SanFranciscoSubArea_2010_PM.csv table to the dynameq network located in
 %DTA_CODE_DIR% and having the prefix sf_trn.
 The whole time period being read in is from 14:30 to 18:30.
 The time period associated with the SanFranciscoSubArea_2010_PM.csv table is from 15:30 to 18:30. The other (MD) *.csv file listed will also be read and added to the 14:30-15:30 period.
 The demand portion variables indicate the fraction of the demand from the input tables that should be added to the Dynameq demand table.
 This is useful when only taking a fraction of the total demand (i.e. 1 hour of demand from a 3-hour input table).
 The code is able to loop through any number of demand tables and assocated demand periods as long as they are in chronological order, within the scenario time period, and covering the entire
 period specified by the start time and end time.
 The output table will have 7 time periods, given the first hour being imported as one time slice and the remaining 3 hours of demand being imported
 in 30 minute time slices and will be saved in the %DTA_CODE_DIR% in the dynameq format.
 
 """

               


if __name__ == "__main__":

    optlist, args = getopt.getopt(sys.argv[1:], "f:")

    if len(args) < 11:
        print USAGE
        sys.exit(2)
    

    INPUT_DYNAMEQ_NET_DIR         = args[0]
    INPUT_DYNAMEQ_NET_PREFIX      = args[1]
    CUBE_VEH_CLASS                = args[2]
    OUTPUT_DYNAMEQ_TABLE          = args[3]
    START_TIME                    = args[4]
    END_TIME                      = args[5]

    if optlist:
        for (opt,arg) in optlist:
            if opt=="-f":
                DEMAND_PROFILE_FILE   = arg
    else:
        DEMAND_PROFILE_FILE = None
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

  
# Read in the demand profile(s) if an input file was provided
    factorsStart = []
    if DEMAND_PROFILE_FILE:
        factorsEnd   = []
        factorsList = []
        factorsLists = []
        factorNum = 0
        inputStream = open(DEMAND_PROFILE_FILE, "r")
        for record in csv.DictReader(inputStream):
            factorsList = []
            factorsStart.append(dta.Utils.Time.readFromString(record["Start Time"]))
            factorsEnd.append(dta.Utils.Time.readFromString(record["End Time"]))
            ii = 1
            factorNum = record["Factor %d" % ii]
            while factorNum:
                factorsList.append(factorNum)
                ii += 1
                factorNum = record["Factor %d" % ii]
            factorsLists.append(factorsList)

# Check to make sure that demand is within the scenario time.  Exit if not.  

    if startTime < scenario.startTime:
        dta.DtaLogger.error("Demand cannot start before scenario start time.  Demand start = %s, Scenario start = %s" % (startTime.strftime("%H:%M"), scenario.startTime.strftime("%H:%M")))
        sys.exit(2)
    if endTime > scenario.endTime:
        dta.DtaLogger.error("Demand cannot end after scenario end time.  Demand end = %s, Scenario end = %s" % (endTime.strftime("%H:%M"), scenario.endTime.strftime("%H:%M")))
        sys.exit(2)

    # Create and write out demand for each table in the correct order (earliest first and getting continualy later.)
    dta.Demand.writeDynameqDemandHeader(outputStream, startTime, endTime, CUBE_VEH_CLASS)
    numDemandTables = (len(args)-5)/5
    for ii in range(0,numDemandTables):
        CUBE_TABLE            = args[6+(ii*5)]
        START_TIME_N          = args[7+(ii*5)]
        END_TIME_N            = args[8+(ii*5)]
        TIME_STEP             = args[9+(ii*5)]
        DEMAND_PORTION        = args[10+(ii*5)]

    # Check to be sure time is continuous
        if ii == 0:
            if dta.Utils.Time.readFromString(START_TIME_N) != startTime:
                dta.DtaLogger.error("Start time of first demand period (%s) must equal provided demand start time of %s." % (START_TIME_N, startTime.strftime("%H:%M")))
        elif ii > 0 and ii < numDemandTables-1:
            if dta.Utils.Time.readFromString(START_TIME_N) != endTime_n:
                dta.DtaLogger.error("Time should be continuous.  Start time of demand period %d does not equal end time of demand period %d." % (ii+1, ii))
        elif ii > 0 and ii == numDemandTables-1:
            if dta.Utils.Time.readFromString(END_TIME_N) != endTime:
                dta.DtaLogger.error("End time of last demand period (%s) must equal provided demand end time of %s." % (END_TIME_N, endTime.strftime("%H:%M")))

    # Set start time, end time, and time step for the demand period
        startTime_n = dta.Utils.Time.readFromString(START_TIME_N)
        endTime_n   = dta.Utils.Time.readFromString(END_TIME_N)
        timeStep    = dta.Utils.Time.readFromString(TIME_STEP)

    # Check to see if demand period has a demand profile

        demProf = 0
        for jj in range(0,len(factorsStart)):
            if startTime_n == factorsStart[jj] and endTime_n == factorsEnd[jj]:
                demProf = 1
                FactorsList = factorsLists[jj]

    # Read in cube demand table, apply time of day factors (if applicable) and write demand out to OUTPUT_DYNAMEQ_TABLE

        if demProf == 1:
            timeStep = endTime_n - startTime_n
            demand = dta.Demand.readCubeODTable(CUBE_TABLE, net, CUBE_VEH_CLASS, startTime_n, endTime_n, timeStep, float(DEMAND_PORTION))
            demand = demand.applyTimeOfDayFactors(FactorsList)
        else:
            demand = dta.Demand.readCubeODTable(CUBE_TABLE, net, CUBE_VEH_CLASS, startTime_n, endTime_n, timeStep, float(DEMAND_PORTION))

        demand.writeDynameqTable(outputStream)
        dta.DtaLogger.info("Wrote %10.2f %-10s to %s" % (demand.getTotalNumTrips(), "TRIPS", OUTPUT_DYNAMEQ_TABLE))

    outputStream.close()


    
    


    
    
        
        








