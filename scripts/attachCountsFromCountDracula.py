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

 python attachCountsFromCountDracula.py [-l links.shp] [-m movements.shp] [-n nodes.shp] dynameq_net_dir dynameq_net_prefix
 
 e.g.
 
 python attachCountsFromCountDracula.py . sf
 

 Checks the CountDracula counts database for movement and turn counts for a few different
 timeslice specifications, and writes the data files for Dynameq into the current dir.
"""


import dta
import datetime
import getopt
import sys
import xlwt

# global
STYLE_REG  = xlwt.easyxf('font: name Calibri')
STYLE_BOLD = xlwt.easyxf('font: name Calibri, bold on')
STYLE_TIME = xlwt.easyxf('font: name Calibri', num_format_str='hh:mm')
STYLE_DATE = xlwt.easyxf('font: name Calibri', num_format_str='yyyy-mm-dd hh:mm ddd')
STYLE_DATE.alignment = xlwt.Alignment()
STYLE_DATE.alignment.horz = xlwt.Alignment.HORZ_LEFT

def exportTurnCountsToDynameqUserDataFile(cd_reader, sanfranciscoDynameqNet, starttime, period, num_intervals,
                                               suffix=None, from_date=None, to_date=None, weekdays=None,
                                               all_count_workbook=None):
    """
    Exports turn counts from CountDracula database and exports them to a Dynameq movement user data file.
    
    * *cd_reader* is a CountDraculaReader instance where the counts are stored
    * *sanfranciscoDynameqNet* is a :py:class:`Network` instance for looking up the relevant nodes for the output file
    * *starttime* is a datetime.time instance defining the start time for the counts we'll extract
    * *period* is a datetime.timedelta instance defining the duration of each time slice (e.g. 15-minute counts)
    * *num_intervals* is an integer defining how many intervals we'll export
    * *suffix* is an optional suffix for the file name (something descriptive)
    * *from_date* is a datetime.date instance defining the start date (inclusive) of acceptable count dates
    * *to_date* is a datetime.date instance defining the end date (inclusive) of acceptable count dates
    * If *weekdays* is passed (a list of integers, where Monday is 0 and Sunday is 6), then counts will
      only include the given weekdays.
    * If *all_count_workbook* is passed (it should be an xlwt.Workbook) then the raw data will be added
      to a sheet there as well.
            
    Writes to a file called ``counts_movements_Xmin_Y_Z_suffix.dat`` where X is the number of minutes in the period, Y is the starttime and Z is
    the endtime; e.g. counts_movements_15min_1600_1830_suffix.dat
    """    
    endtime         = datetime.datetime.combine(datetime.date(2000,1,1), starttime) + (num_intervals*period)
    filename        = "counts_movements_%dmin_%s_%s%s.dat" % (period.seconds/60, 
                                                              starttime.strftime("%H%M"), endtime.strftime("%H%M"),
                                                              "_%s" % suffix if suffix else "")
    movement_counts = cd_reader.getTurningCounts(starttime=starttime, period=period, num_intervals=num_intervals,
                                                 from_date=from_date, to_date=to_date, weekdays=weekdays)
    
    # file header (comments)
    outfile         = open(filename, "w")
    outfile.write("* mainline_counts\n")
    outfile.write("* domain: Movements\n")
    outfile.write("* script: %s\n" % sys.argv[0])
    outfile.write("* starttime: %s\n" % starttime.strftime("%H:%M"))
    outfile.write("* period: %d min\n" % (period.seconds/60))
    outfile.write("* num_intervals: %d\n" % num_intervals)
    outfile.write("* date_range: %s - %s\n" % (str(from_date), str(to_date)))
    outfile.write("* weekdays: %s\n" % str(weekdays))
    outfile.write("* CREATED %s\n" % datetime.datetime.now().ctime())
    outfile.write("*%8s %8s %8s" % ("at","start","end"))

    if all_count_workbook:
        sheet = all_count_workbook.add_sheet("movavg_%s_%d" % (suffix, period.seconds/60))
        # header row
        row_num = 0
        sheet.write(row_num,0, "from-at-to",    STYLE_BOLD) # for joins
        sheet.write(row_num,1, "fromstreet",    STYLE_BOLD)
        sheet.write(row_num,2, "fromdir",       STYLE_BOLD)
        sheet.write(row_num,3, "tostreet",      STYLE_BOLD)
        sheet.write(row_num,4, "todir",         STYLE_BOLD)

        sheet.panes_frozen      = True
        sheet.horz_split_pos    = 1
        sheet.col(0).width      = 23*256
        sheet.col(1).width      = 15*256
        sheet.col(3).width      = 15*256

    for interval in range(num_intervals):
        curtime     = datetime.datetime.combine(datetime.date(2000,1,1), starttime) + (interval*period)
        outfile.write("  %s" % curtime.strftime("%H:%M"))
        if all_count_workbook: sheet.write(row_num, 5+interval, curtime, STYLE_TIME)
        
    outfile.write("\n")

    # For each movement count, see if we can find the right place for it in the sanfranciscoDynameqNet
    movements_found     = 0
    movements_not_found = 0
    key_to_movement     = {} # cache key to link
    
    for key,counts in movement_counts.iteritems():

        # ignore if there are no real counts here
        real_counts = [count for count in counts if count > 0]
        if len(real_counts) == 0: continue
        
        dta.DtaLogger.debug("Finding movement for %s %s to %s %s @ %d (x street %s)" % 
                            (key[0], key[1], key[2], key[3], key[5], key[4]))
        
        second_try = False
        movement = None
        try:
            movement = sanfranciscoDynameqNet.findMovementForRoadLabels(incoming_street_label=key[0].replace(" ",""), incoming_direction=key[1],
                                                                        outgoing_street_label=key[2].replace(" ",""), outgoing_direction=key[3],
                                                                        intersection_street_label=(key[4] if key[0]==key[2] else None),
                                                                        roadnode_id=key[5],
                                                                        remove_label_spaces=True,
                                                                        use_dir_for_movement=False,    # use labels
                                                                        dir_need_not_be_primary=True)  # dir not need be primary

            key_to_movement[key] = movement
            movements_found += 1
            dta.DtaLogger.debug(" %8d %8d" % (movement.getIncomingLink().getId(), movement.getOutgoingLink().getId()))
                    
        except dta.DtaError, e:
            
            dta.DtaLogger.warn("Failed to find movement @ %d: %s; counts=%s" % (key[5], str(e), str(counts)))    
            # try again but not within an except
            second_try = True
            
        if second_try:
            try:
                movement = sanfranciscoDynameqNet.findMovementForRoadLabels(incoming_street_label=key[0].replace(" ",""), incoming_direction=key[1],
                                                                            outgoing_street_label=key[2].replace(" ",""), outgoing_direction=key[3],
                                                                            intersection_street_label=(key[4] if key[0]==key[2] else None),
                                                                            roadnode_id=key[5],
                                                                            remove_label_spaces=True,
                                                                            use_dir_for_movement=True,     # use directions over labels
                                                                            dir_need_not_be_primary=False) # keep it tighter tho

                key_to_movement[key] = movement
                movements_found += 1
                dta.DtaLogger.warn("Found movement by loosening label constraints: %s %s to %s %s" % 
                                   (movement.getIncomingLink().getLabel(), movement.getIncomingLink().getDirection(),
                                    movement.getOutgoingLink().getLabel(), movement.getOutgoingLink().getDirection()))
                dta.DtaLogger.debug(" %8d %8d" % (movement.getIncomingLink().getId(), movement.getOutgoingLink().getId()))
            
            except dta.DtaError, e:
                
                dta.DtaLogger.error("Failed to find movement @ %d: %s; counts=%s" % (key[5], str(e), str(counts)))                  
                movements_not_found += 1
                continue
        
        # movement found -- write it out
        outfile.write(" %8d %8d %8d" % (movement.getAtNode().getId(), 
                                        movement.getStartNode().getId(),
                                        movement.getEndNode().getId()))
        for interval in range(num_intervals):
            outfile.write(" %6.1f" % counts[interval])
        outfile.write("\n")
        
        # workbook version
        if all_count_workbook:
            row_num += 1
            sheet.write(row_num, 0, "%d %d %d" % (movement.getStartNode().getId(),
                                                  movement.getAtNode().getId(),
                                                  movement.getEndNode().getId()), STYLE_REG)
            sheet.write(row_num, 1, key[0], STYLE_REG)
            sheet.write(row_num, 2, key[1], STYLE_REG)
            sheet.write(row_num, 3, key[2], STYLE_REG)
            sheet.write(row_num, 4, key[3], STYLE_REG)
            for interval in range(num_intervals):
                sheet.write(row_num, 5+interval, counts[interval], STYLE_REG)            
            
    outfile.close()
    dta.DtaLogger.info("Wrote movement counts for %d movements to %s; failed to find %d movements." % 
                       (movements_found, filename, movements_not_found))

    # write raw data into workbook
    if all_count_workbook:
        sheet = all_count_workbook.add_sheet("movements_%s_%d" % (suffix, period.seconds/60))

        # fetch the movement_counts again but without averaging
        movement_counts = cd_reader.getTurningCounts(starttime=starttime, period=period, num_intervals=num_intervals,
                                                     from_date=from_date, to_date=to_date, weekdays=weekdays,
                                                     return_averages=False)
        # header row
        row_num = 0
        # dta location data        
        sheet.write(row_num,0, "from-at-to",    STYLE_BOLD) # for joins
        sheet.write(row_num,1, "at-node",       STYLE_BOLD)
        sheet.write(row_num,2, "from-node",     STYLE_BOLD)
        sheet.write(row_num,3, "to-node",       STYLE_BOLD)
        sheet.write(row_num,4, "from_link",     STYLE_BOLD)
        sheet.write(row_num,5, "to_link",       STYLE_BOLD)
        # count dracula location data - fromstreet, fromdir, tostreet, todir
        sheet.write(row_num,6, "fromstreet",    STYLE_BOLD)
        sheet.write(row_num,7, "fromdir",       STYLE_BOLD)
        sheet.write(row_num,8, "tostreet",      STYLE_BOLD)
        sheet.write(row_num,9, "todir",         STYLE_BOLD)
        # count data, count = [ count, starttime, period, vtype, sourcefile, project ]
        sheet.write(row_num,10,"count",         STYLE_BOLD)
        sheet.write(row_num,11,"starttime",     STYLE_BOLD)
        sheet.write(row_num,12,"year",          STYLE_BOLD) # for ease of trends analysis
        sheet.write(row_num,13,"allyears",      STYLE_BOLD) # for ease of trends analysis        
        sheet.write(row_num,14,"time",          STYLE_BOLD) # for ease of trends analysis
        sheet.write(row_num,15,"period (min)",  STYLE_BOLD)
        sheet.write(row_num,16,"vtype",         STYLE_BOLD)
        sheet.write(row_num,17,"sourcefile",    STYLE_BOLD)
        sheet.write(row_num,18,"project",       STYLE_BOLD)

        sheet.panes_frozen      = True
        sheet.horz_split_pos    = 1
        sheet.col(0).width      = 23*256
        sheet.col(11).width     = 23*256
        
        for key,counts in movement_counts.iteritems():
            if key not in key_to_movement: continue

            # figure out multiyear
            count_years = set()
            for count in counts: count_years.add(count[1].year)
            
            for count in counts:
                # data row
                row_num += 1
                movement = key_to_movement[key]
                # dta location data                        
                sheet.write(row_num,0, "%d %d %d" % (movement.getStartNode().getId(), movement.getAtNode().getId(), movement.getEndNode().getId()), STYLE_REG)
                sheet.write(row_num,1, movement.getAtNode().getId(),        STYLE_REG)
                sheet.write(row_num,2, movement.getStartNode().getId(),     STYLE_REG)
                sheet.write(row_num,3, movement.getEndNode().getId(),       STYLE_REG)
                sheet.write(row_num,4, movement.getIncomingLink().getId(),  STYLE_REG)
                sheet.write(row_num,5, movement.getOutgoingLink().getId(),  STYLE_REG)
                # count dracula location data - fromstreet, fromdir, tostreet, todir
                sheet.write(row_num,6, key[0],                              STYLE_REG)
                sheet.write(row_num,7, key[1],                              STYLE_REG)
                sheet.write(row_num,8, key[2],                              STYLE_REG)
                sheet.write(row_num,9, key[3],                              STYLE_REG)
                # count data, count = [ count, starttime, period, vtype, sourcefile, project ]
                sheet.write(row_num,10, count[0],                           STYLE_REG)
                sheet.write(row_num,11, count[1],                           STYLE_DATE)
                sheet.write(row_num,12, count[1].year,                      STYLE_REG)
                sheet.write(row_num,13, str(sorted(count_years)),           STYLE_REG)                
                sheet.write(row_num,14, 
                            datetime.time(count[1].hour, 
                                          count[1].minute,
                                          count[1].second),                 STYLE_TIME)
                sheet.write(row_num,15,(count[2].seconds/60),               STYLE_REG)
                sheet.write(row_num,16,count[3],                            STYLE_REG)
                sheet.write(row_num,17,count[4],                            STYLE_REG)
                sheet.write(row_num,18,count[5],                            STYLE_REG)


def exportMainlineCountsToDynameUserDataFile(cd_reader, sanfranciscoDynameqNet, starttime, period, num_intervals,
                                                   suffix=None, from_date=None, to_date=None, weekdays=None,
                                                   all_count_workbook=None):
    """
    Exports mainline counts from CountDracula database and exports them to a Dynameq link user data file.
    
    * *cd_reader* is a CountDraculaReader instance where the counts are stored
    * *sanfranciscoDynameqNet* is a :py:class:`Network` instance for looking up the relevant nodes for the output file    
    * *starttime* is a datetime.time instance defining the start time for the counts we'll extract
    * *period* is a datetime.timedelta instance defining the duration of each time slice (e.g. 15-minute counts)
    * *num_intervals* is an integer defining how many intervals we'll export
    * *suffix* is an optional suffix for the file name (something descriptive)
    * *from_date* is a datetime.date instance defining the start date (inclusive) of acceptable count dates
    * *to_date* is a datetime.date instance defining the end date (inclusive) of acceptable count dates
    * If *weekdays* is passed (a list of integers, where Monday is 0 and Sunday is 6), then counts will
      only include the given weekdays.
    * If *all_count_workbook* is passed (it should be an xlwt.Workbook) then the raw data will be added
      to a sheet there as well.
          
    Writes to a file called ``counts_links_Xmin_Y_Z.dat`` where X is the number of minutes in the period, Y is the starttime and Z is
    the endtime; e.g. counts_links_15min_1600_1830.dat
    """    
    endtime         = datetime.datetime.combine(datetime.date(2000,1,1), starttime) + (num_intervals*period)
    filename        = "counts_links_%dmin_%s_%s%s.dat" % (period.seconds/60, 
                                                          starttime.strftime("%H%M"), 
                                                          endtime.strftime("%H%M"),
                                                          "_%s" % suffix if suffix else "")
    link_counts     = cd_reader.getMainlineCounts(starttime=starttime, period=period, num_intervals=num_intervals,
                                                  from_date=from_date, to_date=to_date, weekdays=weekdays)
    
    # file header (comments)
    outfile         = open(filename, "w")
    outfile.write("* mainline_counts\n")
    outfile.write("* domain: Links\n")
    outfile.write("* script: %s\n" % sys.argv[0])
    outfile.write("* starttime: %s\n" % starttime.strftime("%H:%M"))
    outfile.write("* period: %d min\n" % (period.seconds/60))
    outfile.write("* num_intervals: %d\n" % num_intervals)
    outfile.write("* date_range: %s - %s\n" % (str(from_date), str(to_date)))
    outfile.write("* weekdays: %s\n" % str(weekdays))
    outfile.write("* CREATED %s\n" % datetime.datetime.now().ctime())
    outfile.write("*%8s %8s" % ("from","to"))
    
    if all_count_workbook:
        sheet = all_count_workbook.add_sheet("linkavg_%s_%d" % (suffix, period.seconds/60))
        # header row
        row_num = 0
        sheet.write(row_num,0, "from-to",       STYLE_BOLD) # for joins
        sheet.write(row_num,1, "onstreet",      STYLE_BOLD)
        sheet.write(row_num,2, "ondir",         STYLE_BOLD)
        sheet.write(row_num,3, "fromstreet",    STYLE_BOLD)
        sheet.write(row_num,4, "tostreet",      STYLE_BOLD)

        sheet.panes_frozen      = True
        sheet.horz_split_pos    = 1
        sheet.col(0).width      = 15*256
        sheet.col(1).width      = 15*256
        sheet.col(3).width      = 15*256
        
    for interval in range(num_intervals):
        curtime     = datetime.datetime.combine(datetime.date(2000,1,1), starttime) + (interval*period)
        outfile.write("  %s" % curtime.strftime("%H:%M"))
        if all_count_workbook: sheet.write(row_num, 5+interval, curtime, STYLE_TIME)
    outfile.write("\n")

    # For each link count, see if we can find the right place for it in the sanfranciscoDynameqNet
    links_found     = 0
    links_not_found = 0
    key_to_link     = {} # cache key to link
    
    for key,counts in link_counts.iteritems():

        # ignore if there are no real counts here
        real_counts = [count for count in counts if count > 0]
        if len(real_counts) == 0: continue
        
        try:
            links = sanfranciscoDynameqNet.findLinksForRoadLabels(on_street_label=key[0].replace(" ",""), on_direction=key[1],
                                                                  from_street_label=key[2].replace(" ",""),
                                                                  to_street_label=key[3].replace(" ",""),
                                                                  remove_label_spaces=True)
            
            # attribute the counts to the first part
            outfile.write(" %8d %8d" % (links[0].getStartNode().getId(), links[0].getEndNode().getId()))
            for interval in range(num_intervals):
                outfile.write(" %6.1f" % counts[interval])
            outfile.write("\n")
            
            # workbook version
            if all_count_workbook:
                row_num += 1
                sheet.write(row_num, 0, "%d %d" % (links[0].getStartNode().getId(), links[0].getEndNode().getId()), STYLE_REG)
                sheet.write(row_num, 1, key[0], STYLE_REG)
                sheet.write(row_num, 2, key[1], STYLE_REG)
                sheet.write(row_num, 3, key[2], STYLE_REG)
                sheet.write(row_num, 4, key[3], STYLE_REG)
                for interval in range(num_intervals):
                    sheet.write(row_num, 5+interval, counts[interval], STYLE_REG)
    
            key_to_link[key] = links[0]
            links_found += 1

        except dta.DtaError, e:
            
            dta.DtaLogger.error("Failed to find links: %s; counts=%s" % (str(e), str(counts)))               
            links_not_found += 1
            
    outfile.close()
    dta.DtaLogger.info("Wrote link counts for %d links to %s; failed to find %d links." % 
                       (links_found, filename, links_not_found))

    # write raw data into workbook
    if all_count_workbook:
        sheet = all_count_workbook.add_sheet("links_%s_%d" % (suffix, period.seconds/60))

        # fetch the link_counts again but without averaging
        link_counts = cd_reader.getMainlineCounts(starttime=starttime, period=period, num_intervals=num_intervals,
                                                  from_date=from_date, to_date=to_date, weekdays=weekdays,
                                                  return_averages=False)
        # header row
        row_num = 0
        # dta location data
        sheet.write(row_num,0, "from-to",       STYLE_BOLD)
        sheet.write(row_num,1, "from-node",     STYLE_BOLD)
        sheet.write(row_num,2, "to-node",       STYLE_BOLD)
        sheet.write(row_num,3, "linkid",        STYLE_BOLD)
        # count dracula location data
        sheet.write(row_num,4, "onstreet",      STYLE_BOLD)
        sheet.write(row_num,5, "ondir",         STYLE_BOLD)
        sheet.write(row_num,6, "fromstreet",    STYLE_BOLD)
        sheet.write(row_num,7, "tostreet",      STYLE_BOLD)
        # count data, count = [ count, starttime, period, vtype, refpos, sourcefile, project ]
        sheet.write(row_num,8, "count",         STYLE_BOLD)
        sheet.write(row_num,9, "starttime",     STYLE_BOLD)
        sheet.write(row_num,10,"year",          STYLE_BOLD) # for ease of trends analysis
        sheet.write(row_num,11,"allyears",      STYLE_BOLD) # for ease of trends analysis
        sheet.write(row_num,12,"time",          STYLE_BOLD) # for ease of trends analysis
        sheet.write(row_num,13,"period (min)",  STYLE_BOLD)
        sheet.write(row_num,14,"vtype",         STYLE_BOLD)
        sheet.write(row_num,15,"refpos",        STYLE_BOLD)
        sheet.write(row_num,16,"sourcefile",    STYLE_BOLD)
        sheet.write(row_num,17,"project",       STYLE_BOLD)

        sheet.panes_frozen      = True
        sheet.horz_split_pos    = 1
        sheet.col(0).width      = 15*256
        sheet.col(9).width      = 23*256
        
        for key,counts in link_counts.iteritems():
            if key not in key_to_link: continue
            
            # figure out multiyear
            count_years = set()
            for count in counts: count_years.add(count[1].year)
            
            for count in counts:
                # data row
                row_num += 1
                link = key_to_link[key]
                # dta location data
                sheet.write(row_num,0, "%d %d" % (link.getStartNode().getId(), link.getEndNode().getId()), STYLE_REG)
                sheet.write(row_num,1, link.getStartNode().getId(),                 STYLE_REG)
                sheet.write(row_num,2, link.getEndNode().getId(),                   STYLE_REG)
                sheet.write(row_num,3, link.getId(),                                STYLE_REG)
                # count dracula location data
                sheet.write(row_num,4, key[0],                                      STYLE_REG)
                sheet.write(row_num,5, key[1],                                      STYLE_REG)
                sheet.write(row_num,6, key[2],                                      STYLE_REG)
                sheet.write(row_num,7, key[3],                                      STYLE_REG)
                # count data, count = [ count, starttime, period, vtype, refpos, sourcefile, project ]
                sheet.write(row_num,8, count[0],                                    STYLE_REG)
                sheet.write(row_num,9, count[1],                                    STYLE_DATE)
                sheet.write(row_num,10,count[1].year,                               STYLE_REG)
                sheet.write(row_num,11,str(sorted(count_years)),                    STYLE_REG)
                sheet.write(row_num,12,
                            datetime.time(count[1].hour,
                                          count[1].minute,
                                          count[1].second),                         STYLE_TIME)
                sheet.write(row_num,13,(count[2].seconds/60),                       STYLE_REG)
                sheet.write(row_num,14,count[3],                                    STYLE_REG)
                sheet.write(row_num,15,count[4],                                    STYLE_REG)
                sheet.write(row_num,16,count[5],                                    STYLE_REG)
                sheet.write(row_num,17,count[6],                                    STYLE_REG)

#: this_is_main
if __name__ == '__main__':

    import countdracula

    optlist, args = getopt.getopt(sys.argv[1:], "l:m:n:")
    
    if len(args) != 2:
        print USAGE
        sys.exit(2)
    
    SF_DYNAMEQ_NET_DIR          = args[0] 
    SF_DYNAMEQ_NET_PREFIX       = args[1]
    
    OUTPUT_LINK_SHAPEFILE       = None
    OUTPUT_MOVE_SHAPEFILE       = None
    OUTPUT_NODE_SHAPEFILE       = None
    
    for (opt,arg) in optlist:
        if opt=="-m":
            OUTPUT_MOVE_SHAPEFILE  = arg
        elif opt=="-l":
            OUTPUT_LINK_SHAPEFILE  = arg
        elif opt=="-n":
            OUTPUT_NODE_SHAPEFILE  = arg
                
    dta.setupLogging("attachCountsFromCountDracula.INFO.log", "attachCountsFromCountDracula.DEBUG.log", logToConsole=True)
    
    dta.VehicleType.LENGTH_UNITS= "feet"
    dta.Node.COORDINATE_UNITS   = "feet"
    dta.RoadLink.LENGTH_UNITS   = "miles"
        
    # Read the SF scenario and DTA network
    sanfranciscoScenario = dta.DynameqScenario()
    sanfranciscoScenario.read(dir=SF_DYNAMEQ_NET_DIR, file_prefix=SF_DYNAMEQ_NET_PREFIX)
    
    sanfranciscoDynameqNet = dta.DynameqNetwork(scenario=sanfranciscoScenario)
    sanfranciscoDynameqNet.read(dir=SF_DYNAMEQ_NET_DIR, file_prefix=SF_DYNAMEQ_NET_PREFIX)
    
    counts_wb = xlwt.Workbook()
    
    # Instantiate the count dracula reader and do the exports
    # Time slices here are based on what we have available (according to CountDracula's querySanFranciscoCounts.py)
    cd_reader       = countdracula.CountsDatabaseReader(pw="ReadOnly", logger=dta.DtaLogger)
    
    for suffix in ["all", "all_midweek", "recent", "recent_midweek"]:
        from_date   = None
        to_date     = None
        weekdays    = None
        
        # year range
        if suffix.find("recent") >= 0:
            from_date   = datetime.date(year=2009,month=1 ,day=1 )
            to_date     = datetime.date(year=2011,month=12,day=31)
            
        # weekdays
        if suffix.find("midweek") >= 0:
            weekdays    = [1,2,3] # Tues, Wed, Thurs
            
        dta.DtaLogger.info("Processing %s" % suffix)
        exportTurnCountsToDynameqUserDataFile   (cd_reader, sanfranciscoDynameqNet, starttime=datetime.time(16,00), 
                                                 period=datetime.timedelta(minutes=15), num_intervals=10, 
                                                 suffix=suffix, from_date=from_date, to_date=to_date, weekdays=weekdays,
                                                 all_count_workbook=counts_wb)
        exportTurnCountsToDynameqUserDataFile   (cd_reader, sanfranciscoDynameqNet, starttime=datetime.time(16,00),
                                                 period=datetime.timedelta(minutes= 5), num_intervals=24,
                                                 suffix=suffix, from_date=from_date, to_date=to_date, weekdays=weekdays,
                                                 all_count_workbook=counts_wb)
        exportMainlineCountsToDynameUserDataFile(cd_reader, sanfranciscoDynameqNet, starttime=datetime.time(16,00),
                                                 period=datetime.timedelta(minutes=60), num_intervals=2,
                                                 suffix=suffix, from_date=from_date, to_date=to_date, weekdays=weekdays,
                                                 all_count_workbook=counts_wb)
        exportMainlineCountsToDynameUserDataFile(cd_reader, sanfranciscoDynameqNet, starttime=datetime.time(16,00),
                                                 period=datetime.timedelta(minutes=15), num_intervals=10,
                                                 suffix=suffix, from_date=from_date, to_date=to_date, weekdays=weekdays,
                                                 all_count_workbook=counts_wb)

    counts_wb.save("counts_generated_%s.xls" % str(datetime.date.today()))
    
    if OUTPUT_LINK_SHAPEFILE: sanfranciscoDynameqNet.writeLinksToShp(OUTPUT_LINK_SHAPEFILE)
    if OUTPUT_MOVE_SHAPEFILE: sanfranciscoDynameqNet.writeMovementsToShp(OUTPUT_MOVE_SHAPEFILE)
    if OUTPUT_NODE_SHAPEFILE: sanfranciscoDynameqNet.writeNodesToShp(OUTPUT_NODE_SHAPEFILE)
    