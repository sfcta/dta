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

import csv 
import difflib
from collections import defaultdict
import os
import pickle
import re
import xlrd
from itertools import izip, chain
import sys 

import shapefile
import datetime

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

USAGE = r"""

 python importUnsignalizedIntersections.py dynameq_net_dir dynameq_net_prefix four_way_stop_fil all_stop_fil 
 
 e.g.
 
 python importUnsignalizedIntersections.py . sf Q:\GIS\Road\StopSigns\allway_stops.shp  Q:\GIS\Road\StopSigns\stop_signs.shp 
 
 This script reads all unsignalized intersections from shapefiles and updates the priorities of the matching node accordingly.
  
 The script writes a new dynameq network that includes the new priorities
 """

def readAWSFromShapefile(self,nodesShpFilename, nodeVariableNames,
                 nodeGeometryTypeEvalStr,
                 nodeControlEvalStr,
                 nodePriorityEvalStr,
                 nodeLabelEvalStr,
                 nodeLevelEvalStr):

    sf = shapefile.Reader(nodesShpFilename)
    shapes = sf.shapes()
    records = sf.records()

    fields = [field[0] for field in sf.fields[1:]]
    for shape, recordValues in izip(shapes, records):
        x, y = shape.points[0]
        localsdict = dict(izip(fields, recordValues))
        n = int(localsdict["ObjectID"])
            
        newNode = None
        newNode = RoadNode(id=n,x=x,y=y,
                            geometryType=eval(nodeGeometryTypeEvalStr, globals(), localsdict),
                            control=eval(nodeControlEvalStr, globals(), localsdict),
                            priority=eval(nodePriorityEvalStr, globals(), localsdict),
                            label=str(localsdict["Intersecti"]),
                            level=eval(nodeLevelEvalStr, globals(), localsdict))

        self.append(newNode)

def readOthFromShapefile(self,priorityStreets,nodesShpFilename, nodeVariableNames,
                 nodeGeometryTypeEvalStr,
                 nodeControlEvalStr,
                 nodePriorityEvalStr,
                 nodeLabelEvalStr,
                 nodeLevelEvalStr):

    sf = shapefile.Reader(nodesShpFilename)
    shapes = sf.shapes()
    records = sf.records()

    fields = [field[0] for field in sf.fields[1:]]
    for shape, recordValues in izip(shapes, records):
        if len(shape.points) == 0:
            dta.DtaLogger.error("No shape points for ID = %d, intersection = %s" % (int(localsdict["ID"]),str(localsdict["CONCATENAT"])))
            continue
        x, y = shape.points[0]
        localsdict = dict(izip(fields, recordValues))
        n = int(localsdict["ID"])
        interPriority = str(localsdict["X_STREET"])+","+str(localsdict["STREET"])
            
        newNode = None
        newNode = RoadNode(id=n,x=x,y=y,
                            geometryType=eval(nodeGeometryTypeEvalStr, globals(), localsdict),
                            control=eval(nodeControlEvalStr, globals(), localsdict),
                            priority=eval(nodePriorityEvalStr, globals(), localsdict),
                            label=str(localsdict["CONCATENAT"]),
                            level=eval(nodeLevelEvalStr, globals(), localsdict))

        self.append(newNode)
        priorityStreet.append(interPriority)

def matchStopNodes(self,net,matchedNodes,matchedAllNodes):
    foundNodeMatch = False
    for node in net.iterRoadNodes():
        if abs(node.getX()-stop.getX())<2 and abs(node.getY()-stop.getY())<1:
            if node in matchedNodes:
                foundNodeMatch = True
                matchedNodes.append(node)
                #dta.DtaLogger.debug("Four-way stop %s at %s was matched to node %s (already matched) from (x,y)" % (stop.getId(),stop._label,node.getStreetNames()))
                return True
                continue
            else:
                node._priority = stop._priority
                node._control = stop._control
                matchedNodes.append(node)
                foundNodeMatch = True
                dta.DtaLogger.info("Stop %s at %s was matched to node %s from (x,y)" % (stop.getId(),str(stop._label).strip(),node.getStreetNames()))
                return True
            if node not in matchedAllNodes:
                matchedAllNodes.append(node)
        else:
            continue
                                    
    return foundNodeMatch 

def matchStopLinks(self,net,matchedNodes,matchedAllNodes):
    foundLinkMatch = False
    streetNamesSet = []
    streetLabel = str(stop._label)
    splitval = streetLabel.find("&")
    streetNamesSet.append(streetLabel[:splitval])
    streetNamesSet.append(streetLabel[splitval+1:])
    streetNamesSet = [cleanStreetName(sn) for sn in streetNamesSet]

    #dta.DtaLogger.debug("Street Name Set = %s" % str([streetName for streetName in streetNamesSet]))
    
    for node in net.iterRoadNodes():
        streetsMatched = 0
        baseStreetNames = node.getStreetNames()
        baseStreetNames = [cleanStreetName(bs) for bs in baseStreetNames]
        if len(baseStreetNames) < len(streetNamesSet):
            continue
        for streetName in streetNamesSet:
            if streetName in baseStreetNames:
                streetsMatched +=1
            else:
                continue
        if streetsMatched == len(streetNamesSet):
            if node in matchedNodes:
                matchedNodes.append(node)
                #dta.DtaLogger.debug("Four-way stop %s at %s was matched to node %s (already matched)" % (stop.getId(),stop._label,node.getStreetNames()))
                foundLinkMatch = True
                return True
                continue
            else:
                node._priority = stop._priority
                node._control = stop._control
                matchedNodes.append(node)
                foundLinkMatch = True
                dta.DtaLogger.info("Stop %s at %s was matched to node %s" % (stop.getId(),str(stop._label).strip(),node.getStreetNames()))
                return True
            if node not in matchedAllNodes:
                matchedAllNodes.append(node)

        else:
            continue
    return foundLinkMatch

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
                   "ST FRANCIS":"SAINT FRANCIS"}


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
    # If node was matched 4 or more times, it is set to all-way stop.  If node was matched fewer times, it is set to two-way stop.

    for node in net.iterRoadNodes():
        if node in matchedNodes:
            if matchedNodes.count(node)>=4:
                node._priority = "PRIORITY_TEMPLATE_AWSC"
            elif matchedNodes.count(node)<4:
                node._priority = "PRIORITY_TEMPLATE_TWSC"
    return True
                
    

if __name__ == "__main__":

    if len(sys.argv) < 3:
        print USAGE
        sys.exit(2)

    INPUT_DYNAMEQ_NET_DIR         = sys.argv[1]
    INPUT_DYNAMEQ_NET_PREFIX      = sys.argv[2]
    ALL_WAY_STOPS                 = sys.argv[3]
    OTHER_STOPS                   = sys.argv[4]
    
    # The SanFrancisco network will use feet for vehicle lengths and coordinates, and miles for link lengths
    dta.VehicleType.LENGTH_UNITS= "feet"
    dta.Node.COORDINATE_UNITS   = "feet"
    dta.RoadLink.LENGTH_UNITS   = "miles"

    dta.setupLogging("importUnsignalizedIntersections.INFO.log", "importUnsignalizedIntersections.DEBUG.log", logToConsole=True)

    scenario = dta.DynameqScenario(dta.Time(0,0), dta.Time(23,0))
    scenario.read(INPUT_DYNAMEQ_NET_DIR, INPUT_DYNAMEQ_NET_PREFIX) 
    net = dta.DynameqNetwork(scenario)
    net.read(INPUT_DYNAMEQ_NET_DIR, INPUT_DYNAMEQ_NET_PREFIX)

    # Import other stops (two-way and four-way) shape file
    othStopShapefile = OTHER_STOPS 
    otherStops = []
    priorityStreet = []

    readOthFromShapefile(otherStops,priorityStreet,
        nodesShpFilename=othStopShapefile,
        nodeVariableNames=["ID","STREET","X_STREET","CONCATENAT"],
        nodeGeometryTypeEvalStr          = "Node.GEOMETRY_TYPE_INTERSECTION",
        nodeControlEvalStr               = "RoadNode.CONTROL_TYPE_UNSIGNALIZED",
        nodePriorityEvalStr              = "RoadNode.PRIORITY_TEMPLATE_TWSC",
        nodeLabelEvalStr                 = "None",
        nodeLevelEvalStr                 = "None" )
    matchedAllNodes = []
    matchedOthNodes = []
    readOStopNodes = []
    foundOStopNodes = []
    # Try to match stops to nodes using X & Y coordinates, and if that fails, using link names
    for stop in otherStops:
        readOStopNodes.append(stop)
        foundStopNode = matchStopNodes(stop,net,matchedOthNodes, matchedAllNodes)
        if foundStopNode == False:
            foundStopLinks = matchStopLinks(stop,net,matchedOthNodes, matchedAllNodes)
            if foundStopLinks == False:
                dta.DtaLogger.error("Cannot match four-way stop %s at %s" % (stop.getId(),stop._label))
                continue
            else:
                foundOStopNodes.append(stop)
        else:
            foundOStopNodes.append(stop)
            
    udpatedPriorities = updateNodePriority(net,matchedOthNodes)

                
    dta.DtaLogger.info("Number of other stop nodes read in = %d" % len(readOStopNodes))
    dta.DtaLogger.info("Number of other stop nodes matched = %d" % len(foundOStopNodes))

    allStopShapefile = ALL_WAY_STOPS
    allwaysStops = []
    # Import all-way stops shape file

    readAWSFromShapefile(allwaysStops,
        nodesShpFilename=allStopShapefile,
        nodeVariableNames=["ObjectID","X","Y","Intersecti"],
        nodeGeometryTypeEvalStr          = "Node.GEOMETRY_TYPE_INTERSECTION",
        nodeControlEvalStr               = "RoadNode.CONTROL_TYPE_UNSIGNALIZED",
        nodePriorityEvalStr              = "RoadNode.PRIORITY_TEMPLATE_AWSC",
        nodeLabelEvalStr                 = "None",
        nodeLevelEvalStr                 = "None" )

    matchedNodes = []
    readAWStopNodes = []
    foundAWStopNodes = []
    # Try to match stops to nodes using X & Y coordinates, and if that fails, using link names
    for stop in allwaysStops:
        readAWStopNodes.append(stop)
        foundStopNode = matchStopNodes(stop,net,matchedNodes,matchedAllNodes)
        if foundStopNode == False:
            foundStopLinks = matchStopLinks(stop,net,matchedNodes,matchedAllNodes)
            if foundStopLinks == False:
                dta.DtaLogger.error("Cannot match four-way stop %s at %s" % (stop.getId(),stop._label))
                continue
            else:
                foundAWStopNodes.append(stop)
        else:
            foundAWStopNodes.append(stop)

    dta.DtaLogger.info("Number of other stop nodes read in = %d" % len(readOStopNodes))
    dta.DtaLogger.info("Number of other stop nodes matched = %d" % len(foundOStopNodes))
                
    dta.DtaLogger.info("Number of all-way stop nodes read in = %d" % len(readAWStopNodes))
    dta.DtaLogger.info("Number of all-way stop nodes matched = %d" % len(foundAWStopNodes))

    dta.DtaLogger.info("Number of nodes updated with stops = %d" % len(matchedAllNodes))

    net.write(".", "sf_stops")

        
    

            
            

