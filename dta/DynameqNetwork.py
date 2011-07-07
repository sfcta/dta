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
import os
import sys
from .Centroid import Centroid
from .Connector import Connector
from .DtaError import DtaError
from .Logger import DtaLogger
from .Movement import Movement
from .Network import Network
from .Node import Node
from .RoadLink import RoadLink
from .RoadNode import RoadNode
from .VirtualLink import VirtualLink
from .VirtualNode import VirtualNode

class DynameqNetwork(Network):
    """
    A Dynameq DTA Network.
    """
    
    BASE_FILE       = '%s_base.dqt'
    ADVANCED_FILE   = '%s_advn.dqt'
    CONTROL_FILE    = '%s_ctrl.dqt'
    TRANSIT_FILE    = '%s_ptrn.dqt'
    PRIORITIES_FILE = '%s_prio.dqt'
    
    def __init__(self, scenario):
        """
        Constructor.  Initializes to an empty network.
        
        Keeps a reference to the given dynameqScenario (a :py:class:`DynameqScenario` instance)
        for :py:class:`VehicleClassGroup` lookups        
        """ 
        Network.__init__(self, scenario)

        
    def read(self, dir, file_prefix, ):
        """
        Reads the network in the given *dir* with the given *file_prefix*.

        """
        # base file processing
        basefile = os.path.join(dir, DynameqNetwork.BASE_FILE % file_prefix)
        if not os.path.exists(basefile):
            raise DtaError("Base network file %s does not exist" % basefile)
        
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
            # TODO do LINK_EVENTS have to correspond to scenario events?
            print fields
            count += 1
        DtaLogger.info("Read  %8d %-16s from %s" % (count, "LINK_EVENTS", basefile))

        count = 0
        for fields in self._readSectionFromFile(basefile, "LANE_EVENTS", "VIRTUAL_LINKS"):
            # TODO do LANE_EVENTS have to correspond to scenario events?
            print fields
            count += 1
        DtaLogger.info("Read  %8d %-16s from %s" % (count, "LANE_EVENTS", basefile))
            
        count = 0
        for fields in self._readSectionFromFile(basefile, "VIRTUAL_LINKS", "MOVEMENTS"):
            self.addLink(self._parseVirtualLinkFromFields(fields))
            count += 1
        DtaLogger.info("Read  %8d %-16s from %s" % (count, "VIRTUAL_LINKS", basefile))
            
        count = 0                        
        for fields in self._readSectionFromFile(basefile, "MOVEMENTS", "MOVEMENT_EVENTS"):
            self.addMovement(self._parseMovementFromFields(fields))
            count += 1
        DtaLogger.info("Read  %8d %-16s from %s" % (count, "MOVEMENTS", basefile))
                
    def write(self, dir, file_prefix):
        """
        Writes the network into the given *dir* with the given *file_prefix*
        """
        basefile = os.path.join(dir, DynameqNetwork.BASE_FILE % file_prefix)
        
        basefile_object = open(basefile, "w")
        self._writeNodesToBaseFile(basefile_object)
        self._writeCentroidsToBaseFile(basefile_object)
        self._writeLinksToBasefile(basefile_object)
        self._writeLanePermissionsToBaseFile(basefile_object)
        self._writeVirtualLinksToBaseFile(basefile_object)
        self._writeMovementsToBaseFile(basefile_object)
        basefile_object.close()

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
        for nodeId in sorted(self._nodes.keys()):
            node = self._nodes[nodeId]
            if isinstance(node, Centroid):
                continue # don't write centroids; they go in their own section
            elif isinstance(node, VirtualNode):
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
        label   = fields[12]
        if label[0] == '"' and label[-1] ==  '"':
            label = label[1:-1]
            
        startNode = self.getNodeForId(startid)
        endNode = self.getNodeForId(endid)
        
        if (isinstance(startNode, Centroid) or isinstance(endNode, Centroid) or
            isinstance(startNode, VirtualNode) or isinstance(endNode, VirtualNode)):
            
            return Connector(id, startNode, endNode, reverseAttachedLinkId=rev, 
                                facilityType=faci, length=length,
                                freeflowSpeed=fspeed, effectiveLengthFactor=lenfac, 
                                responseTimeFactor=resfac, numLanes=lanes,
                                roundAbout=rabout, level=level, label=label)
        
        # are these all RoadLinks?  What about VirtualLinks?
        return RoadLink(id, startNode, endNode, reverseAttachedLinkId=rev, 
                           facilityType=faci, length=length,
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
        for linkId in sorted(self._linksById.keys()):
            link = self._linksById[linkId]
            
            # virtual links are later
            if isinstance(link, VirtualLink): continue
            
            basefile_object.write("%9d %8d %8d %7d %4d %12f %12f %8f %8f %5d %5d %6d %13s\n" % 
                                  (link.id,
                                   link.getStartNode().getId(),
                                   link.getEndNode().getId(),
                                   link._reverseAttachedLinkId,
                                   link._facilityType,
                                   link._length,
                                   link._freeflowSpeed,
                                   link._effectiveLengthFactor,
                                   link._responseTimeFactor,
                                   link._numLanes,
                                   link._roundAbout,
                                   link._level,
                                   '"' + link.label + '"'))
            count += 1
        DtaLogger.info("Wrote %8d %-16s to %s" % (count, "LINKS", basefile_object.name))
        
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
        Write version of _addLanePermissionsFromFields().  *basefile_object* is the file object,
        ready for writing.        
        """
        basefile_object.write("LANE_PERMS\n")
        basefile_object.write("*    link  id                perms\n")
        
        count = 0
        for linkId in sorted(self._linksById.keys()):
            
            if (not isinstance(self._linksById[linkId], RoadLink) and
                not isinstance(self._linksById[linkId], Connector)):
                continue
            
            for laneId in range(self._linksById[linkId]._numLanes):
                basefile_object.write("%9d %3d %20s\n" % 
                                      (linkId,
                                       laneId,
                                       self._linksById[linkId]._lanePermissions[laneId].name))
                count += 1
        DtaLogger.info("Wrote %8d %-16s to %s" % (count, "LANE_PERMS", basefile_object.name))
    
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
                           (centroidId, linkId, conn2.id))
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
                                  (link.getStartNode().getId(),
                                   link.getAdjacentConnector().id))
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
        Write version of _parseMovementFromFields().  *basefile_object* is the file object,
        ready for writing.        
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
                                       movement.getIncomingLink().id,
                                       movement._outgoingLink.id,
                                       str(-1 if not movement._freeflowSpeed else movement._freeflowSpeed),
                                       movement._permission.name,
                                       -1 if not movement._numLanes else movement._numLanes,
                                       -1 if not movement._incomingLane else movement._incomingLane,
                                       -1 if not movement._outgoingLane else movement._outgoingLane,
                                       str(movement._followupTime)))
                count += 1
        DtaLogger.info("Wrote %8d %-16s to %s" % (count, "MOVEMENTS", basefile_object.name))