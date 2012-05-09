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
import csv
import os
import sys
from itertools import izip
import pdb

import dta
from dta.TPPlusTransitRoute import TPPlusTransitRoute
from dta.DynameqTransitLine import TransitLine
from dta.Algorithms import ShortestPaths
from dta.CubeNetwork import CubeNetwork
#from dta.Network import Network

USAGE = r"""

 python importTPPlusTransitRoutes.py dynameq_net_dir dynameq_net_prefix tpplus_transit.lin
 
 e.g.
 
 python importTPPlusTransitRoutes.py . sf Y:\dta\SanFrancisco\2010\transit\transitPM.lin
 
 This script reads the dynameq network in the given directory, as well as the given Cube TPPlus transit line file,
 and converts the transit lines into DTA transit lines, outputting them in Dynameq format as 
 [dynameq_net_dir]\[dynameq_net_prefix]_ptrn.dqt
 
 """
 
def convertHeadway2HHMM(headwayInMin):

    hours = headwayInMin / 60
    minutes = headwayInMin - hours * 60

    if hours < 10:
        hours = '0%d' % hours
    else:
        hours = '%d' % hours
    if minutes < 10:
        minutes = '0%d' % minutes
    else:
        minutes = '%d' % minutes

    return "%s%s" % (hours, minutes)

def convertStartTime2HHMMSS(startTimeInMin):

    hours = startTimeInMin / 60
    minutes = startTimeInMin - hours * 60

    if hours < 10:
        hours = '0%d' % hours
    else:
        hours = '%d' % hours
    if minutes < 10:
        minutes = '0%d' % minutes
    else:
        minutes = '%d' % minutes

    return "%s:%s:00" % (hours, minutes)



class TPPlus2Dynameq(object):
    """Converts TPPlus Network elemements to the equivalent Dynameq ones"""
    
    @classmethod
    def convertRoute(cls, dtaNetwork, tpplusRoute, doShortestPath=True):
        """
        Convert the given input *tpplusRoute*, which is an instance of :py:class:`TPPlusTransitRoute`
        to an equivalent DTA transit line.  Returns an instance of a :py:class:`TransitLine`.
        
        Links on the route are checked against the given *dtaNetwork* (an instance of :py:class:`Network`).
        If *doShortestPath* is True, then a shortest path is searched for on the *dtaNetwork* and that
        is included (so this is assuming that the *tpplusRoute* is missing some nodes).  If
        *doShortestPath* is False, these links are dropped (?).
        
        ..TODO:: They're not all buses; enable communication about this fact.
        ..TODO:: Move this to something in dta; it does not belong in scripts.
        
        """
        DWELL_TIME = 30

        for edge in dtaNetwork.iterLinks():
            edge.cost = edge.euclideanLength()
            if edge.isConnector():
                edge.cost = sys.maxint
        
        dNodeSequence = []
        for tNode in tpplusRoute.iterTransitNodes():
            if not dtaNetwork.hasNodeForId(tNode.nodeId):
                dta.DtaLogger.warn('Node id %d does not exist in the Dynameq network' % tNode.nodeId)
                continue
            dNode = dtaNetwork.getNodeForId(tNode.nodeId)
            dNodeSequence.append(dNode)

        if len(dNodeSequence) == 0:
             dta.DtaLogger.error('Tpplus route %s cannot be converted to Dynameq because '
                                 'none of its nodes is in the Dynameq network' % tpplusRoute.name)
                                              
        if len(dNodeSequence) == 1:
             dta.DtaLogger.error('Tpplus route %s cannot be converted to Dyanmeq because only '
                                 'one of its nodes is in the Dynameq network' % tpplusRoute.name)

        dRoute = dta.DynameqTransitLine.TransitLine(dtaNetwork, tpplusRoute.name, 'label1', '0', 'Generic', '15:30:00', '00:20:00', 10)
        for dNodeA, dNodeB in izip(dNodeSequence, dNodeSequence[1:]):
               
            if dtaNetwork.hasLinkForNodeIdPair(dNodeA.getId(), dNodeB.getId()):
                dLink = dtaNetwork.getLinkForNodeIdPair(dNodeA.getId(), dNodeB.getId())
                dSegment = dRoute.addSegment(dLink, 0)
                #print 'added link', dLink.iid

                tNodeB = tpplusRoute.getTransitNode(dNodeB.getId())
                if tNodeB.isStop:
                    dSegment.dwell = 60*tpplusRoute.getTransitDelay(dNodeB.getId())
                    #print 'Delay = ',dSegment.dwell
            else:
                if doShortestPath:
                    dta.DtaLogger.debug('Running the SP from Root node %d' % dNodeA.getId())
                    #ShortestPaths.labelSettingWithLabelsOnNodes(dtaNetwork, dNodeA, dNodeB)
                    ShortestPaths.labelCorrectingWithLabelsOnNodes(dtaNetwork, dNodeA)
                    if dNodeB.label == sys.maxint:
                        continue

                    pathNodes = ShortestPaths.getShortestPathBetweenNodes(dNodeA, dNodeB)
                    numnewlinks = 0
                    for pathNodeA, pathNodeB in izip(pathNodes, pathNodes[1:]):
                        numnewlinks+=1
                        dLink = dtaNetwork.getLinkForNodeIdPair(pathNodeA.getId(), pathNodeB.getId())
                        dSegment = dRoute.addSegment(dLink, 0)
                        #if dNodeB.getId()==24666 and dNodeA.getId()==24564:
                        #    print 'New Link Added = ',dLink.getId()

                    if numnewlinks>2:
                        dta.DtaLogger.debug('NodeStart = %d, NodeEnd = %d, Number of new links added = %d' % (dNodeA.getId(), dNodeB.getId(), numnewlinks))

                    tNodeB = tpplusRoute.getTransitNode(dNodeB.getId())
                    if tNodeB.isStop:
                        dSegment.dwell = 60*tpplusRoute.getTransitDelay(dNodeB.getId())
                else:
                    pass
                        
        
        dRoute.isPathValid()
        return dRoute

if __name__ == "__main__":

    INPUT_DYNAMEQ_NET_DIR         = sys.argv[1]
    INPUT_DYNAMEQ_NET_PREFIX      = sys.argv[2]
    TRANSIT_LINES                 = sys.argv[3]
    #SF_CUBE_NET_FIL               = sys.argv[4]

    dta.VehicleType.LENGTH_UNITS= "feet"
    dta.Node.COORDINATE_UNITS   = "feet"
    dta.RoadLink.LENGTH_UNITS   = "miles"

    dta.setupLogging("importTPPlusTransitRoutes.INFO.log", "importTPPlusTransitRoutes.DEBUG.log", logToConsole=True)
    
    scenario = dta.DynameqScenario(dta.Time(0,0), dta.Time(23,0))
    scenario.read(INPUT_DYNAMEQ_NET_DIR, INPUT_DYNAMEQ_NET_PREFIX) 
    net = dta.DynameqNetwork(scenario)
    net.read(INPUT_DYNAMEQ_NET_DIR, INPUT_DYNAMEQ_NET_PREFIX)


    #projectFolder2 = "C:/SFCTA/dta/testdata/ReneeTransitTest/"
    #net.writeNodesToShp(os.path.join(projectFolder2, "sf_nodes"))
    #net.writeLinksToShp(os.path.join(projectFolder2, "sf_links"))
    
    for tpplusRoute in dta.TPPlusTransitRoute.read(net, TRANSIT_LINES):

        dynameqRoute = TPPlus2Dynameq.convertRoute(net, tpplusRoute)
        

    


    

    
    

    
                
