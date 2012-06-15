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

 python importUnsignalizedIntersections.py dynameq_net_dir dynameq_net_prefix four_way_stop_fil all_stop_fil 
 
 e.g.
 
 python importUnsignalizedIntersections.py . sf Q:\GIS\Road\StopSigns\allway_stops.shp  Q:\GIS\Road\StopSigns\stop_signs.shp 
 
 This script reads all unsignalized intersections from shapefiles and updates the priorities of the matching node accordingly.
  
 The script writes a new dynameq network that includes the new priorities
 """

class StopNode(Node):
    """
    A Road Node subclass that represents a stop sign from a shapefile that is used to updated Road Node priorities.
    """
    #: the intersection is not signalized
    CONTROL_TYPE_UNSIGNALIZED       = 0
    #: the intersection is signalized
    CONTROL_TYPE_SIGNALIZED         = 1
    #: all control types
    CONTROL_TYPES                   = [CONTROL_TYPE_UNSIGNALIZED,
                                       CONTROL_TYPE_SIGNALIZED, 11]
    

    #: No template: either a signalized or unsignalized junction, where there is no yielding of any
    #: kind, and the permitted capacity is equal to the protected capacity. 
    PRIORITY_TEMPLATE_NONE          = 0
    
    #: All Way Stop Control - an intersection with a stop sign on every approach
    PRIORITY_TEMPLATE_AWSC          = 1
    
    #: Two Way Stop Control - an intersection at which a minor street crosses a major street and
    #: only the minor street is stop-controlled
    PRIORITY_TEMPLATE_TWSC          = 2
    
    #: A junction on a roundabout at which vehicles enter the roundabout. Vehicles entering the
    #: roundabout must yield to those already on the roundabout (by convention in most countries).
    PRIORITY_TEMPLATE_ROUNDABOUT    = 3
    
    #: An uncontrolled (unsignalized) junction at which a minor street must yield to the major street,
    #: which may or may not be explicitly marked with a Yield sign. 
    PRIORITY_TEMPLATE_MERGE         = 4
    
    #: Any signalized intersection (three-leg, four-leg, etc.). For right-side driving, left-turn
    #: movements yield to opposing through traffic and right turns, and right turns yield to the
    #: conflicting through traffic (if applicable). For left-side driving, the rules are the same but reversed.
    PRIORITY_TEMPLATE_SIGNALIZED    = 11
    
    #: For each control type, a list of available Capacity/Priority templates is provided.
    #: Choosing a template from the list will automatically provide follow-up time values with
    #: corresponding permitted capacity values in the movements table below, and define all movement
    #: priority relationships at the node with corresponding gap acceptance values.     
    PRIORITY_TEMPLATES              = [PRIORITY_TEMPLATE_NONE,
                                       PRIORITY_TEMPLATE_AWSC,
                                       PRIORITY_TEMPLATE_TWSC,
                                       PRIORITY_TEMPLATE_ROUNDABOUT,
                                       PRIORITY_TEMPLATE_MERGE,
                                       PRIORITY_TEMPLATE_SIGNALIZED]
        
    def __init__(self, id, x, y, geometryType, control, priority, label=None, level=None):
        """
        Constructor.
        
         * *id* is a unique identifier (unique within the containing network), an integer
         * *x* and *y* are coordinates in the units specified by :py:attr:`Node.COORDINATE_UNITS`
         * *geometryType* is one of :py:attr:`Node.GEOMETRY_TYPE_INTERSECTION` or 
           :py:attr:`Node.GEOMETRY_TYPE_JUNCTION`
         * *control* is one of :py:attr:`RoadNode.CONTROL_TYPE_UNSIGNALIZED` or 
           :py:attr:`RoadNode.CONTROL_TYPE_SIGNALIZED`
         * *priority* is one of
         
           * :py:attr:`RoadNode.PRIORITY_TEMPLATE_NONE`
           * :py:attr:`RoadNode.PRIORITY_TEMPLATE_AWSC`
           * :py:attr:`RoadNode.PRIORITY_TEMPLATE_TWSC`
           * :py:attr:`RoadNode.PRIORITY_TEMPLATE_ROUNDABOUT`
           * :py:attr:`RoadNode.PRIORITY_TEMPLATE_MERGE`
           * :py:attr:`RoadNode.PRIORITY_TEMPLATE_SIGNALIZED`
                                       
         * *label* is a string, for readability.  If None passed, will default to "label [id]"
         * *level* is for vertical alignment.  More details TBD.  If None passed, will use default.  
        """
        if geometryType not in [Node.GEOMETRY_TYPE_INTERSECTION, Node.GEOMETRY_TYPE_JUNCTION]:
            raise DtaError("RoadNode initialized with invalid type: %d" % type)
        
        if control not in StopNode.CONTROL_TYPES:
            raise DtaError("RoadNode initailized with invalid control: %d" % control)
        
        Node.__init__(self, id, x, y, geometryType, label, level)

        self._control    = control
        self._priority   = priority
        self._label = label
        


    def matchStopNodes(self,net,matchedNodes,matchedAllNodes):
        foundNodeMatch = False
        for node in net.iterRoadNodes():
            if node._control==1:
                continue
            if abs(node.getX()-self.getX())<2 and abs(node.getY()-self.getY())<1:
                if node not in matchedAllNodes:
                    matchedAllNodes.append(node)
                if node in matchedNodes:
                    foundNodeMatch = True
                    matchedNodes.append(node)
                    #dta.DtaLogger.debug("Four-way stop %s at %s was matched to node %s (already matched) from (x,y)" % (stop.getId(),stop._label,node.getStreetNames()))
                    return True
                    continue
                else:
                    node._priority = self._priority
                    node._control = self._control
                    node._label = self._label
                    matchedNodes.append(node)
                    foundNodeMatch = True
                    dta.DtaLogger.debug("Stop %s at %s was matched to node %s from (x,y)" % (stop.getId(),str(stop._label).strip(),node.getStreetNames()))
                    return True

            else:
                continue
                                    
        return foundNodeMatch 

    def matchStopLinks(self,net,matchedNodes,matchedAllNodes):
        foundLinkMatch = False
        streetNamesSet = []
        streetLabel = str(self._label)
        splitval = streetLabel.find("&")
        streetNamesSet.append(streetLabel[:splitval])
        streetNamesSet.append(streetLabel[splitval+1:])
        streetNamesSet = [cleanStreetName(sn) for sn in streetNamesSet]

        #dta.DtaLogger.debug("Street Name Set = %s" % str([streetName for streetName in streetNamesSet]))
    
        for node in net.iterRoadNodes():
            if node._control==1:
                continue
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
                if node not in matchedAllNodes:
                    matchedAllNodes.append(node)
                if node in matchedNodes:
                    matchedNodes.append(node)
                    #dta.DtaLogger.debug("Four-way stop %s at %s was matched to node %s (already matched)" % (stop.getId(),stop._label,node.getStreetNames()))
                    foundLinkMatch = True
                    return True
                    continue
                else:
                    node._priority = self._priority
                    node._control = self._control
                    node._label = self._label
                    matchedNodes.append(node)
                    foundLinkMatch = True
                    dta.DtaLogger.debug("Stop %s at %s was matched to node %s" % (stop.getId(),str(stop._label).strip(),node.getStreetNames()))
                    return True

            else:
                continue
        return foundLinkMatch

def readAWSFromShapefile(stops,nodesShpFilename, nodeVariableNames,
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
        newNode = StopNode(id=n,x=x,y=y,
                        geometryType=eval(nodeGeometryTypeEvalStr, globals(), localsdict),
                        control=eval(nodeControlEvalStr, globals(), localsdict),
                        priority=eval(nodePriorityEvalStr, globals(), localsdict),
                        label=str(localsdict["Intersecti"]),
                        level=eval(nodeLevelEvalStr, globals(), localsdict))

        stops.append(newNode)

def readOthFromShapefile(stops,priorityStreets,nodesShpFilename, nodeVariableNames,
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
            x, y = 0,0
        else:
            x, y = shape.points[0]


        localsdict = dict(izip(fields, recordValues))
        n = int(localsdict["ID"])
        interPriority = str(localsdict["X_STREET"])+"&"+str(localsdict["STREET"])
            
        newNode = None
        newNode = StopNode(id=n,x=x,y=y,
                        geometryType=eval(nodeGeometryTypeEvalStr, globals(), localsdict),
                        control=eval(nodeControlEvalStr, globals(), localsdict),
                        priority=eval(nodePriorityEvalStr, globals(), localsdict),
                        label=interPriority,
                        level=eval(nodeLevelEvalStr, globals(), localsdict))

        stops.append(newNode)
        priorityStreet.append(interPriority)

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
        nodeControlEvalStr               = "StopNode.CONTROL_TYPE_UNSIGNALIZED",
        nodePriorityEvalStr              = "StopNode.PRIORITY_TEMPLATE_TWSC",
        nodeLabelEvalStr                 = "None",
        nodeLevelEvalStr                 = "None" )
    matchedAllNodes = []
    matchedOthNodes = []
    readOStopNodes = []
    foundOStopNodes = []
    # Try to match stops to nodes using X & Y coordinates, and if that fails, using link names
    for stop in otherStops:
        readOStopNodes.append(stop)
        foundStopNode = stop.matchStopNodes(net,matchedOthNodes, matchedAllNodes)
        if foundStopNode == False:
            foundStopLinks = stop.matchStopLinks(net,matchedOthNodes, matchedAllNodes)
            if foundStopLinks == False:
                dta.DtaLogger.error("Cannot match stop %s at %s" % (stop.getId(),stop._label))
                continue
            else:
                foundOStopNodes.append(stop)
        else:
            foundOStopNodes.append(stop)
    # Check to see how many stop signs were found at each node and update priorities to all-way or two-way accordingly.        

                
    dta.DtaLogger.info("Number of other stop nodes read in = %d" % len(readOStopNodes))
    dta.DtaLogger.info("Number of other stop nodes matched = %d" % len(foundOStopNodes))

    # All-way stop file is imported second so that if there is an all-way stop that wasn't correctly detected by the other shapefile,
    # this section of code will find it again and change the priority to all-way
    
    allStopShapefile = ALL_WAY_STOPS
    allwaysStops = []
    # Import all-way stops shape file

    readAWSFromShapefile(allwaysStops,
        nodesShpFilename=allStopShapefile,
        nodeVariableNames=["ObjectID","X","Y","Intersecti"],
        nodeGeometryTypeEvalStr          = "Node.GEOMETRY_TYPE_INTERSECTION",
        nodeControlEvalStr               = "StopNode.CONTROL_TYPE_UNSIGNALIZED",
        nodePriorityEvalStr              = "StopNode.PRIORITY_TEMPLATE_AWSC",
        nodeLabelEvalStr                 = "None",
        nodeLevelEvalStr                 = "None" )

    matchedNodes = []
    readAWStopNodes = []
    foundAWStopNodes = []
    # Try to match stops to nodes using X & Y coordinates, and if that fails, using link names
    for stop in allwaysStops:
        readAWStopNodes.append(stop)
        foundStopNode = stop.matchStopNodes(net,matchedNodes,matchedAllNodes)
        if foundStopNode == False:
            foundStopLinks = stop.matchStopLinks(net,matchedNodes,matchedAllNodes)
            if foundStopLinks == False:
                dta.DtaLogger.error("Cannot match stop %s at %s" % (stop.getId(),stop._label))
                continue
            else:
                foundAWStopNodes.append(stop)
        else:
            foundAWStopNodes.append(stop)
    # Remove nodes updated as all-way from other set
    for node in matchedOthNodes:
        if node in matchedNodes:
            matchedOthNodes.remove(node)
        else:
            continue
    
    udpatedPriorities = updateNodePriority(net,matchedOthNodes)

    dta.DtaLogger.info("Number of other stop nodes read in = %d" % len(readOStopNodes))
    dta.DtaLogger.info("Number of other stop nodes matched = %d" % len(foundOStopNodes))
                
    dta.DtaLogger.info("Number of all-way stop nodes read in = %d" % len(readAWStopNodes))
    dta.DtaLogger.info("Number of all-way stop nodes matched = %d" % len(foundAWStopNodes))

    dta.DtaLogger.info("Number of nodes updated with stops = %d" % len(matchedAllNodes))

    net.write(".", "sf_stops")

        
    

            
            

