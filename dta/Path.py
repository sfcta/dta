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
from itertools import izip
from .DtaError import DtaError
import shapefile 
                    
class Path(object):
    """
    A path in the network represented by a sequence of links
    that are connected to each other
    """

    @classmethod
    def writePathsToShp(cls, paths, outFileName):
        """
        Write the paths as a shapefile
        """
        w = shapefile.Writer(shapefile.POLYLINE) 
        w.field("NAME", "C", 40)
        for path in paths:
            points = []
            for node in path.iterNodes():
                points.append((node.getX(), node.getY()))
            w.line(parts=[points])
            w.record(path.getName())
        w.save(outFileName)
        
    def __init__(self, net, name, iterLinks):
        """
        Constructor that accepts a network, the path name, and a sequence of connected links
        """
        self._net = net
        self._name = name
        self.visualizeInReverse = False

        self._links = list(iterLinks)

        for linkUpstream, linkDownstream in izip(self._links, self._links[1:]):
            if not linkUpstream.hasOutgoingMovement(linkDownstream.getEndNodeId()):
                raise DtaError("Link %d does not have an outgoing movement towards "
                               "node %d" % (linkUpstream.getId(), linkDownstream.getEndNodeId()))

        if len(self._links) == 0:
            raise DtaError('A path cannot istantiated without any links')
        self._lengthInMiles = sum([link.getLengthInMiles() for link  in self.iterLinks()])
        self._obsTTInMin = {}

    def getLengthInMiles(self):
        """
        Get the length of the path in miles
        """
        return self._lengthInMiles

    def getLengthInFeet(self):
        """
        Get the length of the path in feet
        """
        return self.getLengthInMiles() * 5280

    def getSimSpeedInMPH(self, startTimeInMin, endTimeInMin):
        """
        Get the simulated speed in mph durin the specified interval
        """
        travelTime = self.getSimTTInMin(startTimeInMin, endTimeInMin)
        return self._lengthInMiles / (travelTime / 60.0)
        
    def getSimTTInMin(self, startTimeInMin, endTimeInMin):
        """
        Return the simulated travel time in minutes for the specified 
        time period
        """        
        simTT = 0
        if self.getNumLinks() > 1:
            for upLink, downLink in izip(self.iterLinks(), list(self.iterLinks())[1:]):
                movement = upLink.getOutgoingMovement(downLink.getEndNodeId())
                movTT = movement.getSimTTInMin(startTimeInMin, endTimeInMin)            
                simTT += movTT
        else:
            downLink = self._links[0]

        if downLink.hasThruTurn():
            finalMovement = downLink.getThruTurn()
            movTT = finalMovement.getSimTTInMin(startTimeInMin, endTimeInMin)
            simTT += movTT
        else:
            edgeTT = downLink.getSimTTInMin(startTimeInMin, endTimeInMin)
            simTT += edgeTT        
        return simTT

    def getSimTTInMinToLink(self, endLink, startTimeInMin, timeStepInMin):
        """
        Return the simulated travel time in minutes for the specified 
        time period
        """        
        travelTime = startTimeInMin 
        timeInSteps = int(travelTime // timeStepInMin * timeStepInMin)
        
        if endLink.getIid() == self._links[0].getIid():
            mov = self._links[0].getEmanatingMovement(self._links[1].nodeBid)
            return travelTime + mov.getSimTTInMin(timeInSteps, timeInSteps + timeStepInMin)

        for upLink, downLink in pairwise(self.iterLinks()):
            mov = upLink.getEmanatingMovement(downLink.nodeBid) 
            movTT = mov.getSimTTInMin(timeInSteps, timeInSteps + timeStepInMin)

            travelTime += movTT
            timeInSteps = int(travelTime // timeStepInMin * timeStepInMin) 
            if upLink.getIid() == endLink.getIid():
                return travelTime 
        else:
            travelTime += downLink.getSimTTInMin(timeInSteps, timeInSteps + timeStepInMin)
        return travelTime

    def getNumLinks(self):
        """
        Get the number of links in the path
        """
        return len(self._links)

    def getName(self):
        """
        Get the name of the path
        """
        return self._name

    def getFirstNode(self):
        """
        Get the first node in the path
        """
        return self._links[0].nodeA

    def getLastNode(self):
        """
        Return the last node in the path
        """
        return self._links[-1].nodeB

    def getFirstLink(self):
        """
        Return the first link in the path
        """
        return self._links[0]

    def getLastLink(self):
        """
        Return the last link in the path
        """
        return self._links[-1]

    def iterLinks(self):
        """
        Return an iterator to the edges of the path
        """
        return iter(self._links)

    def iterLinksInReverse(self):
        """
        Return an iterator to the links in the path in reverse order
        """
        links = [link for link in self.iterLinks]
        rLinks = links.reverse()
        return iter(rLinks)

    def iterNodes(self):
        """
        Return an iterator to the nodes in the path
        """
        for link in self.iterLinks():
            yield link.getStartNode()
        yield link.getEndNode()
    


        
