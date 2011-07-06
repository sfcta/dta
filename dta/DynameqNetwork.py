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
from .Centroid import Centroid
from .Connector import Connector
from .DtaError import DtaError
from .Logger import DtaLogger
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
    
    def __init__(self, dir, file_prefix, scenario):
        """
        Constructor.  Reads the network in the given *dir* with the given *file_prefix*.
        
        Keeps a reference to the given dynameqScenario (a :py:class:`DynameqScenario` instance)
        for :py:class:`VehicleClassGroup` lookups
        
        """
        Network.__init__(self, scenario)
        
        # base file processing
        basefile = os.path.join(dir, DynameqNetwork.BASE_FILE % file_prefix)
        if not os.path.exists(basefile):
            raise DtaError("Base network file %s does not exist" % basefile)
        
        for fields in self._readSectionFromFile(basefile, "NODES", "CENTROIDS"):
            self.addNode(self._parseNodeFromFields(fields))

        for fields in self._readSectionFromFile(basefile, "CENTROIDS", "LINKS"):
            self.addCentroid(self._parseCentroidFromFields(fields))
        
        for fields in self._readSectionFromFile(basefile, "LINKS", "LANE_PERMS"):
            self.addLink(self._parseLinkFromFields(fields))
            
        for fields in self._readSectionFromFile(basefile, "LANE_PERMS", "LINK_EVENTS"):
            self._addLanePermissionFromFields(fields)
            
        for fields in self._readSectionFromFile(basefile, "LINK_EVENTS", "LANE_EVENTS"):
            # TODO do LINK_EVENTS have to correspond to scenario events?
            print fields
            
        for fields in self._readSectionFromFile(basefile, "LANE_EVENTS", "VIRTUAL_LINKS"):
            # TODO do LANE_EVENTS have to correspond to scenario events?
            print fields

        for fields in self._readSectionFromFile(basefile, "VIRTUAL_LINKS", "MOVEMENTS"):
            (vlink1, vlink2) = self._parseVirtualLinkFromFields(fields)
            self.addVirtualLink(vlink1)
            self.addVirtualLink(vlink2)
        return
            
        for fields in self._readSectionFromFile(basefile, "MOVEMENTS", "MOVEMENT_EVENTS"):
            print fields            
                    
    def __del__(self):
        pass
    
    def write(self, dir, file_prefix):
        basefile = os.path.join(dir, DynameqNetwork.BASE_FILE % file_prefix)
        
        basefile_object = open(basefile, "w")
        self._writeNodesToBaseFile(basefile_object)
        self._writeCentroidsToBaseFile(basefile_object)
        self._writeLinksToBasefile(basefile_object)
        self._writeLanePermissionsToBaseFile(basefile_object)
        self._writeVirtualLinksToBaseFile(basefile_object)
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
        for nodeId in sorted(self._nodes.keys()):
            node = self._nodes[nodeId]
            if isinstance(node, VirtualNode):
                control = VirtualNode.DEFAULT_CONTROL
                priority = VirtualNode.DEFAULT_PRIORITY
            else:
                control = node._control
                priority = node._priority

            basefile_object.write("%9d %20.6f %20.6f %8d %8d %4d %6d %12s\n" %
                                  (node.id,
                                   node.x,
                                   node.y,
                                   control,
                                   priority,
                                   node._type,
                                   node._level,
                                   '"' + node._label + '"'))

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
        for nodeId in sorted(self._centroids.keys()):
            centroid = self._centroids[nodeId]
            basefile_object.write("%9d %20.6f %20.6f %6d %s\n" % 
                                  (centroid.id,
                                   centroid.x,
                                   centroid.y,
                                   centroid._level,
                                   '"' + centroid._label + '"'))

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
            
        nodeA = self.getNodeForId(startid)
        nodeB = self.getNodeForId(endid)
        
        if (isinstance(nodeA, Centroid) or isinstance(nodeB, Centroid) or
            isinstance(nodeA, VirtualNode) or isinstance(nodeB, VirtualNode)):
            
            DtaLogger.debug("Connector has faci %d length %f" % (faci, length))
            return Connector(id, nodeA, nodeB, reverseAttachedLinkId=rev, 
                                facilityType=faci, length=length,
                                freeflowSpeed=fspeed, effectiveLengthFactor=lenfac, 
                                responseTimeFactor=resfac, numLanes=lanes,
                                roundAbout=rabout, level=level, label=label)
        
        # are these all RoadLinks?  What about VirtualLinks?
        return RoadLink(id, nodeA, nodeB, reverseAttachedLinkId=rev, 
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
        

        for linkId in sorted(self._links.keys()):
            link = self._links[linkId]
            basefile_object.write("%9d %8d %8d %7d %4d %12f %12f %8f %8f %5d %5d %6d %13s\n" % 
                                  (link.id,
                                   link.nodeA.id,
                                   link.nodeB.id,
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
        for linkId in sorted(self._links.keys()):
            if not isinstance(self._links[linkId], RoadLink): continue
            for laneId in range(self._links[linkId]._numLanes):
                basefile_object.write("%9d %3d %20s\n" % 
                                      (linkId,
                                       laneId,
                                       self._links[linkId]._lanePermissions[laneId].name))
    
    def _parseVirtualLinkFromFields(self, fields):
        """
        Interprets fields into two VirtualLink (one in each direction)
        """
        centroidId  = int(fields[0])
        linkId      = int(fields[1])
        
        centroid    = self._centroids[centroidId]
        connector   = self._links[linkId]

        if not isinstance(connector, Connector):
            raise DtaError("Virtual link specified with non-Connector link: %s" % str(connector))
        
        return (VirtualLink(id=None,
                            nodeA=centroid, 
                            nodeB=(connector.nodeB if connector._fromRoadNode else connector.nodeA),
                            label=None,
                            connector=connector),
                VirtualLink(id=None,
                            nodeA=(connector.nodeB if connector._fromRoadNode else connector.nodeA),
                            nodeB=centroid,
                            label=None,
                            connector=connector))
        
    def _writeVirtualLinksToBaseFile(self, basefile_object):
        """
        Write version of _parseVirtualLinkFromFields().  *basefile_object* is the file object,
        ready for writing.
        """
        basefile_object.write("VIRTUAL_LINKS\n")
        basefile_object.write("* centroid_id  link_id\n")
        for virtualLink in self._virtualLinks:
            # these are bidirectional so ignore those with NodeB as the centroid
            if isinstance(virtualLink.nodeB, Centroid): continue
            # nodeA is a centroid
            basefile_object.write("%13d %8d\n" %
                                  (virtualLink.nodeA.id,
                                   virtualLink._connector.id))