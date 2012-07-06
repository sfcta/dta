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


import dta
from itertools import izip
import os
import re
import shapefile
import sys 


USAGE = r"""

 python importUnsignalizedIntersections.py dynameq_net_dir dynameq_net_prefix stop_signs.shp
 
 e.g.
 
 python importUnsignalizedIntersections.py . sf Q:\GIS\Road\StopSigns\allway_stops.shp  Q:\GIS\CityGIS\TrafficControl\StopSigns\stops_signs.shp 
 
 This script reads all unsignalized intersections from shapefile and updates the priorities of the matching node accordingly.
  
 The script writes a new dynameq network that includes the new priorities as sf_stops_*.dqt
 """

def readStopSignShapefile(shapefilename):
    """
    Reads the stop sign shapefile and returns the following:
    
    { cnn -> [ record1_dict, record2_dict, ... ] }
    
    Where *record_dict* includes all the fields from the shapefile, plus `COORDS` which maps to the coordinate tuple.
    """
    sf      = shapefile.Reader(shapefilename)
    fields  = [field[0] for field in sf.fields[1:]]
    count   = 0
    nocnn_id= 1
    
    # what we're returning
    cnn_to_recordlist = {}
    for sr in sf.shapeRecords():
        
        # name the records
        sr_record_dict = dict(izip(fields, sr.record))
        
        # we expect these shapes to have one point
        if len(sr.shape.points) != 1: continue

        point = sr.shape.points[0]
        cnn   = sr_record_dict['CNN']
        if cnn == 0:
            cnn = "nocnn_%d" % nocnn_id
            nocnn_id += 1
        
        # add the point
        sr_record_dict['COORDS'] = point
        if cnn not in cnn_to_recordlist:
            cnn_to_recordlist[cnn] = []
        cnn_to_recordlist[cnn].append(sr_record_dict)
        count += 1

    dta.DtaLogger.info("Read %d unique nodes and %d stop signs from %s" % (len(cnn_to_recordlist), count, shapefilename))
    return cnn_to_recordlist
    
def cleanStreetName(streetName):
    """
    Given a streetname, this function attempts to make it uniform with the San Francisco DTA Network streetnames.
    """

    # these will be treated as regexes so you can specify ^ for the beginning of the string
    # $ for the end, wild chars, etc
    corrections = {"TWELFTH":"12TH", 
                   "ELEVENTH":"11TH",
                   "TENTH":"10TH",
                   "NINTH":"9TH",
                   "EIGHTH":"8TH",
                   "SEVENTH":"7TH",
                   "SIXTH":"6TH",
                   "FIFTH":"5TH",
                   "FOURTH":"4TH",
                   "THIRD":"3RD",
                   "SECOND":"2ND",
                   "FIRST":"1ST",
                   "3RDREET":"3RD",
                   "3RD #3":"3RD",
                   "BAYSHORE #3":"BAYSHORE",
                   "09TH":"9TH",
                   "08TH":"8TH",
                   "07TH":"7TH",
                   "06TH":"6TH",
                   "05TH":"5TH",
                   "04TH":"4TH",
                   "03RD":"3RD",
                   "02ND":"2ND",
                   "01ST":"1ST",
                   "ARMY":"CESAR CHAVEZ",
                   "DEL SUR":"DELSUR",
                   "EMBARCADERO/KING":"THE EMBARCADERO",
                   "GREAT HIGHWAY":"GREAT HWY",
                   "O'FARRELL":"O FARRELL",
                   "MARTIN L(UTHER)? KING":"MLK",
                   "MCALLISTER":"MC ALLISTER",
                   "MCKINNON":"MC KINNON",
                   "MIDDLEPOINT":"MIDDLE POINT",
                   "MT VERNON":"MOUNT VERNON",
                   "^ST ":"SAINT ",            
                   "VAN NESSNUE":"VAN NESS",                   
                   "WEST GATE":"WESTGATE",
                   }

    cleaned_name = streetName.strip()
    for wrongName, rightName in corrections.items():
        cleaned_name = re.sub(wrongName, rightName, cleaned_name)
    return cleaned_name

def checkStreetnameConsistency(dta_node_id, dta_streets, stopsign_streets, stopsign_x_streets):
    """
    Verifies that the stopsign streets and the stopsign_x_streets are subsets of dta_streets.
    Warns about violations.
    
    *dta_node_id* is an integer, just used for logging.  All three  remaining inputs are lists of strings.
    """
    # these are what we're checking
    # check once, and "stopsign street" overrides "stopsign X street"
    checkname_to_checktype = {}
    for stopsign_x_street in stopsign_x_streets:
        checkname_to_checktype[cleanStreetName(stopsign_x_street)] = "stopsign X street"

    for stopsign_street in stopsign_streets:
        checkname_to_checktype[cleanStreetName(stopsign_street)] = "stopsign street"
    
    # actually check them now
    for checkname,checktype in checkname_to_checktype.iteritems():

        found = False
        for dta_street in dta_streets:
            # if any of the dta_streets start with it, coo
            if dta_street.startswith(checkname):
                found = True
                break
            
        if not found:    
            dta.DtaLogger.warn("Streetname consistency check: node %d doesn't have %s [%s]  (Searched %s)" % 
                               (dta_node_id, checktype, checkname, str(dta_streets)))

def updateNodePriority(net,matchedNodes):
    conflictNodes = []
    # If node was matched 4 or more times, it is set to all-way stop.  If node was matched fewer times, it is set to two-way stop.
    for node in net.iterRoadNodes():
        if node in matchedNodes:
            if matchedNodes.count(node)>=node.getNumIncomingLinks():
                node._priority = 1
            elif matchedNodes.count(node)<node.getNumIncomingLinks() and matchedNodes.count(node)>=1:
                if float(matchedNodes.count(node))/float(node.getNumIncomingLinks())>0.5:
                    node._priority=1
                else:
                    node._priority = 2
                    maxFac = 100
                    maxFacName = ""
                    for links in node.iterIncomingLinks():
                        streetLabel = str(node._label)
                        splitval = streetLabel.find("&")
                        streetName = streetLabel[:splitval]
                        streetName = cleanStreetName(streetName)
                        #dta.DtaLogger.info("TW stop at node %s has link %s with facility type %s and %s has priority." % (node.getId(),links.getLabel(),links.getFacilityType(),streetName))
                        if links.getFacilityType()==maxFac:
                            if links.getLabel()==maxFacName:
                                continue
                            else:
                                dta.DtaLogger.error("Two-way stop %s at %s has conflicting facility types.  Set to four-way." % (node.getId(),node.getStreetNames()))
                                node._priority = 1
                                if node not in conflictNodes:
                                    conflictNodes.append(node)
                                #for link2 in node.iterIncomingLinks():
                                    #dta.DtaLogger.error("TW stop tagged %d of %d times at node %s at %d, %d has link %s with facility type %s and %s has priority." % (matchedNodes.count(node),node.getNumIncomingLinks(),node.getId(),node.getX(),node.getY(),link2.getLabel(),link2.getFacilityType(),streetName))
                        elif links.getFacilityType()<maxFac:
                            maxFac = links.getFacilityType()
                            maxFacName = links.getLabel()
    dta.DtaLogger.info("%d stops are two-way with facility type conflicts" % len(conflictNodes))
    return True

#: this_is_main                
if __name__ == "__main__":

    if len(sys.argv) != 4:
        print USAGE
        sys.exit(2)

    INPUT_DYNAMEQ_NET_DIR         = sys.argv[1]
    INPUT_DYNAMEQ_NET_PREFIX      = sys.argv[2]
    STOP_SHAPEFILE                = sys.argv[3]
    
    # The SanFrancisco network will use feet for vehicle lengths and coordinates, and miles for link lengths
    dta.VehicleType.LENGTH_UNITS= "feet"
    dta.Node.COORDINATE_UNITS   = "feet"
    dta.RoadLink.LENGTH_UNITS   = "miles"

    dta.setupLogging("importUnsignalizedIntersections.INFO.log", "importUnsignalizedIntersections.DEBUG.log", logToConsole=True)

    scenario = dta.DynameqScenario(dta.Time(0,0), dta.Time(23,0))
    scenario.read(INPUT_DYNAMEQ_NET_DIR, INPUT_DYNAMEQ_NET_PREFIX) 
    net = dta.DynameqNetwork(scenario)
    net.read(INPUT_DYNAMEQ_NET_DIR, INPUT_DYNAMEQ_NET_PREFIX)

    cnn_to_recordlist = readStopSignShapefile(STOP_SHAPEFILE)
    
    count_notmapped     = 0
    count_hassignal     = 0
    count_moreincoming  = 0
    count_allway        = 0
    count_twoway        = 0
    count_allway_fromtwo= 0
    # the cnn is unique per intersection so loop through each intersection with stop signs
    for cnn, stopsignlist in cnn_to_recordlist.iteritems():
        
        # these are the streets for the stop signs
        stopsign_streets   = []
        stopsign_x_streets = []
        for stopsign in stopsignlist:
            if stopsign['STREET'] not in stopsign_streets:
                stopsign_streets.append(stopsign['STREET'])
            if stopsign['X_STREET'] not in stopsign_x_streets:
                stopsign_x_streets.append(stopsign['X_STREET'])

        # find the nearest node to this                
        (min_dist, roadnode) = net.findNodeNearestCoords(stopsignlist[0]['COORDS'][0], stopsignlist[0]['COORDS'][1], quick_dist=100.0)
        
        if roadnode == None:
            dta.DtaLogger.warn("Could not find road node near %s and %s in the stop sign file" % (stopsignlist[0]['STREET'], stopsignlist[0]['X_STREET']))
            count_notmapped += 1
            continue

        dta.DtaLogger.debug("min_dist = %.3f roadnodeID=%d roadnode_streets=%s stopsign_streets=%s" % 
                            (min_dist, roadnode.getId(), str(roadnode.getStreetNames(incoming=True, outgoing=False)),
                             str(stopsign_streets)))

        # streetname checking; warn if stopsign_streets are not found in the roadnode_streets
        checkStreetnameConsistency(roadnode.getId(), roadnode.getStreetNames(incoming=True, outgoing=False),
                                   stopsign_streets, stopsign_x_streets)
                        
        # if the roadnode is already a signalized intersection, move on
        if roadnode.hasTimePlan():
            dta.DtaLogger.warn("Roadnode %d already has signal. Ignoring stop sign info." % roadnode.getId())
            count_hassignal += 1
            continue
        
        # if the number of incoming links == the number of stop signs, mark it an all way stop
        if len(stopsignlist) > roadnode.getNumIncomingLinks():
            dta.DtaLogger.warn("Roadnode %d missing incoming links?  More stop signs than incoming links" % roadnode.getId())
            count_moreincoming += 1 # not exclusive count!
            
        if  len(stopsignlist) >= roadnode.getNumIncomingLinks():
            roadnode.setAllWayStopControl()
            count_allway += 1
            continue
        
        # two way stop
        # todo: look at the matching facility type issue and set up custom priorities

        # collect the through movements
        through_movements = []        
        for inlink in roadnode.iterIncomingLinks():
            try:
                through_movements.append(inlink.getThruTurn())
            except:
                pass
        
        # for now: set to all way stops if multiple incoming through movements conflict and 
        # their incoming links have the same facility type
        allway   = False        
        for mov1 in through_movements:
            for mov2 in through_movements:
                if mov1 == mov2: continue
                if not mov1.isInConflict(mov2): continue
                # now they're in conflict
                
                if mov1.getIncomingLink().getFacilityType() == mov2.getIncomingLink().getFacilityType():
                    # and equivalent priority
                    roadnode.setAllWayStopControl()
                    allway = True
                    count_allway_fromtwo += 1
                    break
            # alway - done already
            if allway: break 
            
        if not allway: 
            roadnode.setTwoWayStopControl()
            count_twoway += 1
        
    dta.DtaLogger.info("Read %d stop-sign intersections" % len(cnn_to_recordlist))
    dta.DtaLogger.info("  %-4d: Failed to map" % count_notmapped)
    dta.DtaLogger.info("  %-4d: Ignored because they're signalized" % count_hassignal)
    dta.DtaLogger.info("  %-4d: Setting as allway-stop (including %d questionable, with more stop signs than incoming links)" % (count_allway, count_moreincoming))
    dta.DtaLogger.info("  %-4d: Setting as allway-stop in lieu of custom priorities" % count_allway_fromtwo)
    dta.DtaLogger.info("  %-4d: Setting as twoway-stop" % count_twoway)
    
    net.write(".", "sf_stops")

    net.writeNodesToShp("sf_stops_nodes")
    net.writeLinksToShp("sf_stops_links")         
    

            
            

