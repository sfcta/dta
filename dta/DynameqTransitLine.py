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
from itertools import izip
from dta.Algorithms import pairwise

class TransitSegment(object):        
    
    def __init__(self, _id, link,  label, lane, dwell, stopside):
        
        self._id = _id
        self.link = link
        self.label = label
        self.lane = lane
        self.dwell = dwell
        self.stopside = stopside

    def __repr__(self):
        
        return '\t'.join(['%d' % self._id, self.link.nodeAid, self.link.nodeBid, self.label, 
                          str(self.lane), '%8.6f' % self.dwell, self.stopside]) + '\n'
        
class TransitLine(object):

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
    
    def __init__(self, net, id_, label, litype, vtype, stime, hway, dep):
        
        self._net = net
        self._id = id_
        self.label = label
        self.litype = litype
        self.vtype = vtype
        self.stime = stime
        self.hway = hway
        self.dep = dep

        self._segments = []

    def __repr__(self):
        
        header = 'LINE\n*id\tlabel\tlitype\tvtype\t\tstime\n'
        header += '%s\t%s\t%s\t%s\t\t%s\n' % \
            (self._id, self.label, self.litype, self.vtype, self.stime)

        header += '*hway\tdep\n%s\t%d\n' % (self.hway, self.dep)

        body = 'SEGMENTS\n*id\tstart\tend\tlabel\tlane\tdwell\t\tstopside\n'
        
        for segment in self.iterSegments():
            body += str(segment)

        return header + body

    def addSegment(self, link, dwell, lane=1, stopside=0, position=-1):
        
        transitSegment = TransitSegment(self.getNumSegments() + 1, 
                                        link, 'label%d' % (self.getNumSegments() + 1),
                                        1, dwell, '0')

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
            downLink = downSegment.link
           
            if not upLink.hasOutgoingMovement(downLink.getEndNodeId()):
                errorMessage = "Route %20s cannot excecute movement from link %15s to link %15s " % \
                (self.label, str(upLink.getIid()), str(downLink.getIid()))

                dta.DtaLogger.error(errorMessage)

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
