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

import re
import dta
import time
from itertools import izip
from dta.Algorithms import pairwise

class TransitSegment(object):        
    """
    A piece of a :py:class:`TransitLine`.
    """
    #: If the transit lane is unspecified use this for the *lane* arg to :py:meth:`TransitSegment.__init__`
    TRANSIT_LANE_UNSPECIFIED = 0
    
    #: What do these mean?
    STOP_EXIT_LANE  = 0
    #: What do these mean?    
    STOP_OUTSIDE    = 1
    #: What do these mean?    
    STOP_INSIDE     = 2
    
    def __init__(self, id, link,  label, lane, dwell, stopside):
        """
        A link in a :py:class:`TransitLine`.  The arguments are:
        
        * *id* segment identifier
        * *start* starting node ID
        * *end* ending node ID
        * *label* user-defined label for the segment or stop, a string
        * *tlane* is the lane used by the transit line. Use :py:attr:`TransitSegment.TRANSIT_LANE_UNSPECIFIED`, 1 for the outside lane, 2 for the next in, etc
        * *dwell* is the average dwell time in seconds, a float
        * *stopside* is one of :py:attr:`TransitSegment.STOP_EXIT_LANE`, :py:attr:`TransitSegment.STOP_OUTSIDE`, or :py:attr:`TransitSegment.STOP_INSIDE`

        """
        self._id        = id
        self.link       = link
        self.label      = label
        self.lane       = lane
        self.dwell      = dwell
        self.stopside   = stopside
    
    @classmethod
    def getDynameqHeaderStr(self):
        """
        Returns the Dynameq-formatted header string (the start of the file preceding the actual transit line data
        """
        return 'SEGMENTS\n*%8s %9s %9s %15s %6s %9s %9s\n' % ("id", "start", "end", "label", "tlane", "dwell", "stopside")
    
    def getDynameqStr(self):
        """
        Returns the Dynameq-formatted string representation of the transit segments.
        """
        return ' %8d %9d %9d %15s %6d %9.4f %9d\n' % (self._id, self.link.getStartNode().getId(), self.link.getEndNode().getId(),
                                                     '"' + self.label + '"', self.lane, self.dwell, self.stopside)
        
class TransitLine(object):
    """
    Transit Line representation for a DTA Network.  A Transit Line consists of a set of attributes and
    a list of :py:class:`TransitSegment` instances.
    """

    #: If the transit line is a bus, pass this as the *litype* arg of :py:meth:`TransitLine.__init__`
    LINE_TYPE_BUS   = 0
    #: If the transit line is a tram or an LRT, pass this as the *litype* arg of :py:meth:`TransitLine.__init__`    
    LINE_TYPE_TRAM  = 1
    
    #: If the transit line is active in the simulation, pass this as the *active* arg of :py:meth:`TransitLine.__init__
    LINE_ACTIVE     = 1
    #: If the transit line is not active in the simulation, pass this as the *active* arg of :py:meth:`TransitLine.__init__    
    LINE_INACTIVE   = 0


    @classmethod
    def read(cls, net, fileName):
        """Generator function that yields TransitLine objects 
        read from the input fileName"""
        inputStream = open(fileName, 'r')

        for trLine in iterRecords(inputStream, is_separator=re.compile(r'^LINE.*'),
                                     is_comment = re.compile(r'^ *\*'),
                                     joiner = lambda line:line):
            transitLineId, lineLabel, litype, vtype, stime = trLine[1].strip().split()
            hwy, dep = trLine[2].strip().split('\t')

            transitLine = TransitLine(net, transitLineId, lineLabel, litype, vtype, stime, hwy, int(dep))

            for line in trLine[4:]:
                id_, start, end, label, lane, dwell, stopside = line.strip().split()
                try:
                    link = net.getLink(start, end)
                except dta.DtaError, e:
                    logging.error('Transit line %s with id: %s. %s' % (lineLabel, transitLineId, str(e)))
                    continue
                lane = int(lane)
                stopside = int(stopside)
                if lane > link.lanes:
                    raise dta.DtaError("Transit Line %s. The the lane the bus stops %d"
                                           "cannot be greater than the number of lanes %d on "
                                           "the link" % (lineLabel, lane, link.lanes))

                transitLine.addSegment(link, float(dwell), lane=lane, stopside=stopside)
            yield transitLine

        inputStream.close()
        raise StopIteration
    
    def __init__(self, net, id, label, litype, vtype, stime, level, active, hway, dep):
        """
        Constructor.
        
        * *net* is a :py:class:`Network` instance
        * *id* is an integer ID for the transit line
        * *label* is a string label
        * *litype* is a one of :py:attr:`TransitLine.LINE_TYPE_BUS` or :py:attr:`TransitLine.LINE_TYPE_TRAM` 
        * *vtype* is a string representing vehicle type (more?)
        * *stime* is an instance of :py:class:`dta.Time` representing the start time of the line
        * *level* is an indicator for vertical alignment
        * *active* is one of :py:attr:`TransitLine.LINE_ACTIVE` or :py:attr:`TransitLine.LINE_INACTIVE`
        * *hway* is the line headway in minutes, a float
        * *dep* is the number of departures, an integer (???)
        
        """
        self._net   = net
        self._id    = id
        self.label  = label
        self.litype = litype
        self.vtype  = vtype
        self.stime  = stime
        self.level  = level
        self.active = active
        
        self.hway   = hway
        self.dep    = dep

        self._segments = []

    @classmethod
    def getDynameqFileHeaderStr(self):
        """
        Returns the Dynameq-formatted header string (the start of the file preceding the actual transit line data
        """
        return r"""<DYNAMEQ>
<VERSION_1.6>
<PUBLIC_TRANSIT_FILE>
"""
                                                                
    def getDynameqStr(self):
        """
        Returns the Dynameq-formatted string representation of the transit line.
        """
        line_comment = "LINE\n*%8s %15s %8s %15s %8s %5s %6s\n" % ("id","label", "litype", "vtype", "stime", "level", "active")        
        line_str = '%9d %15s %8d %15s %8s %5d %6d\n' % (self._id, '"' + self.label + '"', self.litype, self.vtype, self.stime.strftime("%H:%M:%S"), self.level, self.active)

        headway_comment = "*hway    dep\n"
        headway_hours = self.hway // 60
        headway_mins  = int(self.hway - headway_hours)
        headway_secs  = float(self.hway - 60*headway_hours - headway_mins)/60.0
        
        headway = '%02d:%02d:%02d %3d\n' % (headway_hours, headway_mins, headway_secs, self.dep)

        seg_str = TransitSegment.getDynameqHeaderStr()
        for segment in self.iterSegments():
            seg_str += segment.getDynameqStr()
        
        return line_comment + line_str + headway_comment + headway + seg_str
    

    def addSegment(self, link, dwell, lane=1, stopside=TransitSegment.STOP_EXIT_LANE, position=-1):
        
        transitSegment = TransitSegment(self.getNumSegments() + 1, 
                                        link, 'label%d' % (self.getNumSegments() + 1),
                                        lane, # outside lane
                                        dwell, TransitSegment.STOP_EXIT_LANE)

        if position == -1:
            self._segments.append(transitSegment)
        else:
            self._segments.insert(position, transitSegment)
        return transitSegment

    def getNumSegments(self):
        """Return the number of segments(=links) the transit line has"""
        return len(self._segments)

    def getNumStops(self):
        """Return the number of stops the transit line makes"""
        numStops = 0
        for segment in self.iterSegments():
            if segment.dwell > 0:
                numStops += 1
        return numStops

    def hasNode(self, nodeId):
        """Return True if the transit Line visits the node with the given id"""
        for segment in self.iterSegments():
            if segment.link.nodeAid == nodeId or segment.link.nodeBid == nodeId:
                return True
        return False

    def getSegment(self, startNodeId=None, endNodeId=None):
        """Return the segment with starting from startNodeId or ending to node with 
        endNodeId."""
        if not startNodeId and not endNodeId:
            raise TypeError("Incorrect invocation")
        for segment in self.iterSegments():
            if startNodeId and endNodeId:
                if segment.link.nodeAid == startNodeId and \
                        segment.link.nodeBid == endNodeId:
                    return segment
            elif startNodeId:
                if segment.link.nodeAid == startNodeId:
                    return segment
            else:
                if segment.link.nodeBid == endNodeId:
                    return segment
        raise dta.DtaError("TransitLine %s does not have the specified segment" % self.label)

    def getFirstNode(self):
        """Get the first node in the transit path"""
        return self._segments[0].link.nodeA

    def getLastNode(self):
        """Get the last node in the transit path"""
        return self._segments[-1].link.nodeB

    def hasSegment(self, startNodeId=None, endNodeId=None):
        """Return True if the line has a segment with the given start or end nodes.
        Otherwise return false"""

        try:
            self.getSegment(startNodeId=startNodeId, endNodeId=endNodeId)
            return True
        except dta.DtaError:
            return False

    def iterSegments(self):
        
        return iter(self._segments)

    @property
    def id(self):
        return self._id

    def isPathValid(self):
        
        try:
            self.validatePath()
        except dta.DtaError, e:
            return False
        return True

    def validatePath(self):
        
        allSegments=list(self.iterSegments())
        for upSegment, downSegment in izip(allSegments,allSegments[1:]):
            upLink = upSegment.link
            upNode = upLink.getEndNode()
            downLink = downSegment.link
            downNode = downLink.getEndNode()

            movecheck = False
           
            #if not upLink.hasOutgoingMovement(downLink.getEndNodeId()):
            for mov in upNode.iterOutgoingLinks():
                if mov.getEndNode()==downNode:
                    movecheck = True
            
            #if not upNode.hasOutgoingLinkForNodeId(downNode):
            if not movecheck :
                errorMessage = "Route %-15s cannot excecute movement from link %15s to link %15s " % \
                (self.label, str(upLink.getIid()), str(downLink.getIid()))

                dta.DtaLogger.error(errorMessage)
                #print 'outgoing movements:'
                #for mov in upNode.iterOutgoingLinks():
                #    print mov.getEndNode().getId()

def correctTransitLineUsingSP(net, transitLine):
    
    if transitLine.isPathValid():
        raise DynameqError('The transit line %s has a valid path and cannnot '
                           'be corrected using a SP' % transitLine.label)

    newLine = TransitLine(net, transitLine.id, transitLine.label, transitLine.litype, 
                          transitLine.vtype, transitLine.stime, transitLine.hway,
                          transitLine.dep)

    for edge in net.iterEdges():
        for mov in edge.iterEmanatingMovements():
            mov.cost = edge.length
    
    for segment1, segment2 in pairwise(transitLine.iterSegments()):
        
        link = segment1.link
        if link.hasEmanatingMovement(segment2.link.nodeBid):

            newLine.addSegment(segment1.link, segment1.dwell)
        else:

            ShortestPaths.labelCorrectingWithLabelsOnEdges(net, segment1.link)
            newLine.addSegment(segment1.link, segment1.dwell)

            path = ShortestPaths.getShortestPath2(segment1.link, segment2.link)

            for edge in path[1:-1]:
                dSegment = newLine.addSegment(edge, 0)
                

    newLine.addSegment(segment2.link, segment2.dwell)

    return newLine
