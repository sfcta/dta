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
from itertools import izip
import pdb
from collections import defaultdict

import nose.tools
from pyparsing import *

from dta.DtaError import DtaError

import re

def iterRecords(iterable, is_separator=re.compile(r"^a"), 
                is_comment = re.compile(r"^#"), 
                joiner=lambda tokens: " ".join(tokens)): 


    """Read a text file record by record where a record is defined
    in multiple sequential lines and return a string concatenating 
    all the lines of a record into one line.The provided function 
    is_separator identifies the lines which separate records. The 
    provided is_comment function identies comment lines that ought to 
    be bypased. The provided joiner function is used to combine
    all the lines of a record into one string"""

    record = []
    for line in iterable:
        line = line.strip()
        if is_comment.match(line):
            continue
        if is_separator.match(line):
            if record:
                if isinstance(joiner(record), str):
                    if is_separator.match(joiner(record)):
                        yield joiner(record)
                    record = []
                else:
                    yield record
                    record = [] # remove if record headers do
                            # not serve as record separators
            record.append(line)
        else:
            record.append(line)
    if record:
        yield joiner(record)



def createTPPlusTransitRouteParser():
    """Create two parsers on the the header and one for the body containing hte nodes
    I may be able to create one parser if I can deal with N= wich has the same format with the
    header expresions. My problem is that I cannot get the parser to see the N= not as a header 
    expression but as a block of data"""

    lineName = Word(alphanums +" "+"#" + ":" + "_" + "-" + "/" + "\\" + "(" + ")" +"." + "&" + '"') + Literal(',').suppress()
    expr = Word(alphanums + '[' + ']') + Literal('=').suppress() + Word(alphanums + '"' + '.') + Literal(',').suppress()
    header = Literal('LINE NAME=') + lineName + OneOrMore(expr) 


    nodeId = Word(nums + '-') + ZeroOrMore(Literal(',').suppress())
    access = Optional('ACCESS=' + Word(nums) + ZeroOrMore(Literal(',').suppress()))
    delay = Optional('DELAY=' + Word(nums+'.'+nums) + ZeroOrMore(Literal(',').suppress()))
    segment = Group('N=' + OneOrMore(nodeId) + access + delay)
    body = OneOrMore(segment)
    route = header + body

    return header.parseString, body.parseString

def getDictOfParsedElements(parsedSegment):

    result = defaultdict(list)
    keyword = ""
    for i in parsedSegment:
        if i in ["N=", "ACCESS=", "DELAY="]:
            keyword = i
        else:
            result[keyword].append(i)
                
    return result

def parseRoute(net, routeAsString, includeOnlyNetNodes=False):

    header = routeAsString[0:routeAsString.find('N=')]
    body = routeAsString[routeAsString.find('N='):]
    
    headerParser, bodyParser = createTPPlusTransitRouteParser()
    headerFields = headerParser(header).asList()
    bodyFields = bodyParser(body)

    if 'LINE NAME=' not in headerFields:
        raise TPPlusError("I cannot create a route from %s" % str(headerFields))
    name = headerFields[headerFields.index('LINE NAME=') + 1]
    
    route = TPPlusTransitRoute(net, name)

    #TODO I do not like the following
    #print '\n\n', headerFields, '\n\n'
    #nose.tools.set_trace()

    for extAttrName, intAttrName in TPPlusTransitRoute.attrs.iteritems():
        if extAttrName in headerFields:
            setattr(route, intAttrName, headerFields[headerFields.index(extAttrName) + 1])

    
        
    for segment in bodyFields:
        
        access = TransitNode.ACCESS_BOTH
        delay = TransitNode.DELAY_VAL

        parsedSegment = getDictOfParsedElements(segment)

        nodeIds = parsedSegment["N="]
        if "ACCESS=" in parsedSegment:
            accessLast = float(parsedSegment["ACCESS="][0])
        else:
            accessLast = access
        if "DELAY=" in parsedSegment:
            delayLast = float(parsedSegment["DELAY="][0])
        else:
            delayLast = delay 
        
        #if segment[-2] == 'ACCESS=':
        #    access == segment[-1]
        #    nodeIds = segment[1:-2]
        #elif segment[-2] == 'DELAY=':
        #    delay == segment[-1]
        #    nodeIds = segment[1:-3]
        #else:
        #    nodeIds = segment[1:]
            
        for i, nodeId in enumerate(nodeIds):
            isStop = True
            if nodeId.startswith('-'):
                isStop = False
                nodeId = nodeId[1:]
            if includeOnlyNetNodes:
                if not net.hasNode(nodeId):
                    continue
                
            if i == len(nodeIds) - 1:
                route.addTransitNode(int(nodeId), isStop, accessLast, delayLast)
            else:
                route.addTransitNode(int(nodeId), isStop, access, delay)
            
            #print 'nodeId = ',nodeId

    return route
        
class TransitNode(object):

    ACCESS_BOARD = '1'
    ACCESS_ALIGHT = '2'
    ACCESS_BOTH = '0'
    DELAY_VAL = '0.0'

    def __init__(self, nodeId, isStop, access, delay):
        
        #self.node = None # transitNode
        self.nodeId = nodeId
        self.isStop = isStop
        self.access = access
        self.delay = delay

    def __repr__(self):
        
        if self.isStop:
            return "%s, ACCESS=%f.2, DELAY=%f.2, \n" % (self.nodeId, self.access, self.delay)
        else:
            return "-%s, ACCESS=%f.2, DELAY=%f.2, \n" % (self.nodeId, self.access, self.delay)

class TPPlusTransitRoute(object):

    extAttributes = ['RUNTIME', 'ONEWAY', 'MODE', 'OWNER', 'XYSPEED', 'TIMEFAC', 'FREQ[1]', 
                     'FREQ[2]', 'FREQ[3]', 'FREQ[4]', 'FREQ[5]']
    intAttributes = ['runtime', 'oneway', 'mode', 'owner', 'xySpeed', 'timefac', 'freq1',
                     'freq2', 'freq3', 'freq4', 'freq5']

    attrs = dict(izip(extAttributes, intAttributes))

    @classmethod
    def read(cls, net, fileName, includeOnlyNetNodes=False):

        inputStream = open(fileName, 'r')
        for record in iterRecords(inputStream, is_separator=re.compile(r'^LINE NAME')):

            transitRoute = parseRoute(net, record, includeOnlyNetNodes=includeOnlyNetNodes)

            yield transitRoute
        
    
    def __init__(self, net, name):
        
        self._net = net
        if name.startswith('"') and name.endswith('"'):
            name = name[1:-1]
        self.name = name
        self.color = None
        self.mode = None
        self.oneway = None
        self.owner = None
        self.timefac = None
        self.xySpeed = None
        self.freq1 = None
        self.freq2 = None
        self.freq3 = None
        self.freq4 = None
        self.freq5 = None
        self.runtime = None
        self._transitNodes = []

        self.attributes = {'RUNTIME':self.__dict__['runtime'], 
                           'ONEWAY':self.__dict__['oneway'],
                           'MODE':self.__dict__['mode'],
                           'OWNER':self.__dict__['owner'],
                           'XYSPEED':self.__dict__['xySpeed'],
                           'TIMEFAC':self.__dict__['timefac'],
                           'FREQ[1]':self.__dict__['freq1'],
                           'FREQ[2]':self.__dict__['freq2'],
                           'FREQ[3]':self.__dict__['freq3'],
                           'FREQ[4]':self.__dict__['freq4'],
                           'FREQ[5]':self.__dict__['freq5']}

    def __repr__(self):
        
        header = 'LINE NAME=%s' % self.name
        
        for extAttrName, intAttrName in TPPlusTransitRoute.attrs.iteritems():
            attrValue = getattr(self, intAttrName)
            if attrValue:
                header += ', %s=%s' % (extAttrName, str(attrValue))
                
        body = ', N='
        for transitNode in self.iterTransitNodes():
            if transitNode.isStop:
                body += '%s, ACCESS=%f.2, DELAY=%f.2, \n' % (transitNode.nodeId, transitNode.access, transitNode.delay) 
            else:
                body += '-%s, ACCESS=%f.2, DELAY=%f.2, \n' % (transitNode.nodeId, transitNode.access, transitNode.delay) 

        return header + body[:-2] + '\n'
        
    def addTransitNode(self, nodeId, isStop, access, delay):
        """
        Add a node with the given input id to the transit route
        """        
        transitNode = TransitNode(nodeId, isStop, access, delay)
        self._transitNodes.append(transitNode)

    def getTransitNode(self, nodeId):
        """Return the transit node with the given id"""
        for transitNode in self.iterTransitNodes():
            if transitNode.nodeId == nodeId:
                return transitNode
        raise TPPlusError("Node %s is not in the route %s" % (nodeId, self.name))

    def getTransitDelay(self, nodeId):
        """Return the transit node with the given id"""
        for transitNode in self.iterTransitNodes():
            if transitNode.nodeId == nodeId :
                return transitNode.delay

    def hasTransitNode(self, nodeId):
        """Return True if the route has a node with the given id otherwise false"""
        return nodeId in [tn.nodeId for tn in self.iterTransitNodes()]
        
    def iterTransitNodes(self):
        """Return an iterator to the transit nodes"""
        return iter(self._transitNodes)

    def iterTransitStops(self):

        for trNode in self.iterTransitNodes():
            if trNode.isStop:
                yield trNode

    def isFirstNode(self, nodeId):
        """Return True if the input node id belongs to the first transit node 
        of the route"""
        if self.getNumTransitNodes() == 0:
            raise TPPluseError("Route %s does not have any transit nodes" % self.name)
        if self._transitNodes[0].nodeId == nodeId:
            return True
        else:
            return False

    def isLastNode(self, nodeId):
        """Return True if the input node id is the last node in the route"""

        if self.getNumTransitNodes() == 0:
            raise TPPluseError("Route %s does not have any transit nodes" % self.name)
        if self._transitNodes[-1].nodeId == nodeId:
            return True
        else:
            return False

    def getNumTransitNodes(self):
        """Return the number of transit nodes in the route"""
        return len(self._transitNodes)

    def getNumStops(self):
        """Return the number of stops the route makes"""
        return sum([tr.isStop for tr in self.iterTransitNodes()])



    

        
