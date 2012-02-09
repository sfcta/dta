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
import shapefile
import pdb

import math
from itertools import izip, imap
import os
import sys, csv

from collections import defaultdict 

from itertools import chain 
from .Centroid import Centroid
from .Connector import Connector
from .DtaError import DtaError
from .Logger import DtaLogger
from .Movement import Movement
from .Network import Network
from .Node import Node
from .RoadLink import RoadLink
from .RoadNode import RoadNode
from .TimePlan import TimePlan
from .VirtualLink import VirtualLink
from .VirtualNode import VirtualNode
from .VehicleClassGroup import VehicleClassGroup

class DynameqNetwork(Network):
    """
    A Dynameq DTA Network.
    """
    
    BASE_FILE       = '%s_base.dqt'
    ADVANCED_FILE   = '%s_advn.dqt'
    CONTROL_FILE    = '%s_ctrl.dqt'
    TRANSIT_FILE    = '%s_ptrn.dqt'
    PRIORITIES_FILE = '%s_prio.dqt'
    
    BASE_HEADER          = """<DYNAMEQ>
<VERSION_1.5>
<BASE_NETWORK_FILE>
* CREATED by DTA Anyway http://code.google.com/p/dta/
"""
    ADVANCED_HEADER     = """<DYNAMEQ>
<VERSION_1.5>
<ADVN_NETWORK_FILE>
* CREATED by DTA Anyway http://code.google.com/p/dta/    
"""
    CTRL_HEADER        = """<DYNAMEQ>
<VERSION_1.7>
<CONTROL_PLANS_FILE>
* CREATED by DTA Anyway http://code.google.com/p/dta/
"""

    MOVEMENT_FLOW_OUT = 'movement_aflowo.dqt'
    MOVEMENT_TIME_OUT = 'movement_atime.dqt'
    MOVEMENT_SPEED_OUT = "movement_aspeed.dqt"
    LINK_FLOW_OUT = 'link_aflowo.dqt'
    LINK_TIME_OUT = 'link_atime.dqt'
    LINK_SPEED_OUT = "link_aspeed.dqt"
    
    def __init__(self, scenario):
        """
        Constructor.  Initializes to an empty network.
        
        Keeps a reference to the given dynameqScenario (a :py:class:`DynameqScenario` instance)
        for :py:class:`VehicleClassGroup` lookups        
        """ 
        Network.__init__(self, scenario)
        self._dir = None 
                
    def read(self, dir, file_prefix):
        """
        Reads the network in the given *dir* with the given *file_prefix*.

        """
        # base file processing
        basefile = os.path.join(dir, DynameqNetwork.BASE_FILE % file_prefix)
        if not os.path.exists(basefile):
            raise DtaError("Base network file %s does not exist" % basefile)
        
        self._dir = dir 
        count = 0
        for fields in self._readSectionFromFile(basefile, "NODES", "CENTROIDS"):
            self.addNode(self._parseNodeFromFields(fields))
            count += 1
        DtaLogger.info("Read  %8d %-16s from %s" % (count, "NODES", basefile))

        count = 0
        for fields in self._readSectionFromFile(basefile, "CENTROIDS", "LINKS"):
            self.addNode(self._parseCentroidFromFields(fields))
            count += 1
        DtaLogger.info("Read  %8d %-16s from %s" % (count, "CENTROIDS", basefile))
        
        count = 0
        for fields in self._readSectionFromFile(basefile, "LINKS", "LANE_PERMS"):
            self.addLink(self._parseLinkFromFields(fields))
            count += 1
        DtaLogger.info("Read  %8d %-16s from %s" % (count, "LINKS", basefile))
        
        count = 0
        for fields in self._readSectionFromFile(basefile, "LANE_PERMS", "LINK_EVENTS"):
            self._addLanePermissionFromFields(fields)
            count += 1
        DtaLogger.info("Read  %8d %-16s from %s" % (count, "LANE_PERMS", basefile))
        
        count = 0
        for fields in self._readSectionFromFile(basefile, "LINK_EVENTS", "LANE_EVENTS"):
            #TODO: do LINK_EVENTS have to correspond to scenario events?
            raise DtaError("LINK_EVENTS not implemented yet")
            count += 1
        DtaLogger.info("Read  %8d %-16s from %s" % (count, "LINK_EVENTS", basefile))

        count = 0
        for fields in self._readSectionFromFile(basefile, "LANE_EVENTS", "VIRTUAL_LINKS"):
            #TODO: do LANE_EVENTS have to correspond to scenario events?
            raise DtaError("LANE_EVENTS not implemented yet")
            count += 1
        DtaLogger.info("Read  %8d %-16s from %s" % (count, "LANE_EVENTS", basefile))
            
        count = 0
        for fields in self._readSectionFromFile(basefile, "VIRTUAL_LINKS", "MOVEMENTS"):
            self.addLink(self._parseVirtualLinkFromFields(fields))
            count += 1
        DtaLogger.info("Read  %8d %-16s from %s" % (count, "VIRTUAL_LINKS", basefile))
            
        count = 0                        
        for fields in self._readSectionFromFile(basefile, "MOVEMENTS", "MOVEMENT_EVENTS"):
            mov = self._parseMovementFromFields(fields)
            if mov._permission.classDefinitionString == VehicleClassGroup.CLASSDEFINITION_PROHIBITED:
                continue                               
            self.addMovement(self._parseMovementFromFields(fields))
            count += 1
        DtaLogger.info("Read  %8d %-16s from %s" % (count, "MOVEMENTS", basefile))
        
        count = 0
        for fields in self._readSectionFromFile(basefile, "MOVEMENT_EVENTS", "ENDOFFILE"):
            #TODO: MOVEMENT_EVENTS
            raise DtaError("MOVEMENT_EVENTS not implemented yet")            
            count += 1
        DtaLogger.info("Read  %8d %-16s from %s" % (count, "MOVEMENT_EVENTS", basefile))
        
        # advanced file processing
        advancedfile = os.path.join(dir, DynameqNetwork.ADVANCED_FILE % file_prefix)
        if os.path.exists(advancedfile):
            
            count = 0
            for fields in self._readSectionFromFile(advancedfile, "SHIFTS", "VERTICES"):
                self._addShiftFromFields(fields)
                count += 1
            DtaLogger.info("Read  %8d %-16s from %s" % (count, "SHIFTS", advancedfile))
            
            count = 0
            for fields in self._readSectionFromFile(advancedfile, "VERTICES", "ENDOFFILE"):
                self._addShapePointsToLink(fields)
                count += 1
            DtaLogger.info("Read  %8d %-16s from %s" % (count, "VERTICES", advancedfile))

        # control file Processing
        controlFile = os.path.join(dir, DynameqNetwork.CONTROL_FILE % file_prefix)
        #The structure of the code is different than the previous read ones
        #Reason 1: The control file does not contain a signal for each line
        #Reason 2: If multiple time periods exist one more nesting level is added 
        if os.path.exists(controlFile):
            for tp in TimePlan.read(self, controlFile):
                tp.getNode().addTimePlan(tp)
                        
        #TODO: what about the custom priorities file?  I don't see that in pbtools               
        ## TODO - what about the public transit file?
        
    def write(self, dir, file_prefix):
        """
        Writes the network into the given *dir* with the given *file_prefix*
        """

        self._scenario.write(dir, file_prefix)
        basefile = os.path.join(dir, DynameqNetwork.BASE_FILE % file_prefix)
        
        basefile_object = open(basefile, "w")
        basefile_object.write(DynameqNetwork.BASE_HEADER)
        self._writeNodesToBaseFile(basefile_object)
        self._writeCentroidsToBaseFile(basefile_object)
        self._writeLinksToBasefile(basefile_object)
        self._writeLanePermissionsToBaseFile(basefile_object)
        self._writeLinkEventsToBaseFile(basefile_object)
        self._writeLaneEventsToBaseFile(basefile_object)
        self._writeVirtualLinksToBaseFile(basefile_object)
        self._writeMovementsToBaseFile(basefile_object)
        self._writeMovementEventsToBaseFile(basefile_object)
        basefile_object.close()
        
        advancedfile = os.path.join(dir, DynameqNetwork.ADVANCED_FILE % file_prefix)
        advancedfile_object = open(advancedfile, "w")
        advancedfile_object.write(DynameqNetwork.ADVANCED_HEADER)
        self._writeShiftsToAdvancedFile(advancedfile_object)
        self._writeShapePointsToAdvancedFile(advancedfile_object)
        advancedfile_object.close()

        ctrlfile = os.path.join(dir, DynameqNetwork.CONTROL_FILE % file_prefix)
        ctrl_object = open(ctrlfile, "w")
        ctrl_object.write(DynameqNetwork.CTRL_HEADER)
        self._writeControlFile(ctrl_object)
        ctrl_object.close() 
        
        
    def _readSectionFromFile(self, filename, sectionName, nextSectionName):
        """
        Generator function, yields fields (array of strings) from the given section of the given file.
        """
        lines = open(filename, "r")
        curLine = ""
        try:
            # find the section
            while curLine != sectionName:
                curLine = lines.next().strip()
        except StopIteration:
            raise DtaError("DynameqNetwork _readSectionFromFile failed to find %s in %s" % 
                           (sectionName,filename))
        
        # go past the section name
        curLine = lines.next().strip()
        # skip any comments
        while curLine[0] == "*":
            curLine = lines.next().strip()
        
        # these are the ones we want
        while not curLine == nextSectionName:
            fields  = curLine.split()
            yield fields
            
            curLine = lines.next().strip()
        lines.close()
        raise StopIteration

    def _parseNodeFromFields(self, fields):
        """
        Interprets fields and returns a RoadNode or a VirtualNode
        """
        id      = int(fields[0])
        x       = float(fields[1])
        y       = float(fields[2])
        control = int(fields[3])
        priority= int(fields[4])
        type    = int(fields[5])
        level   = int(fields[6])
        label   = fields[7]
        if label[0] == '"' and label[-1] ==  '"':
            label = label[1:-1]

        if type == Node.GEOMETRY_TYPE_INTERSECTION or \
           type == Node.GEOMETRY_TYPE_JUNCTION:
            return RoadNode(id, x, y, type, control, priority, label, level)
        
        if type == Node.GEOMETRY_TYPE_VIRTUAL:
            return VirtualNode(id, x, y, label, level)
        
        raise DtaError("DynameqNetwork _parseNodesFromBasefile: Found Node of unrecognized type %d" % type)

    def _writeNodesToBaseFile(self, basefile_object):
        """
        Write version of _parseNodesFromBaseFile().  *basefile_object* is the file object,
        ready for writing.
        """
        basefile_object.write("NODES\n")
        basefile_object.write("*%8s %20s %20s %8s %8s %4s %6s %12s\n" % 
                              ("id",
                               "x-coordinate",
                               "y-coordinate",
                               "control",
                               "priority",
                               "type",
                               "level",
                               "label"))


        count = 0

        roadNodes = sorted(self.iterRoadNodes(), key=lambda n:n.getId())
        virtualNodes = sorted(self.iterVirtualNodes(), key=lambda n:n.getId())

        for node in chain(roadNodes, virtualNodes):
            
            if isinstance(node, VirtualNode):
                control = VirtualNode.DEFAULT_CONTROL
                priority = VirtualNode.DEFAULT_PRIORITY
            else:
                control = node._control
                priority = node._priority

            basefile_object.write("%9d %20.6f %20.6f %8d %8d %4d %6d %12s\n" %
                                  (node.getId(),
                                   node.getX(),
                                   node.getY(),
                                   control,
                                   priority,
                                   node._geometryType,
                                   node._level,
                                   '"' + node._label + '"'))
            count += 1
        DtaLogger.info("Wrote %8d %-16s to %s" % (count, "NODES", basefile_object.name))
        DtaLogger.info("Wrote %8d %-16s to %s" % (self.getNumRoadNodes(), "ROAD NODES", basefile_object.name))
        DtaLogger.info("Wrote %8d %-16s to %s" % (self.getNumCentroids(), "CENTROIDS", basefile_object.name))
        DtaLogger.info("Wrote %8d %-16s to %s" % (self.getNumVirtualNodes(), "VIRTUAL NODES", basefile_object.name))
        
        
    def _parseCentroidFromFields(self, fields):
        """
        Interprets fields into a Centroid
        """
        id      = int(fields[0])
        x       = float(fields[1])
        y       = float(fields[2])
        level   = int(fields[3])
        label   = fields[4]
        if label[0] == '"' and label[-1] ==  '"':
            label = label[1:-1]
        
        return Centroid(id, x, y, label=label, level=level)
    
    def _writeCentroidsToBaseFile(self, basefile_object):
        """
        Write version of _parseCentroidsFromBaseFile().  *basefile_object* is the file object,
        ready for writing.
        """
        basefile_object.write("CENTROIDS\n")
        basefile_object.write("*%8s %20s %20s %6s %5s\n" % 
                              ("id",
                               "x-coordinate",
                               "y-coordinate",
                               "level",
                               "label"))
        
        count = 0
        for nodeId in sorted(self._nodes.keys()):
            centroid = self._nodes[nodeId]
            if not isinstance(centroid, Centroid): continue
            
            basefile_object.write("%9d %20.6f %20.6f %6d %s\n" % 
                                  (centroid.getId(),
                                   centroid.getX(),
                                   centroid.getY(),
                                   centroid._level,
                                   '"' + centroid._label + '"'))
            count += 1
        DtaLogger.info("Wrote %8d %-16s to %s" % (count, "CENTROIDS", basefile_object.name))

    def _parseLinkFromFields(self, fields):
        """
        Interprets fields into a Connector or a RoadLink
        """            
        id      = int(fields[0])
        startid = int(fields[1])
        endid   = int(fields[2])
        rev     = int(fields[3])
        faci    = int(fields[4])
        length  = float(fields[5])
        fspeed  = float(fields[6])
        lenfac  = float(fields[7])
        resfac  = float(fields[8])
        lanes   = int(fields[9])
        rabout  = int(fields[10])
        level   = int(fields[11])
        tmplabel= fields[12:]

        if tmplabel == '""':
            label = ""
        else:
            label = " ".join(tmplabel)[1:-1]
            
        startNode = self.getNodeForId(startid)
        endNode = self.getNodeForId(endid)
        
        if (isinstance(startNode, Centroid) or isinstance(endNode, Centroid) or
            isinstance(startNode, VirtualNode) or isinstance(endNode, VirtualNode)):
            
            # check faci == Connector.FACILITY_TYPE?
            
            return Connector(id, startNode, endNode, reverseAttachedLinkId=rev, 
                                length=(None if length==-1 else length),
                                freeflowSpeed=fspeed, effectiveLengthFactor=lenfac, 
                                responseTimeFactor=resfac, numLanes=lanes,
                                roundAbout=rabout, level=level, label=label)
        
        # are these all RoadLinks?  What about VirtualLinks?
        return RoadLink(id, startNode, endNode, reverseAttachedLinkId=rev, 
                           facilityType=faci, length=(None if length==-1 else length),
                           freeflowSpeed=fspeed, effectiveLengthFactor=lenfac, 
                           responseTimeFactor=resfac, numLanes=lanes,
                           roundAbout=rabout, level=level, label=label)                    

    def _writeLinksToBasefile(self, basefile_object):
        """
        Write version of _readLinksFromBaseFile().  *basefile_object* is the file object,
        ready for writing.
        """
        basefile_object.write("LINKS\n")
        basefile_object.write("*      id    start      end      rev faci          len       fspeed   lenfac   resfac lanes rabout  level         label\n")

        count = 0

        roadLinks = sorted(self.iterRoadLinks() , key=lambda rl:rl.getId()) 
        connectors = sorted(self.iterConnectors(), key=lambda c:c.getId())

        for link in chain(roadLinks, connectors):

            basefile_object.write("%9d %8d %8d %7d %4d %12s %12.1f %8.2f %8.2f %5d %5d %6d %13s\n" % 
                                  (link.getId(),
                                   link.getStartNode().getId(),
                                   link.getEndNode().getId(),
                                   link._reverseAttachedLinkId if link._reverseAttachedLinkId else -1,
                                   link._facilityType,
                                   ("%12.3f" % -1), #link._length if link._length else "-1"),
                                   link._freeflowSpeed,
                                   link._effectiveLengthFactor,
                                   link._responseTimeFactor,
                                   link._numLanes,
                                   link._roundAbout,
                                   link._level,
                                   '"' + (link._label if link._label else "") + '"'))
            count += 1
        DtaLogger.info("Wrote %8d %-16s to %s" % (count, "LINKS", basefile_object.name))
        DtaLogger.info("Wrote %8d %-16s to %s" % (self.getNumRoadLinks(), "ROAD LINKS", basefile_object.name))
        DtaLogger.info("Wrote %8d %-16s to %s" % (self.getNumConnectors(), "CONNECTORS", basefile_object.name))
        DtaLogger.info("Wrote %8d %-16s to %s" % (self.getNumVirtualLinks(), "VIRTUAL LINKS", basefile_object.name))
        
    def _addLanePermissionFromFields(self, fields):
        """
        Updates links by attaching permissions.
        """            
        linkId  = int(fields[0])
        laneId  = int(fields[1])
        perms   = fields[2]
        
        vehicleClassGroup = self._scenario.getVehicleClassGroup(perms)
        link = self.getLinkForId(linkId)
        link.addLanePermission(laneId, vehicleClassGroup)
            
    def _writeLanePermissionsToBaseFile(self, basefile_object):
        """
        Write version of _addLanePermissionsFromFields()
        *basefile_object* is the file object, ready for writing.        
        """
        basefile_object.write("LANE_PERMS\n")
        basefile_object.write("*    link  id                perms\n")
        
        count = 0
        for linkId in sorted(self._linksById.keys()):
            
            if (not isinstance(self._linksById[linkId], RoadLink) and
                not isinstance(self._linksById[linkId], Connector)):
                continue
            
            for laneId in range(self._linksById[linkId]._numLanes):
                if laneId not in self._linksById[linkId]._lanePermissions: continue # warn?
                basefile_object.write("%9d %3d %20s\n" % 
                                      (linkId,
                                       laneId,
                                       self._linksById[linkId]._lanePermissions[laneId].name))
                count += 1
        DtaLogger.info("Wrote %8d %-16s to %s" % (count, "LANE_PERMS", basefile_object.name))
    
    def _writeLinkEventsToBaseFile(self, basefile_object):
        """
        """
        basefile_object.write("LINK_EVENTS\n")
        basefile_object.write("*      id     time         std_att        value\n")
    
    def _writeLaneEventsToBaseFile(self, basefile_object):
        """
        """
        basefile_object.write("LANE_EVENTS\n")
        basefile_object.write("*    link  id     time                perms\n")
        
    def _parseVirtualLinkFromFields(self, fields):
        """
        Interprets fields into a VirtualLink
        """
        centroidId  = int(fields[0])
        linkId      = int(fields[1])
        
        centroid    = self._nodes[centroidId]
        connector   = self._linksById[linkId]

        if not isinstance(connector, Connector):
            raise DtaError("Virtual link specified with non-Connector link: %s" % str(connector))
        
        
        # no id -- make one up
        newId = self._maxLinkId + 1
        
        # if the connector is incoming to a virtual node, the the virtual link is incoming:
        # connector to centroid
        if connector._fromRoadNode:
            vlink = VirtualLink(id=newId,
                                startNode=connector.getEndNode(),
                                endNode=centroid,
                                label=None)
            # DtaLogger.debug("Creating virtual link from connector %d (node %d) to centroid %d" % 
            #                 (linkId, vlink.getStartNode().getId(), centroidId))            
        else:
            # the connector is outgoing to a virtual node, so the virtual link is outgoing:
            # connector to centroid
            vlink = VirtualLink(id=newId,
                            startNode=centroid,
                            endNode=connector.getStartNode(),
                            label=None)
            
            # DtaLogger.debug("Creating virtual link from centroid %d to connector %d (node %d)" % 
            #                 (centroidId, linkId, vlink.getEndNode().getId()))
     
        try:
            conn2 = vlink.getAdjacentConnector()
            assert(conn2 == connector)
        except DtaError:
            DtaLogger.warn(sys.exc_info()[1])
            raise
        except AssertionError:
            DtaLogger.warn("When creating Virtual Link from centroid %d to connector %d, different connector %d found" % 
                           (centroidId, linkId, conn2.getId()))
            raise
            
        return vlink
        
    def _writeVirtualLinksToBaseFile(self, basefile_object):
        """
        Write version of _parseVirtualLinkFromFields().  *basefile_object* is the file object,
        ready for writing.
        """
        basefile_object.write("VIRTUAL_LINKS\n")
        basefile_object.write("* centroid_id  link_id\n")
        
        count = 0
        for linkId in sorted(self._linksById.keys()):
            link = self._linksById[linkId]
            
            if not isinstance(link, VirtualLink): continue
            basefile_object.write("%13d %8d\n" %
                                  (link.getStartNode().getId() if isinstance(link.getStartNode(), Centroid) else link.getEndNode().getId(),
                                   link.getAdjacentConnector().getId()))
            count += 1
        DtaLogger.info("Wrote %8d %-16s to %s" % (count, "VIRTUAL_LINKS", basefile_object.name))

    def _parseMovementFromFields(self, fields):
        """
        Interprets fields into a Movement
        """
        nodeId          = int(fields[0])
        incomingLinkId  = int(fields[1])
        outgoingLinkId  = int(fields[2])
        freeflowSpeed   = float(fields[3])
        perms           = fields[4]
        numLanes        = int(fields[5])
        incomingLane    = int(fields[6])
        outgoingLane    = int(fields[7])
        followupTime    = float(fields[8])
    
        node                = self.getNodeForId(nodeId)
        incomingLink        = self.getLinkForId(incomingLinkId)
        outgoingLink        = self.getLinkForId(outgoingLinkId)
        vehicleClassGroup   = self._scenario.getVehicleClassGroup(perms)
        
        return Movement(node, incomingLink, outgoingLink, freeflowSpeed,
                        vehicleClassGroup,
                        None if numLanes==-1 else numLanes,
                        None if incomingLane==-1 else incomingLane,
                        None if outgoingLane==-1 else outgoingLane,
                        followupTime)
        
    def _writeMovementsToBaseFile(self, basefile_object):
        """
        Write version of _parseMovementFromFields().
        *basefile_object* is the file object, ready for writing.        
        """
        basefile_object.write("MOVEMENTS\n")
        basefile_object.write("*   at_node   inc_link   out_link       fspeed                perms lanes inlane outlane  tfollow\n")
        
        count = 0
        for linkId in sorted(self._linksById.keys()):
            
            if (not isinstance(self._linksById[linkId], RoadLink) and
                not isinstance(self._linksById[linkId], Connector)):
                continue
            
            for movement in self._linksById[linkId].iterOutgoingMovements():
                basefile_object.write("%11d %10d %10d %12s %20s %5d %6d %7d %8s\n" %
                                      (movement._node.getId(),
                                       movement.getIncomingLink().getId(),
                                       movement._outgoingLink.getId(),
                                       str(-1 if not movement._freeflowSpeed else movement._freeflowSpeed),
                                       movement._permission.name,
                                       -1 if not movement._numLanes else movement._numLanes,
                                       -1 if not movement._incomingLane else movement._incomingLane,
                                       -1 if not movement._outgoingLane else movement._outgoingLane,
                                       str(movement._followupTime)))
                count += 1
        DtaLogger.info("Wrote %8d %-16s to %s" % (count, "MOVEMENTS", basefile_object.name))                                           
        
    def retrieveCountListFromCountDracula(self, countDraculaReader, starttime, period, number, tolerance):
        """
        Writes counts to movements from CountDracula
        starttime = startitme for counts
        period = interval for each count
        number = total counts = (endtime-starttime)/period
        tolerance = tolerance for matching nodes in two databases in feet (5 ft is appropriate)        
        """
        #Can have additional arguments for aggregating counts, days and other args
        
        Movement.countNumber = number
        Movement.countPeriod = period
        Movement.countStartTime = starttime
        
        movementcounter = 0
        
        dtaNodes2countDraculaNodes_dict = {}  #Dictionary by dta node id: Key = dta_node_id, value = CD_node_id
        #counter = 0

        for dtanodeid in self._nodes:
            dtanode = self._nodes[dtanodeid]
            dta_node_x = dtanode.getX()
            dta_node_y = dtanode.getY()
            cd_node = countDraculaReader.mapNodeId(dta_node_x, dta_node_y, tolerance)
            
            #------ASSUMING there is a single match !!!!------ 
            if not cd_node == -1 :
                dtaNodes2countDraculaNodes_dict[dtanode.getId()] = cd_node
            
                #counter = counter+1
        
        print str(len(dtaNodes2countDraculaNodes_dict))+" nodes matched from "+str(len(self._nodes))+" nodes"
        
        for id in self._linksById:
            link = self._linksById[id]
            if not isinstance(link, VirtualLink):
        
        #TODO - Attach link counts
        #====================================================================
        # 
        # Here we can insert count attachment to links. For this we would need:
        # 1)counts[] instance variable for class link (or roadlink or connector)
        # 2)create getMainlineCountFromCountDracula method for countdracula.ReadFromCD class
        #   
        #====================================================================
                
 
                
                for movement in link.iterOutgoingMovements():
                    movementcounter += 1
                    #print movementcounter
                    #if movementcounter == 9000:
                    #    return
                    
                    if movement.getAtNode().getId() in dtaNodes2countDraculaNodes_dict: #check if node is in CD
                        atNode = dtaNodes2countDraculaNodes_dict[movement.getAtNode().getId()] #returns the nodes CD id
                        if movement.getOriginNode().getId() in dtaNodes2countDraculaNodes_dict:
                            fromNode = dtaNodes2countDraculaNodes_dict[movement.getOriginNode().getId()]
                            if movement.getDestinationNode().getId() in dtaNodes2countDraculaNodes_dict:
                                toNode = dtaNodes2countDraculaNodes_dict[movement.getDestinationNode().getId()]
                    
                                fromangle = movement.getIncomingLink().getReferenceAngle()
                                toangle = movement.getOutgoingLink().getReferenceAngle()
                                
                                countsList = countDraculaReader.getTurningCounts(atNode, fromNode, toNode, fromangle, toangle, starttime, period, number)
                                if not countsList == []: 
                                    #print "***************************************"
                                    movement.setCountsFromCountDracula(countsList)
                            
    def writeCountListToFile(self, dir, starttime, period, number):
        """
        Writes counts to movements from CountDracula
        starttime = startitme for counts
        period = interval for each count
        number = total counts = (endtime-starttime)/period
        tolerance = tolerance for matching nodes in two databases in feet (5 ft is appropriate)        
        """
       
        
        movementcounter = 0
        countList2write = []

        for id in self._linksById:
            link = self._linksById[id]
            if not isinstance(link, VirtualLink):
                for movement in link.iterOutgoingMovements():
                    
                    movementcounter += 1
                    #print movementcounter
                    
                    
                    atNode = movement.getAtNode().getId()
                    fromNode = movement.getOriginNode().getId()
                    toNode = movement.getDestinationNode().getId()
                    
                    movementcountsList = movement.getCountList()
                    
                    if not movementcountsList == []: 
                        countList2write.append([atNode,fromNode,toNode]+(movementcountsList))
        ## TODO Implement better csv file writer                  
        filewriter = csv.writer(open(dir+'\\movement_counts_user_attribute.csv', 'wb'),dialect = 'excel-tab', delimiter=' ',quotechar='|', quoting=csv.QUOTE_MINIMAL)
        filewriter.writerow("*atNode FromNode toNode starttime="+str(starttime)+" period="+str(period)+" number="+str(number))
        filewriter.writerows(countList2write)
        
    def _writeMovementEventsToBaseFile(self, basefile_object):
        """
        *basefile_object* is the file object, ready for writing.
        """
        basefile_object.write("MOVEMENT_EVENTS\n")
        basefile_object.write("*   at_node  inc_link   out_link     time         std_att        value\n")
        
    def _addShiftFromFields(self, fields):
        """
        Updates links by attaching permissions.
        """            
        linkId      = int(fields[0])
        startShift  = int(fields[1])
        endShift    = int(fields[2])
        
        link = self.getLinkForId(linkId)
        link.addShifts(startShift, endShift)
    
    def _writeShiftsToAdvancedFile(self, advancedfile_object):
        """
        Write version of _addLanePermissionsFromFields().  
        *advancedfile_object* is the file object, ready for writing.
        """
        advancedfile_object.write("SHIFTS\n")
        advancedfile_object.write("*      id  start-shift    end-shift\n")
        
        count = 0
        for linkId in sorted(self._linksById.keys()):
            link = self._linksById[linkId]
            
            if isinstance(link, RoadLink):
                (startShift,endShift) = link.getShifts()
                if startShift != None or endShift != None:
                    advancedfile_object.write("%9d %12d %12d\n" % (linkId, startShift, endShift))
                    
                    count += 1
        DtaLogger.info("Write %8d %-16s to %s" % (count, "SHIFTS", advancedfile_object.name))
        
    def _addShapePointsToLink(self, fields):
        """
        Update links by attaching shape points
        """
        linkId      = int(fields[0])
        sequenceNum = int(fields[1])
        xcoord      = float(fields[2])
        ycoord      = float(fields[3])
        
        link = self.getLinkForId(linkId)
        link.addShapePoint(xcoord, ycoord)

    def _writeShapePointsToAdvancedFile(self, advancedfile_object):
        """
        Write version of _addShapePointsToLink().  
        *advancedfile_object* is the file object, ready for writing.
        """
        advancedfile_object.write("VERTICES\n")
        advancedfile_object.write("*      id   sequence_num                     x-coordinate                     y-coordinate\n")
        
        count = 0
        for linkId in sorted(self._linksById.keys()):
            link = self._linksById[linkId]
            
            if isinstance(link, RoadLink) or isinstance(link, Connector):
                for seqnum, (x,y) in enumerate(link._shapePoints):
                    advancedfile_object.write("%9d %14d %32f %32f\n" % 
                                              (linkId, 
                                               seqnum,
                                               x,
                                               y))
                    
                    count += 1
        DtaLogger.info("Write %8d %-16s to %s" % (count, "VERTICES", advancedfile_object.name))

    def _writeControlFile(self, ctrl_object):
        """
        Output the control plans to disk
        """
        for planInfo in self.iterPlanCollectionInfo():
            ctrl_object.write(str(planInfo))            
            for node in sorted(self.iterRoadNodes(), key=lambda node: node.getId()):
                if node.hasTimePlan(planInfo):
                    tp = node.getTimePlan(planInfo)                    
                    ctrl_object.write(str(tp))                              

    def removeCentroidConnectorsFromIntersections(self, splitReverseLinks=False):
        """
        Remove centroid connectors from intersections and attach them to midblock locations.
        If there is not a node defining a midblock location the algorithm will split the 
        relevant links (in both directions) and attach the connector to the newly 
        created node.
        
        Before:
        
        .. image:: /images/removeCentroidConnectors1.png
           :height: 300px
        
        After:
        
        .. image:: /images/removeCentroidConnectors2.png
           :height: 300px
        
        .. todo:: why is this in :py:class:`DynameqNetwork` rather than :py:class:`Network`?
        
        """

        allRoadNodes = [node for node in self.iterNodes() if isinstance(node, RoadNode)]
        for node in allRoadNodes: 

            if not node.hasConnector():
                continue 
            
            connectors = [link for link in node.iterAdjacentLinks() if isinstance(link, Connector)]
                        
            for con in connectors:
                try:
                    self.removeCentroidConnectorFromIntersection(node, con, splitReverseLink=splitReverseLinks) 
                    #DtaLogger.info("Removed centroid connectors from intersection %d" % node.getId())
                except DtaError, e:
                    DtaLogger.error("%s" % str(e))

        #fix the number of lanes on the new connectors
        for node in self.iterNodes():

            if not node.isRoadNode():
                continue 
            if not node.hasConnector():
                continue 
            if node.isIntersection():                
                for link in node.iterAdjacentLinks():
                    if link.isConnector():
                        link.setNumLanes(1) 

            #remove the connector to connector movements
            movementsToDelete = []
            
            for ilink in node.iterIncomingLinks():                
                for olink in node.iterOutgoingLinks():
                    if ilink.isConnector() and olink.isConnector():
                        if ilink.hasOutgoingMovement(olink.getEndNodeId()):
                            mov = ilink.getOutgoingMovement(olink.getEndNodeId())
                            ilink.removeOutgoingMovement(mov)
                        else:
                            prohibitedMovement = Movement.simpleMovementFactory(ilink, olink,
                                 self.getScenario().getVehicleClassGroup(VehicleClassGroup.PROHIBITED))
                            ilink.addOutgoingMovement(prohibitedMovement) 
                    else:
                        if not ilink.hasOutgoingMovement(olink.getEndNode().getId()):
                            
                            allowedMovement = Movement.simpleMovementFactory(ilink, olink,
                               self.getScenario().getVehicleClassGroup(VehicleClassGroup.ALL))
                            ilink.addOutgoingMovement(allowedMovement)
                    
    def removeCentroidConnectorFromIntersection(self, roadNode, connector, splitReverseLink=False):
        """
        Remove the input connector for an intersection and attach it to a midblock 
        location. If a midblock location does does not exist a RoadLink close
        to the connector is split in half and the connector is attached to the new 
        midblock location
        
        .. todo:: This is insufficient documentation.  I'm currently getting a lot of errors about VehicleClassGroups.
        """
        if not isinstance(roadNode, RoadNode):
            raise DtaError("Input Node %d is not a RoadNode" % roadNode.getId())
        if not isinstance(connector, Connector):
            raise DtaError("Input Link %s is not a Connector" % connector.getId())
        
        if not roadNode.hasConnector():
            raise DtaError("RoadNode %d does not have a connector attached to it"
                           % roadNode.getId())

        centroid = connector.getCentroid()
        candidateLinks = roadNode.getCandidateLinksForSplitting(connector)

        nodeToAttachConnector = None

        if len(candidateLinks) >= 2: 

            cNode1 = candidateLinks[0].getOtherEnd(roadNode)
            cNode2 = candidateLinks[1].getOtherEnd(roadNode)
            
            #if cNode1.isShapePoint(countRoadNodesOnly=True) and not centroid.isConnectedToRoadNode(cNode1):
            if cNode1.isShapePoint(countRoadNodesOnly=True):
                nodeToAttachConnector = candidateLinks[0].getOtherEnd(roadNode)
            elif cNode2.isShapePoint(countRoadNodesOnly=True):#  and not centroid.isConnectedToRoadNode(cNode2):            
                nodeToAttachConnector = candidateLinks[1].getOtherEnd(roadNode)
            else:                    
                nodeToAttachConnector = self.splitLink(candidateLinks[0], splitReverseLink=splitReverseLink)

        elif len(candidateLinks) == 1:
            
            cNode = candidateLinks[0].getOtherEnd(roadNode)            
            if cNode.isShapePoint(countRoadNodesOnly=True):# and not centroid.isConnectedToRoadNode(cNode):
                nodeToAttachConnector = candidateLinks[0].getOtherEnd(roadNode) 
            else:
                nodeToAttachConnector = self.splitLink(candidateLinks[0], splitReverseLink=splitReverseLink) 
        else:
            raise DtaError("Centroid connector(s) were not removed from intersection %d" % roadNode.getId())
                    
        if connector.startIsRoadNode():
            virtualNode = connector.getEndNode() 

            length = math.sqrt((nodeToAttachConnector.getX() - virtualNode.getX()) ** 2 + 
                (nodeToAttachConnector.getY() - virtualNode.getY()) ** 2)

            newConnector = Connector(connector.getId(),
                                     nodeToAttachConnector,
                                     virtualNode,
                                     None,
                                     length, 
                                     connector._freeflowSpeed,
                                     connector._effectiveLengthFactor,
                                     connector._responseTimeFactor,
                                     connector._numLanes,
                                     connector._roundAbout,
                                     connector._level, 
                                     connector._label)

            self.removeLink(connector)
            self.addLink(newConnector)
            #TODO: do the movements
            return newConnector 
        else:
            virtualNode = connector.getStartNode() 

            length = math.sqrt((nodeToAttachConnector.getX() - virtualNode.getX()) ** 2 + 
                (nodeToAttachConnector.getY() - virtualNode.getY()) ** 2)

            newConnector = Connector(connector.getId(),
                                     virtualNode,
                                     nodeToAttachConnector,
                                     None,
                                     length, 
                                     connector._freeflowSpeed,
                                     connector._effectiveLengthFactor,
                                     connector._responseTimeFactor,
                                     connector._numLanes,
                                     connector._roundAbout,
                                     connector._level, 
                                     connector._label)

            self.removeLink(connector)
            self.addLink(newConnector)
            #TODO: do the movements 
            return newConnector 
    
    def iterVirtualNodes(self):
        """
        Return an iterator to the :py:class:`VirtualNode` instances in the network.
        
        .. todo:: Move this to :py:class:`Network`.
        
        """
        for node in self.iterNodes():
            if isinstance(node, VirtualNode):
                yield node 

    def iterRoadNodes(self):
        """
        Return an iterator to the :py:class:`RoadNode` instances in the network.
        
        .. todo:: Move this to :py:class:`Network`.
        
        """
        for node in self.iterNodes():
            if isinstance(node, RoadNode):
                yield node

    def iterCentroids(self):
        """
        Return an iterator to the :py:class:`Centroid` instances in the network.

        .. todo:: Move this to :py:class:`Network`.
        
        """
        for node in self.iterNodes():
            if isinstance(node, Centroid):
                yield node 

    def iterVirtualLinks(self):
        """
        Return an iterator to the :py:class:`VirtualLink` instances in the network.

        .. todo:: Move this to :py:class:`Network`.

        """
        for link in self.iterLinks():
            if isinstance(link, VirtualLink):
                yield link

    def iterRoadLinks(self):
        """
        Return an iterator for to the :py:class:`RoadLink` instances in the network that are 
        not instances of :py:class:`Connector`.
        
        .. todo:: Move this to :py:class:`Network`.

        """
        for link in self.iterLinks():
            if link.isRoadLink():
                yield link 

    def iterConnectors(self):
        """
        Return an iterator to the :py:class:`Connector` instances in the network.

        .. todo:: Move this to :py:class:`Network`.
        
        """
        for link in self.iterLinks():
            if isinstance(link, Connector):
                yield link

    def _readMovementOutFlowsAndTTs(self):
        """
        Read the movement travel times (in seconds) add assign them 
        to the corresponding movement
        """
        if not self._dir:
            raise DtaError("The network directory has not been defined")
        
        movementFlowFileName = os.path.join(self._dir, 
                                            DynameqNetwork.MOVEMENT_FLOW_OUT)
        movementTimeFileName = os.path.join(self._dir,
                                            DynameqNetwork.MOVEMENT_TIME_OUT)

        inputStream1 = open(movementFlowFileName, 'r')
        inputStream2 = open(movementTimeFileName, 'r')

        for flowLine, timeLine in izip(inputStream1, inputStream2):
            
            flowFields = flowLine.strip().split()
            timeFields = timeLine.strip().split()

            nodeBid, nodeAid, nodeCid = map(int, flowFields[:3])

            if [nodeBid, nodeAid, nodeCid] != map(int, timeFields[:3]):
                raise DtaError('The files %s and %s are not in sync. '
                                      'Movement through %s from %s to %s in the first file is not '
                                      'in the same line position in the second '
                                      'file' % (movementFlowFileName,
                                                movementTimeFileName,
                                                nodeBid, nodeAid, nodeCid))

            try:
                link = self.getLinkForNodeIdPair(nodeAid, nodeBid)
                movement = link.getOutgoingMovement(nodeCid)
            except DtaError, e:
                #if the movement does not exist. It could be a prohibited movement
                #perhaps you need to do more error checking there 
                if nodeAid == nodeCid:
                    continue
                continue

            simFlows = imap(int, flowFields[3:])
            simTTs = imap(float, timeFields[3:])
            timePeriodStart = self._simStartTimeInMin
                    
            for simFlow, simTT in izip(simFlows, simTTs):

                if simFlow == 0 and simTT > 0:
                    raise DtaError('Movement %s has zero flow in the '
                                   'time period begining %d and a '
                                   'positive travel time' % 
                                   (movement.getId(), timePeriodStart))
                elif simFlow > 0 and simTT == 0:
                    raise DtaError('Movement %s has positive flow in '
                                   'the time period begining %d and a '
                                   'zero travel time' % 
                                   (movement.getId(), timePeriodStart))
                
                elif simFlow == 0 and simTT == 0:
                    #simTT = movement.getFreeFlowTTInMin()
                    timePeriodStart += self._simTimeStepInMin
                    if timePeriodStart >= self._simEndTimeInMin:
                        break
                else:
                    movement.setSimVolume(timePeriodStart, timePeriodStart + 
                                        self._simTimeStepInMin, simFlow / (60 / self._simTimeStepInMin))

                    movement.setSimTTInMin(timePeriodStart, timePeriodStart + 
                                          self._simTimeStepInMin, simTT / 60.0)
                                      
                    timePeriodStart += self._simTimeStepInMin
                    if timePeriodStart >= self._simEndTimeInMin:
                        break

        inputStream1.close()
        inputStream2.close()

    def removeDuplicateConnectors(self):
        """
        Remove duplicate connectors that connect from the
        same centroid to the same road node
        """
        vNodesToDelete = set()
        for node in self.iterCentroids():
            result = defaultdict(list)
            for vNode in node.iterAdjacentNodes():
                if not vNode.isVirtualNode():
                    continue
                rNode = vNode.getConnectedRoadNode()
                result[rNode.getId()].append(vNode)
            for rNode, vNodes in result.iteritems():
                if len(vNodes) > 1:
                   for vNodeToRemove in vNodes[1:]:
                       vNodesToDelete.add(vNodeToRemove)

        for vNodeToDelete in vNodesToDelete:
            self.removeNode(vNodeToDelete)
                               
    def readSimResults(self, simStartTimeInMin, simEndTimeInMin, simTimeStepInMin):
        """
        Read the movement and link travel times and flows
        """
        self._simStartTimeInMin = simStartTimeInMin
        self._simEndTimeInMin = simEndTimeInMin
        self._simTimeStepInMin = simTimeStepInMin


        for link in self.iterLinks():
            if link.isVirtualLink():
                continue
            for mov in link.iterOutgoingMovements():
                mov.simTimeStepInMin = simTimeStepInMin
                mov.simStartTimeInMin = simStartTimeInMin
                mov.simEndTimeInMin = simEndTimeInMin

        self._readMovementOutFlowsAndTTs()

        
        
        

                    
