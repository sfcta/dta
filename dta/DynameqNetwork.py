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
from .DtaError import DtaError
from .Logger import DtaLogger
from .Network import Network
from .Node import Node
from .RoadLink import RoadLink
from .RoadNode import RoadNode
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
    
    def __init__(self, dir, file_prefix):
        """
        Constructor.  Reads the network in the given *dir* with the given *file_prefix*.
        
        """
        Network.__init__(self)
        
        # base file processing
        basefile = os.path.join(dir, DynameqNetwork.BASE_FILE % file_prefix)
        if not os.path.exists(basefile):
            raise DtaError("Base network file %s does not exist" % basefile)
        
        for node in self._readNodesFromBaseFile(basefile):
            self.addNode(node)

        for centroid in self._readCentroidsFromBaseFile(basefile):
            self.addCentroid(centroid)
        
        for link in self._readLinksFromBaseFile(basefile):
            self.addLink(link)
        
    def __del__(self):
        pass
    
    def write(self, dir, file_prefix):
        basefile = os.path.join(dir, DynameqNetwork.BASE_FILE % file_prefix)
        
        basefile_object = open(basefile, "w")
        self._writeNodesToBaseFile(basefile_object)
        self._writeCentroidsToBaseFile(basefile_object)
        self._writeLinksToBasefile(basefile_object)
        basefile_object.close()

    def _readNodesFromBaseFile(self, basefile):
        """
        Generator function, yields RoadNode and VirtualNode instances to the caller
        """
        lines = open(basefile, "r")
        curLine = lines.next().strip()
        try:
            while curLine !="NODES":
                curLine = lines.next().strip()
        except StopIteration:
            raise DtaError("Base network file %s: cannot locate the Node section" % basefile)
        
        curLine = lines.next().strip()  # should be the header
        curLine = lines.next().strip()  # should be the first record
        
        while not curLine == "CENTROIDS":
            fields  = curLine.split()
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
                yield RoadNode(id, x, y, type, control, priority, label, level)
            elif type == Node.GEOMETRY_TYPE_VIRTUAL:
                yield VirtualNode(id, x, y, label, level)
            else:
                raise DtaError("Found Node of unrecognized type %d in NODES section of %s" % (type, fullfile))
                
            curLine = lines.next().strip()

        lines.close()
        raise StopIteration

    def _writeNodesToBaseFile(self, basefile_object):
        """
        Write version of _readNodesFromBaseFile().  *basefile_object* is the file object,
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

    def _readCentroidsFromBaseFile(self, basefile):
        """
        Generator function, yields Centroid instances to the caller
        """
        lines = open(basefile, "r")
        curLine = lines.next().strip()
        try:
            while curLine !="CENTROIDS":
                curLine = lines.next().strip()
        except StopIteration:
            raise DtaError("Base network file %s: cannot locate the Centroids section" % basefile)
        curLine = lines.next().strip()  # should be the header
        curLine = lines.next().strip()  # should be the first record
        while not curLine =="LINKS":
                  
            fields  = curLine.split()
            id      = int(fields[0])
            x       = float(fields[1])
            y       = float(fields[2])
            level   = int(fields[3])
            label   = fields[4]
            if label[0] == '"' and label[-1] ==  '"':
                label = label[1:-1]
            
            yield Centroid(id, x, y, label=label, level=level)
            curLine = lines.next().strip()
        lines.close()
        raise StopIteration
    
    def _writeCentroidsToBaseFile(self, basefile_object):
        """
        Write version of _readCentroidsFromBaseFile().  *basefile_object* is the file object,
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

    def _readLinksFromBaseFile(self, basefile):
        """
        Generator function, yields Link instances to the caller
        """
        line = open(basefile, "r")
        curLine = line.next().strip()
        try:
            while curLine != "LINKS":
                curLine = line.next().strip()
        except StopIteration:
            raise DtaError("Base network file %s: cannot locate the Links section" % basefile)
        
        curLine = line.next().strip()  # this is the header
        curLine = line.next().strip()  # this is the first record
        while curLine !="LANE_PERMS":
            fields = curLine.split()
            
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
            
            if nodeA == None:
                raise DtaError("Base network file link read with unknown node A ID: %d" % startid)
            if nodeB == None:
                raise DtaError("Base network file link read with unknown node B ID: %d" % endid)
            
            if isinstance(nodeA, Centroid) or isinstance(nodeB, Centroid):
                DtaLogger.debug("Connector has faci %d length %")
                newLink = Connector(id, nodeA, nodeB, reverseAttachedLinkId=rev, 
                                    facilityType=faci, length=length,
                                    freeflowSpeed=fspeed, effectiveLengthFactor=lenfac, 
                                    responseTimeFactor=resfac, numLanes=lanes,
                                    roundAbout=rabout, level=level, label=label)
            
            else:
                # are these all RoadLinks?  What about VirtualLinks?
                newLink = RoadLink(id, nodeA, nodeB, reverseAttachedLinkId=rev, 
                                   facilityType=faci, length=length,
                                   freeflowSpeed=fspeed, effectiveLengthFactor=lenfac, 
                               responseTimeFactor=resfac, numLanes=lanes,
                               roundAbout=rabout, level=level, label=label)                    
                
            yield newLink
                             
            curLine = line.next().strip()
        line.close()
        raise StopIteration
    
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