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
import datetime
import dta
import itertools
import os
import random
import sys


USAGE = r"""

 python importTPPlusTransitRoutes.py dynameq_net_dir dynameq_net_prefix [tpplus_transit1.lin tpplus_transit2.lin ...]
 
 e.g.
 
 python importTPPlusTransitRoutes.py . sf Y:\dta\SanFrancisco\2010\transit\sfmuni.lin Y:\dta\SanFrancisco\2010\transit\bus.lin
 
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
    def convertRoute(cls, dtaNetwork, tpplusRoute, dtaRouteId, MODE_TO_LITYPE, headwayIndex,
                     startTime, demandDurationInMin, doShortestPath=True):
        """
        Convert the given input *tpplusRoute*, which is an instance of :py:class:`TPPlusTransitRoute`
        to an equivalent DTA transit line.  Returns an instance of a :py:class:`TransitLine`.
        
        Links on the route are checked against the given *dtaNetwork* (an instance of :py:class:`Network`).
        If *doShortestPath* is True, then a shortest path is searched for on the *dtaNetwork* and that
        is included (so this is assuming that the *tpplusRoute* is missing some nodes; this can happen, for example, 
        if the DTA network has split links for centroid connectors, etc.).
        If *doShortestPath* is False, these links are dropped (?).

        *dtaRouteId* is the id number for the new :py:class:`TransitLine` instance.
        
        *MODE_TO_LITYPE* maps the :py:attr:`TPPlusTransitRoute.mode` attribute (strings) to a line type
        (either :py:attr:`TransitLine.LINE_TYPE_BUS` or :py:attr:`TransitLine.LINE_TYPE_TRAM`)
        
        *headwayIndex* is the index into the frequencies of the *tpplusRoute* to use for the headway (for use with
        the :py:meth:`TPPlusTransitRoute.getHeadway`)
        
        *startTime* is the start time for the bus line (and instance of :py:class:`Time`),
        and *demandDurationInMin* is used for calculating the number of transit vehicle
        departures that will be dispatched.
        
        Note that the start time for the :py:class:`TransitLine` instance will be randomized within 
        [*startTime*, *startTime* + the headway).
        
        ..TODO:: Move this to something in dta; it does not belong in scripts.
        
        """

        dNodeSequence = []
        for tNode in tpplusRoute.iterTransitNodes():
            if not dtaNetwork.hasNodeForId(tNode.nodeId):
                dta.DtaLogger.debug('Node id %d does not exist in the Dynameq network' % tNode.nodeId)
                continue
            dNode = dtaNetwork.getNodeForId(tNode.nodeId)
            dNodeSequence.append(dNode)

        if len(dNodeSequence) == 0:
             dta.DtaLogger.error('Tpplus route %-15s cannot be converted to Dynameq because '
                                 'none of its nodes is in the Dynameq network' % tpplusRoute.name)
                                              
        if len(dNodeSequence) == 1:
             dta.DtaLogger.error('Tpplus route %-15s cannot be converted to Dyanmeq because only '
                                 'one of its nodes is in the Dynameq network' % tpplusRoute.name)

        # randomize the start time within [startTime, startTime+headway)
        headway_secs = int(60*tpplusRoute.getHeadway(headwayIndex))
        rand_offset_secs = random.randint(0, headway_secs-1)
        # need a datetime version of this to add the delta
        start_datetime = datetime.datetime(1,1,1,startTime.hour,startTime.minute,startTime.second)
        random_start = start_datetime + datetime.timedelta(seconds=rand_offset_secs)
        
        dRoute = dta.TransitLine(net=dtaNetwork, 
                                 id=dtaRouteId,
                                 label=tpplusRoute.name, 
                                 litype=MODE_TO_LITYPE[tpplusRoute.mode],
                                 vtype='Generic',
                                 stime=dta.Time(random_start.hour, random_start.minute, random_start.second),
                                 level=0,
                                 active=dta.TransitLine.LINE_ACTIVE,
                                 hway=tpplusRoute.getHeadway(headwayIndex),
                                 dep=int(float(demandDurationInMin)/tpplusRoute.getHeadway(headwayIndex)))
        
        for dNodeA, dNodeB in itertools.izip(dNodeSequence, dNodeSequence[1:]):
               
            if dtaNetwork.hasLinkForNodeIdPair(dNodeA.getId(), dNodeB.getId()):
                dLink = dtaNetwork.getLinkForNodeIdPair(dNodeA.getId(), dNodeB.getId())
                dSegment = dRoute.addSegment(dLink, 0)

                tNodeB = tpplusRoute.getTransitNode(dNodeB.getId())
                dSegment.dwell = 60*tpplusRoute.getTransitDelay(dNodeB.getId())
            else:
                # if we're not doing shortest path, nothing to do -- just move on
                if not doShortestPath: continue
                
                # dta.DtaLogger.debug('Running the SP from node %d to %d' % (dNodeA.getId(), dNodeB.getId()))
                try:
                    ShortestPaths.labelSettingWithLabelsOnNodes(dtaNetwork, dNodeA, dNodeB)
                    assert(dNodeB.label < sys.maxint)
                except:
                    dta.DtaLogger.error("Tpplus route %-15s No shortest path found from %d to %d" %
                                        (tpplusRoute.name, dNodeA.getId(), dNodeB.getId()))
                    continue

                pathNodes = ShortestPaths.getShortestPathBetweenNodes(dNodeA, dNodeB)
                nodeNumList = [ dNodeA.getId() ]
                for pathNodeA, pathNodeB in itertools.izip(pathNodes, pathNodes[1:]):
                    nodeNumList.append(pathNodeB.getId())
                    dLink = dtaNetwork.getLinkForNodeIdPair(pathNodeA.getId(), pathNodeB.getId())
                    dSegment = dRoute.addSegment(dLink, 0)

                # Warn on this because it's a little odd
                if len(nodeNumList)>4:
                    dta.DtaLogger.warn('Tpplus route %-15s shortest path from %d to %d is long: %s' %
                                        (tpplusRoute.name, dNodeA.getId(), dNodeB.getId(), str(nodeNumList)))

            # add delay
            tNodeB = tpplusRoute.getTransitNode(dNodeB.getId())
            dSegment.dwell = 60*tpplusRoute.getTransitDelay(dNodeB.getId())
        
        
        dRoute.isPathValid()
        return dRoute

if __name__ == "__main__":

    INPUT_DYNAMEQ_NET_DIR         = sys.argv[1]
    INPUT_DYNAMEQ_NET_PREFIX      = sys.argv[2]
    TRANSIT_LINES                 = sys.argv[3:]

    dta.VehicleType.LENGTH_UNITS= "feet"
    dta.Node.COORDINATE_UNITS   = "feet"
    dta.RoadLink.LENGTH_UNITS   = "miles"

    dta.setupLogging("importTPPlusTransitRoutes.INFO.log", "importTPPlusTransitRoutes.DEBUG.log", logToConsole=True)
    
    scenario = dta.DynameqScenario(dta.Time(0,0), dta.Time(23,0))
    scenario.read(INPUT_DYNAMEQ_NET_DIR, INPUT_DYNAMEQ_NET_PREFIX) 
    net = dta.DynameqNetwork(scenario)
    net.read(INPUT_DYNAMEQ_NET_DIR, INPUT_DYNAMEQ_NET_PREFIX)


    MODE_TO_LITYPE = {'11':dta.TransitLine.LINE_TYPE_BUS,  # Muni Local
                      '12':dta.TransitLine.LINE_TYPE_BUS,  # Muni Express
                      '13':dta.TransitLine.LINE_TYPE_BUS,  # Muni BRT
                      '14':dta.TransitLine.LINE_TYPE_TRAM, # Muni CableCar
                      '15':dta.TransitLine.LINE_TYPE_TRAM, # Muni LRT
                      }
    # others are buses
    for modenum in range(1,30):
        key = "%d" % modenum
        if key not in MODE_TO_LITYPE:
            MODE_TO_LITYPE["%d" % modenum] = dta.TransitLine.LINE_TYPE_BUS
        

    # write the output file
    output_file = open(os.path.join(INPUT_DYNAMEQ_NET_DIR, "%s_ptrn.dqt" % INPUT_DYNAMEQ_NET_PREFIX),mode="w+")
    output_file.write(dta.TransitLine.getDynameqFileHeaderStr())
    
    dtaTransitLineId = 1
    for transit_file in TRANSIT_LINES:
        dta.DtaLogger.info("===== Processing %s ======" % transit_file)
        
        for tpplusRoute in dta.TPPlusTransitRoute.read(net, transit_file):
            # ignore if there's no frequency for this time period
            if tpplusRoute.getHeadway(3) == 0: continue
            
            dtaTransitLine = TPPlus2Dynameq.convertRoute(net, tpplusRoute, dtaTransitLineId, MODE_TO_LITYPE, headwayIndex=3, 
                                                         startTime=dta.Time(15,30), demandDurationInMin=3*60)
            
            # ignore if no segments for the DTA network
            if dtaTransitLine.getNumSegments() == 0: continue
            
            output_file.write(dtaTransitLine.getDynameqStr())
            dtaTransitLineId += 1

    output_file.close()

    

    
    

    
                
