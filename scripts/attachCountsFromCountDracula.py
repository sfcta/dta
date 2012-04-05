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

 python attachCountsFromCountDracula.py dynameq_net_dir dynameq_net_prefix
 
 e.g.
 
 python attachCountsFromCountDracula . sf
 

 Checks the CountDracula counts database for movement and turn counts for a few different
 timeslice specifications, and writes the data files for Dynameq into the current dir.
"""


import dta
import countdracula
import datetime
import sys

def exportTurnCountsToDynameqUserDataFile(cd_reader, sanfranciscoDynameqNet, starttime, period, num_intervals):
    """
    Exports turn counts from CountDracula database and exports them to a Dynameq movement user data file.
    
    *cd_reader* is a CountDraculaReader instance where the counts are stored
    *sanfranciscoDynameqNet* is a :py:class:`Network` instance for looking up the relevant nodes for the output file
    *starttime* is a datetime.time instance defining the start time for the counts we'll extract
    *period* is a datetime.timedelta instance defining the duration of each time slice (e.g. 15-minute counts)
    *num_intervals* is an integer defining how many intervals we'll export
    
    Writes to a file called ``counts_movements_Xmin_Y_Z.dat`` where X is the number of minutes in the period, Y is the starttime and Z is
    the endtime; e.g. counts_movements_15min_1600_1830.dat
    """    
    endtime         = datetime.datetime.combine(datetime.date(2000,1,1), starttime) + (num_intervals*period)
    filename        = "counts_movements_%dmin_%s_%s.dat" % (period.seconds/60, starttime.strftime("%H%M"), endtime.strftime("%H%M"))
    movement_counts = cd_reader.getTurningCounts(starttime=starttime, period=period, num_intervals=num_intervals)
    
    # file header (really just a comment)
    outfile         = open(filename, "w")
    outfile.write("*%8s %8s" % ("in", "out"))
    for interval in range(num_intervals):
        curtime     = datetime.datetime.combine(datetime.date(2000,1,1), starttime) + (interval*period)
        outfile.write("   %s" % curtime.strftime("%H%M"))
    outfile.write("\n")

    # For each movement count, see if we can find the right place for it in the sanfranciscoDynameqNet
    movements_found = 0
    movements_not_found = 0
    for key,counts in movement_counts.iteritems():

        # ignore if there are no real counts here
        real_counts = [count for count in counts if count > 0]
        if len(real_counts) == 0: continue
        
        try:
            movement = sanfranciscoDynameqNet.findMovementForRoadLabels(incoming_street_label=key[0].replace(" ",""), incoming_direction=key[1],
                                                                        outgoing_street_label=key[2].replace(" ",""), outgoing_direction=key[3],
                                                                        intersection_street_label=(key[4] if key[0]==key[2] else None),
                                                                        roadnode_id=key[5],
                                                                        remove_label_spaces=True)
            
            outfile.write(" %8d %8d" % (movement.getIncomingLink().getId(), movement.getOutgoingLink().getId()))
            for interval in range(num_intervals):
                outfile.write(" %6.1f" % counts[interval])
            outfile.write("\n")
            
            movements_found += 1
            
        except dta.DtaError, e:
            
            dta.DtaLogger.error("Failed to find movement: %s; counts=%s" % (str(e), str(counts)))               
            movements_not_found += 1
            
    outfile.close()
    dta.DtaLogger.info("Wrote movement counts for %d movements to %s; failed to find %d movements." % 
                       (movements_found, filename, movements_not_found))

def exportMainlineCountsToDynameUserDataFile(cd_reader, sanfranciscoDynameqNet, starttime, period, num_intervals):
    """
    Exports mainline counts from CountDracula database and exports them to a Dynameq link user data file.
    
    *cd_reader* is a CountDraculaReader instance where the counts are stored
    *sanfranciscoDynameqNet* is a :py:class:`Network` instance for looking up the relevant nodes for the output file    
    *starttime* is a datetime.time instance defining the start time for the counts we'll extract
    *period* is a datetime.timedelta instance defining the duration of each time slice (e.g. 15-minute counts)
    *num_intervals* is an integer defining how many intervals we'll export
    
    Writes to a file called ``counts_links_Xmin_Y_Z.dat`` where X is the number of minutes in the period, Y is the starttime and Z is
    the endtime; e.g. counts_links_15min_1600_1830.dat
    """    
    endtime         = datetime.datetime.combine(datetime.date(2000,1,1), starttime) + (num_intervals*period)
    filename        = "counts_links_%dmin_%s_%s.dat" % (period.seconds/60, starttime.strftime("%H%M"), endtime.strftime("%H%M"))
    link_counts     = cd_reader.getMainlineCounts(starttime=starttime, period=period, num_intervals=num_intervals)
    
    # file header (really just a comment)
    outfile         = open(filename, "w")
    outfile.write("*%8s " % "link")
    for interval in range(num_intervals):
        curtime     = datetime.datetime.combine(datetime.date(2000,1,1), starttime) + (interval*period)
        outfile.write("   %s" % curtime.strftime("%H%M"))
    outfile.write("\n")

    # For each link count, see if we can find the right place for it in the sanfranciscoDynameqNet
    links_found = 0
    links_not_found = 0
    for key,counts in link_counts.iteritems():

        # ignore if there are no real counts here
        real_counts = [count for count in counts if count > 0]
        if len(real_counts) == 0: continue
        
        try:
            links = sanfranciscoDynameqNet.findLinksForRoadLabels(on_street_label=key[0].replace(" ",""), on_direction=key[1],
                                                                  from_street_label=key[2].replace(" ",""),
                                                                  to_street_label=key[3].replace(" ",""),
                                                                  remove_label_spaces=True)
            
            # attribute the counts to all parts
            for link in links:
                outfile.write(" %8d" % link.getId())
                for interval in range(num_intervals):
                    outfile.write(" %6.1f" % counts[interval])
                outfile.write("\n")
            
            links_found += 1
            
        except dta.DtaError, e:
            
            dta.DtaLogger.error("Failed to find links: %s; counts=%s" % (str(e), str(counts)))               
            links_not_found += 1
            
    outfile.close()
    dta.DtaLogger.info("Wrote link counts for %d links to %s; failed to find %d links." % 
                       (links_found, filename, links_not_found))
if __name__ == '__main__':
    
    if len(sys.argv) != 3:
        print USAGE
        sys.exit(2)
    
    SF_DYNAMEQ_NET_DIR          = sys.argv[1] 
    SF_DYNAMEQ_NET_PREFIX       = sys.argv[2]
                
    dta.setupLogging("attachCountsFromCountDracula.INFO.log", "attachCountsFromCountDracula.DEBUG.log", logToConsole=True)
    
    dta.VehicleType.LENGTH_UNITS= "feet"
    dta.Node.COORDINATE_UNITS   = "feet"
    dta.RoadLink.LENGTH_UNITS   = "miles"
        

    # Read the SF scenario and DTA network
    sanfranciscoScenario = dta.DynameqScenario(dta.Time(0,0), dta.Time(23,0))
    sanfranciscoScenario.read(dir=SF_DYNAMEQ_NET_DIR, file_prefix=SF_DYNAMEQ_NET_PREFIX)
    
    sanfranciscoDynameqNet = dta.DynameqNetwork(scenario=sanfranciscoScenario)
    sanfranciscoDynameqNet.read(dir=SF_DYNAMEQ_NET_DIR, file_prefix=SF_DYNAMEQ_NET_PREFIX)
    
    # Instantiate the count dracula reader and do the exports
    # Time slices here are based on what we have available (according to CountDracula's querySanFranciscoCounts.py)
    cd_reader       = countdracula.CountsDatabaseReader(pw="ReadOnly", logger=dta.DtaLogger)
    exportTurnCountsToDynameqUserDataFile   (cd_reader, sanfranciscoDynameqNet, starttime=datetime.time(16,00), period=datetime.timedelta(minutes=15), num_intervals=10)
    exportTurnCountsToDynameqUserDataFile   (cd_reader, sanfranciscoDynameqNet, starttime=datetime.time(16,00), period=datetime.timedelta(minutes= 5), num_intervals=24)
    exportMainlineCountsToDynameUserDataFile(cd_reader, sanfranciscoDynameqNet, starttime=datetime.time(16,00), period=datetime.timedelta(minutes=15), num_intervals=10)

    
    
    