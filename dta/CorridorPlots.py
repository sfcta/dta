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

import datetime
import random
from itertools import izip

import numpy as np
import pylab as plt 

class CountsVsVolumes(object):
    
    def __init__(self, net, path, reverse):
        
        self._net = net
        self._path = path
        self._reverse = reverse
        
        self._intNames, self._intLocations = self._getIntersectionNamesAndLocations()
        
        self._linkCapacities = []
        self._leftTurnCapacities = []

    def _getIntersectionNamesAndLocations(self):
        """
        
        """
        intLocationsAlongRoute = [0,]
        intNamesAlongRoute = [self._path.getCrossStreetName(self._path.getFirstNode()),] 
        length = 0
        for node, link in izip(self._path.iterNodes(), self._path.iterLinks()):
        
            length += (link.getLength() * 5280)
            intLocationsAlongRoute.append(length)
            intNamesAlongRoute.append(self._path.getCrossStreetName(node))

        return [inLocationsAlongRoute, intNamesAlongRoute]

    def _getIntersectionNamesAndLocationsInReverse(self):
        """
        
        """
        pass
    
    def getVolumesAlongRoute(self, startTimeInMin, endTimeInMin):
        """Generator method that returns the edge, leftTurn and right turn
        volumes for all the links on the route
        """
        linkVolumes = []
        leftTurnVolumes = []
        rightTurnVolumes = []
        
        for edge in self._path.iterLinks():
            edgeVolume = edge.getSimVolume(startTimeInMin, endTimeInMin)
            leftTurnVolume = 0
            rightTurnVolume = 0
            if edge.hasLeftTurn():
                leftTurn = edge.getLeftTurn()
                leftTurnVolume = leftTurn.getSimVolume(startTimeInMin, endTimeInMin)
            else:
                leftTurn = 0
            if edge.hasRightTurn():
                rightTurn = edge.getRightTurn()
                rightTurnVolume = rightTurn.getSimVolume(startTimeInMin, endTimeInMin)
            else:
                rightTurn = 0

            linkVolumes.append(edgeVolume)
            leftTurnVolumes.append(leftTurnVolume)
            rightTurnVolumes.append(rightTurnVolume)

        return linkVolumes, leftTurnVolumes, rightTurnVolumes

    def getCountsAlongRoute(self, startTimeInMin, endTimeInMin):
        """Generator method that returns the edge, left turn and right turn
        counts for the specified time window along the route
        """
        linkCounts = []
        leftTurnCounts = []
        rightTurnCounts = [] 
        for edge in route.iterEdges():
            edgeCount = None
            leftTurnCount = None
            rightTurnCount = None
            if edge.hasObsCount(startTimeInMin, endTimeInMin):
                edgeCount = edge.getObsCount(startTimeInMin, endTimeInMin)
            if edge.hasLeftTurn():
                leftTurn = edge.getLeftTurn()
                leftTurnCount = leftTurn.getObsCount(startTimeInMin, endTimeInMin)
            if edge.hasRightTurn():
                rightTurn = edge.getRightTurn()
                rightTurnCount = rightTurn.getObsCount(startTimeInMin, endTimeInMin)

            linkCounts.append(edgeCount)
            leftTurnCounts.append(leftTurnCount)
            rightTurnCounts.append(rightTurnCount)

    @classmethod
    def iterMovementVolumesCrossingRoute(cls, route, startTimeInMin, endTimeInMin):
        """Generator method that returns the movement counts that cross the route
         destined to one of the edges of the route
         """
        #nose.tools.set_trace()
        for edge in route.iterEdges():
            leftTurnVolume = None
            rightTurnVolume = None
            for incidentMovement in edge.iterIncidentMovements():
                movementVolume = incidentMovement.getSimVolume(startTimeInMin, endTimeInMin)
                if incidentMovement.isLeftTurn():
                    leftTurnVolume = movementVolume
                elif incidentMovement.isRightTurn():
                    rightTurnVolume = movementVolume

            if not leftTurnVolume:
                leftTurnVolume = 0
            if not rightTurnVolume:
                rightTurnVolume = 0
            yield edge, leftTurnVolume, rightTurnVolume
    
    @classmethod
    def iterMovementCountsCrossingRoute(cls, route, startTimeInMin, endTimeInMin):
        """Generator method that yields the left turn and right turn counts
        on crossing links
        """
        for edge in route.iterEdges():
            leftTurnCount = None
            rightTurnCount = None
            for incidentMovement in edge.iterIncidentMovements():
                if incidentMovement.isLeftTurn():
                    leftTurnCount = incidentMovement.getObsCount(startTimeInMin, endTimeInMin)
                elif incidentMovement.isRightTurn():
                    rightTurnCount = incidentMovement.getObsCount(startTimeInMin, endTimeInMin)

            yield edge, leftTurnCount, rightTurnCount
    
    @classmethod
    def plotEdgeCountsAlongRoute(cls, plot, route, startTimeInMin, endTimeInMin, color):
        """Adds count information to the provided plot"""
        countLocations = []
        counts = []

        for edge in route.iterEdges():
            if edge.getObsCount(startTimeInMin, endTimeInMin):
                counts.append(edge.getObsCount(startTimeInMin, endTimeInMin))
            else:
                counts.append(None)

            if countLocations:
                countLocations.append(countLocations[-1] + edge.getLengthInFeet())
            else:
                countLocations.append(edge.getLengthInFeet())

        countLocationsCleaned = []
        countsCleaned = []
        for countLocation, count in zip(countLocations, counts):
            if count:
                countLocationsCleaned.append(countLocation)
                countsCleaned.append(count)

        plot.scatter(countsCleaned, countLocationsCleaned, c=color)
        return plot
        
    @classmethod
    def plotEdgeVolumesAlongRoute(cls, route, startTimeInMin, endTimeInMin, color):
        """Creates a scatterplot with the Y axis representing edges along the route
        and the x axis representing volumes""" 
        volumes = []
        for edge in route.iterEdges():
            if volumeLocations:
                volumeLocations.append(volumeLocations[-1] + edge.getLengthInFeet())
            else:
                volumeLocations.append(edge.getLengthInFeet())

            print edge.iid, edge.getSimVolume(startTimeInMin, endTimeInMin)
            volumes.append(edge.getSimVolume(startTimeInMin, endTimeInMin))

        plt.clf()
        plt.cla()
        plt.figure(1)
        ax = plt.subplot(111)
        ax.scatter(volumes, volumeLocations, c=color)

        yticks = [loc for loc in volumeLocations]
        #yticks.insert(0, 0)
        ax.set_yticks(yticks)

        #ax.set_yticklabels(map(str, range(len(yticks))))
        ax.set_yticklabels(["" for i in range(len(yticks))])
        return ax


    def writeVolumesVsCounts(self, startTimeInMin, endTimeInMin, outPlotFileName):

        plt.clf()
        plt.cla()
        plt.figure(1)
        ax = plt.subplot(111)


        
        ax.scatter(volumes, volumeLocations, c='r')

        #if countLocations and counts:
        #    ax.scatter(counts, countLocations, c='b')

        ax.set_xticklabels(xticks) 

        yticks = [loc for loc in volumeLocations]
        #yticks.insert(0, 0)
        ax.set_yticks(yticks)
        ax.set_yticklabels(map(str, range(len(yticks))))
        
        plt.show()
        

