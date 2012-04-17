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
import pdb 
import os
import dta
from itertools import izip
import random

dta.VehicleType.LENGTH_UNITS= "feet"
dta.Node.COORDINATE_UNITS   = "feet"
dta.RoadLink.LENGTH_UNITS   = "miles"

mainFolder = os.path.join(os.path.dirname(__file__), "..", "testdata") 

def getGearySubNet():

    projectFolder = os.path.join(mainFolder, 'dynameqNetwork_gearySubset')
    prefix = 'smallTestNet' 

    scenario = dta.DynameqScenario(dta.Time(0,0), dta.Time(12,0))
    scenario.read(projectFolder, prefix) 
    net = dta.DynameqNetwork(scenario) 
    net.read(projectFolder, prefix)

    simStartTimeInMin = 0
    simEndTimeInMin = 60
    simTimeStepInMin = 15
    
    net._simStartTimeInMin = simStartTimeInMin
    net._simEndTimeInMin = simEndTimeInMin
    net._simTimeStepInMin = simTimeStepInMin

    for link in net.iterLinks():
        if link.isVirtualLink():
            continue
        link.simTimeStepInMin = simTimeStepInMin
        link.simStartTimeInMin = simStartTimeInMin
        link.simEndTimeInMin = simEndTimeInMin
        for mov in link.iterOutgoingMovements():
            mov.simTimeStepInMin = simTimeStepInMin
            mov.simStartTimeInMin = simStartTimeInMin
            mov.simEndTimeInMin = simEndTimeInMin

    for link in net.iterLinks():
        if link.isVirtualLink():
            continue
        link._label  = str(link.getId())
        for mov in link.iterOutgoingMovements():
            for start, end in izip(range(0, 60, 15), range(15, 61, 15)):
                mov.setSimVolume(start, end, random.randint(500, 1000))
                mov.cost = link.euclideanLength()
    
    return net 

#def getTestNet():
#
#
#    projectFolder = "/Users/michalis/Documents/sfcta/ASCIIFiles"
#    prefix = 'Base'
#
#    scenario = dta.DynameqScenario(dta.Time(0,0), dta.Time(12,0))
#    scenario.read(projectFolder, prefix) 
#    net = dta.DynameqNetwork(scenario) 
#    net.read(projectFolder, prefix) 
#    return net 

class TestCorridorPlots:

    def test_volumes(self):


        net = getGearySubNet()

        #pdb.set_trace()

        net.writeLinksToShp("gearySubnet_links")
        net.writeNodesToShp("gearySubnet_nodes")
        
        link1 = net.getLinkForId(14834)
        link2 = net.getLinkForId(14539)
        
        pathLinks = dta.Algorithms.ShortestPaths.getShortestPathBetweenLinks(net, link1, link2, runSP=True)

        path = dta.Path(net, "test", pathLinks)
        print [link.getId() for link in pathLinks]
        volumesVsCounts = dta.CorridorPlots.CountsVsVolumes(net, path, False)
        #VC = VolumesVsCounts(net, path, False)

        names = volumesVsCounts.getIntersectionNames()
        locations = volumesVsCounts.getIntersectionLocations()
        volumes = volumesVsCounts.getVolumesAlongCorridor(0, 60)

        volumes2 = volumesVsCounts.getMovementVolumesCrossingCorridor(0, 60)

        print volumes2
        
        print "names=", volumesVsCounts.getIntersectionNames()
        print "locations=", volumesVsCounts.getIntersectionLocations()

        print "volumes=", volumesVsCounts.getVolumesAlongCorridor(0, 60)
        volumesVsCounts.writeVolumesVsCounts(0, 60, 'test')

        
        
        

        



