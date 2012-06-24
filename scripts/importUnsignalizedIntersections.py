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

#import json
import pdb
import math

from collections import defaultdict
import os
import re
from itertools import izip, chain
import sys 

import shapefile

from dta.MultiArray import MultiArray

import dta
from dta.DynameqScenario import DynameqScenario
from dta.DynameqNetwork import DynameqNetwork
from dta.Algorithms import pairwise, any2, all2 
from dta.DtaError import DtaError
from dta.Logger import DtaLogger
from dta.Movement import Movement
from dta.Network import Network
from dta.Node import Node
from dta.RoadLink import RoadLink
from dta.RoadNode import RoadNode
from dta.Utils import lineSegmentsCross, getMidPoint


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
    
    # what we're returning
    cnn_to_recordlist = {}
    for sr in sf.shapeRecords():
        
        # name the records
        sr_record_dict = dict(izip(fields, sr.record))
        
        # we expect these shapes to have one point
        if len(sr.shape.points) != 1: continue

        point = sr.shape.points[0]
        cnn   = sr_record_dict['CNN']
        
        # add the point
        sr_record_dict['COORDS'] = point
        if cnn not in cnn_to_recordlist:
            cnn_to_recordlist[cnn] = []
        cnn_to_recordlist[cnn].append(sr_record_dict)
        count += 1

    DtaLogger.info("Read %d unique nodes and %d stop signs from %s" % (len(cnn_to_recordlist), count, shapefilename))
    return cnn_to_recordlist
    
def cleanStreetName(streetName):

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
                   "O'FARRELL":"O FARRELL",
                   "3RDREET":"3RD",
                   "EMBARCADERO/KING":"THE EMBARCADERO",
                   "VAN NESSNUE":"VAN NESS",
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
                   "WEST GATE":"WESTGATE",
                   "MIDDLEPOINT":"MIDDLE POINT",
                   "ST FRANCIS":"SAINT FRANCIS",
                   "MT VERNON":"MOUNT VERNON"}


    itemsToRemove = [" STREETS",
                     " STREET",
                     " STS.",
                     " STS",
                     " ST.",
                     " ST",
                     " ROAD",
                     " RD.",
                     " RD",
                     " AVENUE",
                     " AVE.",
                     " AVES",
                     " AVE",
                     " BLVD.",
                     " BLVD",
                     " BOULEVARD",
                     "MASTER:",
                     " DRIVE",
                     " DR.",
                     " WAY",
                     " WY",
                     " CT",
                     " TERR",
                     " HWY"]

    newStreetName = streetName.strip()
    for wrongName, rightName in corrections.items():
        if wrongName in streetName:
            newStreetName = streetName.replace(wrongName, rightName)
        if streetName == 'EMBARCADERO':
            newStreetName = "THE EMBARCADERO"
        if streetName.endswith(" DR"):
            newStreetName = streetName[:-3]
        if streetName.endswith(" AV"):
            newStreetName = streetName[:-3]

    for item in itemsToRemove:
        if item in newStreetName:
            newStreetName = newStreetName.replace(item, "")

    return newStreetName.strip()


def cleanStreetNames(streetNames):
    """Accept street names as a list and return a list 
    with the cleaned street names"""
    
    newStreetNames = map(cleanStreetName, streetNames)
    if len(newStreetNames) > 1 and newStreetNames[0] == "":
        newStreetNames.pop(0)
    return newStreetNames

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
    # the cnn is unique per intersection so loop through each intersection with stop signs
    for cnn, stopsignlist in cnn_to_recordlist.iteritems():
        
        # these are the streets for the stop signs
        stopsign_streets = []
        for stopsign in stopsignlist:
            if stopsign['STREET'] not in stopsign_streets:
                stopsign_streets.append(stopsign['STREET'])

        # find the nearest node to this                
        (min_dist, roadnode) = net.findNodeNearestCoords(stopsignlist[0]['COORDS'][0], stopsignlist[0]['COORDS'][1], quick_dist=100.0)
        
        if roadnode == None:
            DtaLogger.warn("Could not find road node near %s and %s in the stop sign file" % (stopsignlist[0]['STREET'], stopsignlist[0]['X_STREET']))
            count_notmapped += 1
            continue

        DtaLogger.debug("min_dist = %.3f roadnodeID=%d roadnode_streets=%s stopsign_streets=%s" % 
                        (min_dist, roadnode.getId(), str(roadnode.getStreetNames(incoming=True, outgoing=False)),
                         str(stopsign_streets)))

        # todo: streetname checking; make sure that the stopsign_streets are a subset of the roadnode_streets
                        
        # if the roadnode is already a signalized intersection, move on
        if roadnode.hasTimePlan():
            DtaLogger.warn("Roadnode %d already has signal. Ignoring stop sign info." % roadnode.getId())
            count_hassignal += 1
            continue
        
        # if the number of incoming links == the number of stop signs, mark it an all way stop
        if len(stopsignlist) > roadnode.getNumIncomingLinks():
            DtaLogger.warn("Roadnode %d missing incoming links?  More stop signs than incoming links" % roadnode.getId())
            count_moreincoming += 1 # not exclusive count!
            
        if  len(stopsignlist) >= roadnode.getNumIncomingLinks():
            roadnode.setAllWayStopControl()
            count_allway += 1
            continue
        
        # two way stop
        # todo: look at the matching facility type issue and set up custom priorities
        roadnode.setTwoWayStopControl()
        count_twoway += 1
        
    dta.DtaLogger.info("Read %d stop-sign intersections" % len(cnn_to_recordlist))
    dta.DtaLogger.info("  %-4d: Failed to map" % count_notmapped)
    dta.DtaLogger.info("  %-4d: Ignored because they're signalized" % count_hassignal)
    dta.DtaLogger.info("  %-4d: Setting as allway-stop (including %d questionable, with more stop signs than incoming links)" % (count_allway, count_moreincoming))
    dta.DtaLogger.info("  %-4d: Setting as twoway-stop" % count_twoway)
    
    net.write(".", "sf_stops")

        
    

            
            

