__copyright__   = "Copyright 2012 SFCTA"
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
import datetime
import dta
import itertools
import os
import sys

# requires pyproj for projecting lat,long to the SF network coordinate space
# requires transitfeed for parsing the GTFS


USAGE = r"""

 python importGTFS.py dynameq_net_dir dynameq_net_prefix gtfs_file.zip
 
 e.g.
 
 python importGTFS.py . sf Y:\dta\SanFrancisco\2010\transit\google_transit_sfmta_20120609_20120914.zip
 
 This script reads the `General Transit Feed Specification <https://developers.google.com/transit/gtfs/>`_
 and converts the transit lines into DTA transit lines, outputting them in Dynameq format as 
 [dynameq_net_dir]\[dynameq_net_prefix]_ptrn.dqt
 
 Each trip is input as a separate line with a large headway, so it runs once.  This is because
 future development will modify dwell times based on the ridership of that particular trip.
 
 The script also outputs sf_gtfs_lines.shp for debugging.
"""
 
def convertLongitudeLatitudeToXY(longitude,latitude):
    from pyproj import Proj
    """
    Converts longitude and latitude to an x,y coordinate pair in
    NAD83 Datum (most of our GIS and CUBE files)
    
    Returns (x,y) in feet.
    """
    FEET_TO_METERS = 0.3048006096012192

    p = Proj(proj  = 'lcc',
             datum = "NAD83",
             lon_0 = "-120.5",
             lat_1 = "38.43333333333",
             lat_2 = "37.066666666667",
             lat_0 = "36.5",
             ellps = "GRS80",
             units = "m",
             x_0   = 2000000,
             y_0   = 500000) #use kwargs
    x_meters,y_meters = p(longitude,latitude,inverse=False,errcheck=True)

    return (x_meters/FEET_TO_METERS,y_meters/FEET_TO_METERS)

def addStopIdToLinkToDict(stop, network, stopid_to_link):
    """
    Maps the given *stop* (a :py:class:`transitfeed.stop` instance) to a link in 
    the given *network* (a :py:class:`Network` instance).
    
    Sets the 5-tuple: ``(x, y, roadlink, distance, portion_along_link)`` into the *stopid_to_link* dictionary
    for the stop id key.  If something is already there, then this does nothing.
    
    The last three values will be None if no roadlink is found.
    """
    if stop['stop_id'] in stopid_to_link: return
    
    QUICK_DIST = 200 # feet
            
    (x,y) = convertLongitudeLatitudeToXY(stop['stop_lon'], stop['stop_lat'])

    closest_tuples = network.findNRoadLinksNearestCoords(x,y, n=3, quick_dist=QUICK_DIST)
    
    # none found - bummer!
    if len(closest_tuples) == 0:
        stopid_to_link[stop['stop_id']] = (x, y, None, None, None)
    else:
        # check if the stop name changes things
        stop_name_parts = stop['stop_name'].split(" ")
        stop_str = stop_name_parts[0].upper()
        
        # if the closest tuple doesn't have a matching name, let's check the other two
        if not closest_tuples[0][0].getLabel().startswith(stop_str):
            
            for close_tuple in closest_tuples[1:]:
                if close_tuple[0].getLabel().startswith(stop_str):
                    # use this because the name matches!
                    dta.DtaLogger.debug("Falling back to secondary close matched link %s for stop %s based on stop_name.  (Was %s)" %
                                        (close_tuple[0].getLabel(), stop['stop_name'], closest_tuples[0][0].getLabel()))
                    stopid_to_link[stop['stop_id']] = (x,y,close_tuple[0],close_tuple[1],close_tuple[2])
        
        # if we didn't fall back, use the first one
        if stop['stop_id'] not in stopid_to_link:
            stopid_to_link[stop['stop_id']] = (x,y,closest_tuples[0][0],closest_tuples[0][1],closest_tuples[0][2])
        
    if len(stopid_to_link) % 500 == 0:
        dta.DtaLogger.info("%5d stop ids mapped" % len(stopid_to_link))

def mapStopIdsToLinks(stoplist, network):
    """
    Pro-actively (non-lazily) fills in a stopid_to_link dictionary (see :py:func:`addStopIdToLinkDict`)
    and returns it. 
    """
    stopid_to_link = {}
    roadlinks_found = 0
    
    for stop in stoplist:
        
        addStopIdToLinkToDict(stop, network, stopid_to_link)
        if stopid_to_link[stop['stop_id']][2]: roadlinks_found += 1
        
    dta.DtaLogger.info("%d of %d stop ids mapped successfully to road links using quick_dist=%f" %
                       (roadlinks_found, len(stopid_to_link), quick_dist))
    return stopid_to_link

def writeStopsShpFile(stoplist, stopid_to_link, shapefilename):
    """
    Write stops to *shapefilename* for debugging.
    
    * *stoplist* is a list of transitfeed stops
    * *stopid_to_link* is a map of { stopid -> (x, y, roadlink, distance, portion_along_link) }
       from :py:func:`mapStopIdToLink`
    
    """
    import shapefile
    shp = shapefile.Writer(shapefile.POINT)
    shp.field("stop_id",     "N", 10)
    shp.field("stop_name",   "C", 30)
    shp.field("nearlink",    "N", 10)
    shp.field("linkdist",    "N", 15, 4)
    shp.field("linkt",       "N", 12, 8)
    
    for stop in stoplist:
        
        stopid = stop['stop_id']
        shp.point(stopid_to_link[stopid][0], stopid_to_link[stopid][1])
        shp.record(stopid, stop['stop_name'],
                   stopid_to_link[stopid][2].getId() if stopid_to_link[stopid][2] else -1,
                   "%15.4f" % stopid_to_link[stopid][3] if stopid_to_link[stopid][2] else 0,
                   "%12.8f" % stopid_to_link[stopid][4] if stopid_to_link[stopid][2] else 0)
        
    shp.save(shapefilename)
    dta.DtaLogger.info("Wrote GTFS stops to shapefile %s" % shapefilename)

def defineLinesShpFile():
    """
    Defines the fields in the transit line shapefile.  For use with :py:func:`writeLineToShapefile`.
    """
    import shapefile
    shp = shapefile.Writer(shapefile.POLYLINE)
    shp.field("route", "C", 50) # label + headsign
    return shp

def writeLineToShapefile(shp, transitline):
    """
    *shp* is the shapefile object from :py:func:`defineLinesShpFile`
    *transitline* is an instance of :py:class:`TransitLine`.
    """
    
    seg_points = []
    for segment in transitline.iterSegments():
        seg_points.extend(segment.link.getCenterLine(wholeLineShapePoints=True))
    shp.line(parts=[seg_points])
    
    label_parts = transitline.label.split("_")
    label_parts.pop() # forget the route id, trip id
    label_parts.pop()
    shp.record("_".join(label_parts))
    
    
if __name__ == "__main__":

    import transitfeed

    INPUT_DYNAMEQ_NET_DIR         = sys.argv[1]
    INPUT_DYNAMEQ_NET_PREFIX      = sys.argv[2]
    GTFS_ZIP                      = sys.argv[3]

    GTFS_ROUTE_TYPE_TO_LINE_TYPE = \
    {"Bus":         dta.TransitLine.LINE_TYPE_BUS,
     "Cable Car":   dta.TransitLine.LINE_TYPE_TRAM,
     "Tram":        dta.TransitLine.LINE_TYPE_TRAM
     }
    GTFS_ROUTE_TYPE_TO_VTYPE = \
    {"Bus":         "Motor_Std",
     "Cable Car":   "CableCar",
     "Tram":        "LRT2"
    }
    

    dta.VehicleType.LENGTH_UNITS= "feet"
    dta.Node.COORDINATE_UNITS   = "feet"
    dta.RoadLink.LENGTH_UNITS   = "miles"

    dta.setupLogging("importGTFS.INFO.log", "importGTFS.DEBUG.log", logToConsole=True)

    scenario = dta.DynameqScenario(dta.Time(0,0), dta.Time(23,0))
    scenario.read(INPUT_DYNAMEQ_NET_DIR, INPUT_DYNAMEQ_NET_PREFIX) 
    net = dta.DynameqNetwork(scenario)
    net.read(INPUT_DYNAMEQ_NET_DIR, INPUT_DYNAMEQ_NET_PREFIX)
    
    tfl = transitfeed.Loader(feed_path=GTFS_ZIP)
    schedule = tfl.Load()
    dta.DtaLogger.info("Read %s" % GTFS_ZIP)
    
    stopid_to_link = {}
    # stopid_to_link = mapStopIdsToLinks(schedule.GetStopList(), net)
    # writeStopsShpFile(schedule.GetStopList(), stopid_to_link, "sf_gtfs_stops.shp")
    line_shp = defineLinesShpFile()
        
    # Get the ServicePeriod we're interested in - we want weekday service
    service_period_tuples = schedule.GetServicePeriodsActiveEachDate(datetime.date(2012,7,10), datetime.date(2012,7,12))
    service_period = service_period_tuples[0][1][0]
    # for now, we only support one
    for (date,sps) in service_period_tuples:
        assert(len(sps) == 1)
        assert(sps[0] == service_period)
    dta.DtaLogger.info("Filtering trips to those with service id %s" % service_period.service_id)
    
    # open the output file for writing
    output_filename = os.path.join(INPUT_DYNAMEQ_NET_DIR, "sf_trn_ptrn.dqt")
    output_file = open(output_filename,mode="w+")
    output_file.write(dta.TransitLine.getDynameqFileHeaderStr())

    # iterate through the routes -- first, determine a sort order
    route_list = schedule.GetRouteList()
    route_labels = []
    for route in route_list:
        route_label = route['route_short_name'].strip() + " " + route['route_long_name'].strip()
        route_labels.append(route_label)
    
    # now iterate through the routes
    transit_line_id = 1 # we're making these up, start at 1
    line_shp_done = set() # (route_label, trip_headsign)
    for route_label in sorted(route_labels):
        
        # iterate through the trips and find those for this route
        trip_list = schedule.GetTripList()
        for trip in trip_list:
                        
            # skip if irrelevant service period
            if trip['service_id'] != service_period.service_id: continue
            route_id = trip['route_id']
            route = schedule.GetRoute(route_id)
            
            # only do the trips for the given route_label
            trip_route_label = route['route_short_name'].strip() + " " + route['route_long_name'].strip()
            if trip_route_label != route_label: continue
    
            # create the transit line
            label = "%s_%s_route%s_trip%s" % (route_label, trip['trip_headsign'], route_id, trip['trip_id'])
            stoptimes = trip.GetStopTimes()
            line_departure = dta.Time.fromSeconds(stoptimes[0].GetTimeSecs())
            
            # Skip if it's not running during simulation time
            if line_departure > scenario.endTime: continue
            if line_departure < scenario.startTime: continue
            
            route_type_str = transitfeed.Route._ROUTE_TYPES[int(route['route_type'])]['name']            
            dta.DtaLogger.debug("Processing %s (%s)" % (label, route_type_str))
            
            dta_transit_line = dta.TransitLine(net, id=transit_line_id,
                                               label=label,
                                               litype=GTFS_ROUTE_TYPE_TO_LINE_TYPE[route_type_str],
                                               vtype=GTFS_ROUTE_TYPE_TO_VTYPE[route_type_str],
                                               stime=line_departure,
                                               level=0,
                                               active=dta.TransitLine.LINE_ACTIVE,
                                               hway=60*6, #run once -- make this cleaner
                                               dep=1)
                                                           
            prev_roadlink = None
            prev_segment  = None
            for stoptime in stoptimes:
                
                stopid = stoptime.stop['stop_id']
                addStopIdToLinkToDict(stoptime.stop, net, stopid_to_link) # lazy updating
                stop_roadlink = stopid_to_link[stopid][2]
                
                if stop_roadlink == None:
                    # todo handle this better
                    continue
                
                # subsequent link - connect from previous link
                if prev_roadlink:
                    
                    if prev_roadlink == stop_roadlink:
                        # todo: split the link?
                        prev_segment.label += ",%s,%5.4f" % (stopid, stopid_to_link[stopid][4])
                        dta.DtaLogger.debug("Two stops on one link! route=%s  label=%s" % (route_label, prev_segment.label))
                        continue
                        
                    try:
                        dta.ShortestPaths.labelSettingWithLabelsOnNodes(net, 
                                                                        prev_roadlink.getEndNode(), 
                                                                        stop_roadlink.getStartNode())
                        path_nodes = dta.ShortestPaths.getShortestPathBetweenNodes(prev_roadlink.getEndNode(), 
                                                                                   stop_roadlink.getStartNode())
        
                    except:
                        dta.DtaLogger.error("Error: %s" % str(sys.exc_info()))
                        dta.DtaLogger.error("route %-25s No shortest path found from %d to %d" %
                                           (label, prev_roadlink.getEndNode(), stop_roadlink.getStartNode()))
                        continue
                    
                    node_num_list = [ prev_roadlink.getEndNode().getId() ]
                    for path_node_A, path_node_B in itertools.izip(path_nodes, path_nodes[1:]):
                        node_num_list.append(path_node_B.getId())
                        newlink = net.getLinkForNodeIdPair(path_node_A.getId(), path_node_B.getId())
                        newseg  = dta_transit_line.addSegment(newlink, 0, label="")
    
                # add this link
                prev_segment = dta_transit_line.addSegment(stop_roadlink,
                                                           label="%s,%5.4f" % (stopid, stopid_to_link[stopid][4]),
                                                           lane=dta.TransitSegment.TRANSIT_LANE_UNSPECIFIED,
                                                           dwell=30, # todo: put in a better default
                                                           stopside=dta.TransitSegment.STOP_OUTSIDE)
                prev_roadlink = stop_roadlink
                prev_segment 
    
            # check if the movements are allowed
            dta_transit_line.checkMovementsAreAllowed(enableMovement=True)
                
            output_file.write(dta_transit_line.getDynameqStr())
            transit_line_id += 1
            
            # only once per (route_label, trip_headsign)
            if (route_label, trip['trip_headsign']) not in line_shp_done:
                writeLineToShapefile(line_shp, dta_transit_line)
                line_shp_done.add( (route_label, trip['trip_headsign']) )

    output_file.close()

    net.write(".", "sf_trn")

    dta.DtaLogger.info("Wrote %8d %-16s to %s" % (transit_line_id-1, "TRANSIT LINES", output_filename))
 
    # write the lines shapefile
    line_shp.save("sf_gtfs_lines")
    dta.DtaLogger.info("Wrote GTFS lines to shapefile sf_gtfs_lines.shp")
