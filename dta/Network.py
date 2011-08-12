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
import copy
from .Centroid import Centroid
from .Connector import Connector
from .DtaError import DtaError
from .Link import Link
from .RoadLink import RoadLink
from .Logger import DtaLogger
from .RoadNode import RoadNode
from .Scenario import Scenario
from .VirtualLink import VirtualLink
from .VirtualNode import VirtualNode
from .VehicleClassGroup import VehicleClassGroup
from .Movement import Movement

class Network(object):
    """
    Base class that represents a DTA Network.  Networks exist on a continuum between
    macro- and micro-simulation, and this network is meant to represent something
    "typical" for a mesosimulation.  Something to be aware of in case it becomes too complicated.
    
    Subclasses will be used to represent networks for different frameworks (Dynameq, Cube, etc)
    so this class should have no code to deal with any particular file formats.
    
    """
    
    def __init__(self, scenario):
        """
        Constructor.  Initializes to an empty network, stores reference to given
        scenario (a :py:class:`Scenario` instance).
        """
        
        #: node id -> node; these can be instances of :py:class:`RoadNode` :py:class:`VirtualNode` or
        #: :py:class:`Centroid`
        self._nodes         = {}
        #: link id -> :py:class:`Link` (these are :py:class:`RoadLink`s and :py:class:`Connector`s)
        self._linksById     = {}
        #: (nodeA id, nodeB id) -> :py:class:`Link` (these are :py:class:`RoadLink`s and :py:class:`Connector`s)
        self._linksByNodeIdPair = {}
        
        #: maximum link id
        self._maxLinkId     = 0
        #: maximum node id
        self._maxNodeId     = 0
        
        #: the relevant :py:class:`Scenario` instance
        if not isinstance(scenario, Scenario):
            raise DtaError("Network __init__ received invalid scenario %s (not Scenario instance)" %
                           str(scenario))
            
        self._scenario = scenario
        
    def __del__(self):
        pass
    
    def copy(self, originNetwork):
        """
        Copies the contents of the originNetwork into self (Nodes and Links and Movements
        , not the scenario).
        """
        #self._nodes     = copy.deepcopy(originNetwork._nodes)
        #self._linksById = copy.deepcopy(originNetwork._linksById)
        #
        #self._linksByNodeIdPair = {}
        #for link in self._linksById.itervalues():
        #    self._linksByNodeIdPair[(link.getStartNode().getId(), link.getEndNode().getId())] = link
        #

        self._maxLinkId = originNetwork._maxLinkId
        self._maxNodeId = originNetwork._maxNodeId
        
        for node in originNetwork.iterNodes():            
            cNode = copy.copy(node) 
            cNode._incomingLinks = []
            cNode._outgoingLinks = []
            self.addNode(cNode)

        for link in originNetwork.iterLinks():
            cLink = copy.copy(link)
            cLink._startNode = self.getNodeForId(link._startNode.getId())
            cLink._endNode = self.getNodeForId(link._endNode.getId())
            if isinstance(link, RoadLink):                
                cLink._outgoingMovements = []
                cLink._incomingMovements = [] 
            self.addLink(cLink) 

        for link in originNetwork.iterLinks():
            if isinstance(link, RoadLink):                
                for mov in link.iterOutgoingMovements():
                    cLink = self.getLinkForId(link.getId())
                    cMov = copy.copy(mov)
                    cMov._node = self.getNodeForId(mov._node.getId())
                    cMov._incomingLink = self.getLinkForId(mov._incomingLink.getId())
                    cMov._outgoingLink = self.getLinkForId(mov._outgoingLink.getId())

                    cLink.addOutgoingMovement(cMov) 
        
    def addNode(self, newNode):
        """
        Verifies that *newNode* is a :py:class:`RoadNode`, :py:class:`VirtualNode` or :py:class:`Centroid`
        and that the id is not already used; stores it.
        """
        if (not isinstance(newNode, RoadNode) and 
            not isinstance(newNode, VirtualNode) and 
            not isinstance(newNode, Centroid)):
            raise DtaError("Network.addNode called on non-RoadNode/VirtualNode/Centroid: %s" % str(newNode))

        if newNode.getId() in self._nodes:
            raise DtaError("Network.addNode called on node with id %d already in the network (for a node)" % newNode.getId())

        self._nodes[newNode.getId()] = newNode
        
        if newNode.getId() > self._maxNodeId: self._maxNodeId = newNode.getId()

    def getNumNodes(self):
        """
        Returns the number of nodes in the network
        """
        return len(self._nodes)

    def getNumRoadNodes(self):
        """
        Returns the number of roadnodes in the network
        """
        return sum(1 for node in self.iterNodes() if isinstance(node, RoadNode))

    def getNumCentroids(self):
        """
        Returns the number of centroids in the network
        """
        return sum(1 for node in self.iterNodes() if isinstance(node, Centroid))

    def getNumVirtualNodes(self):
        """
        Returns the number of virtual nodes in the network
        """
        return sum(1 for node in self.iterNodes() if isinstance(node, VirtualNode))
        
    def getNumLinks(self):
        """
        Returns the number of links in the network
        """
        return len(self._linksById)

    def getNodeForId(self, nodeId):
        """
        Accessor for node given the *nodeId*.
        Raises :py:class:`DtaError` if not found.
        """
        if nodeId in self._nodes:
            return self._nodes[nodeId]
        
        raise DtaError("Network getNodeForId: none found for id %d" % nodeId)
    
    def addLink(self, newLink):
        """
        Verifies that:
        
         * the *newLink* is a Link
         * that the id is not already used
         * the nodepair is not already used
         
        Stores it.
        """ 

        if not isinstance(newLink, Link):
            raise DtaError("Network.addLink called on a non-Link: %s" % str(newLink))

        if newLink.id in self._linksById:
            raise DtaError("Link with id %s already exists in the network" % newLink.id)
        if (newLink.getStartNode().getId(), newLink.getEndNode().getId()) in self._linksByNodeIdPair:
            raise DtaError("Link for nodes (%d,%d) already exists in the network" % 
                           (newLink.getStartNode().getId(), newLink.getEndNode().getId()))
        
        self._linksById[newLink.id] = newLink
        self._linksByNodeIdPair[(newLink.getStartNode().getId(), newLink.getEndNode().getId())] = newLink
        
        if newLink.id > self._maxLinkId: self._maxLinkId = newLink.id
        
        #newLink.updateNodesAdjacencyLists()
        #TODO: Ok I am accessing the internals of the startNode so this is not OO
        #but is there a better way? If C++ we would do a friend function.
        #do you think there is a better way? 
        newLink.getStartNode()._addOutgoingLink(newLink)
        newLink.getEndNode()._addIncomingLink(newLink)

    
    def getLinkForId(self, linkId):
        """
        Accessor for link given the *linkId*.
        Raises :py:class:`DtaError` if not found.
        """
        if linkId in self._linksById:
            return self._linksById[linkId]
        
        raise DtaError("Network getLinkForId: none found for id %d" % linkId)
    
    def getLinkForNodeIdPair(self, nodeAId, nodeBId):
        """
        Accessor for the link given the link nodes.
        Raises :py:class:`DtaError` if not found.        
        """
        if (nodeAId,nodeBId) in self._linksByNodeIdPair:
            return self._linksByNodeIdPair[(nodeAId,nodeBId)]
        
        raise DtaError("Network getLinkForNodeIdPair: none found for (%d,%d)" % (nodeAId,nodeBId))
    
    def addMovement(self, newMovement):
        """
        Adds the movement by adding it to the movement's incomingLink
        """
        newMovement.getIncomingLink().addOutgoingMovement(newMovement)
        
    def _switchConnectorNode(self, connector, switchStart, newNode):
        """
        Helper function for insertVirtualNodeBetweenCentroidsAndRoadNodes().
         * *switchStart* is a boolean
         * *newNode* is the new node to use
        """
        if switchStart:
            oldStartNode = connector.getStartNode()
            
            # the connector should go from the newNode
            connector.setStartNode(newNode)
                
            # fix _linksByNodeIdPair
            del self._linksByNodeIdPair[(oldStartNode.getId(), connector.getEndNode().getId())]
            self._linksByNodeIdPair[(newNode.getId(), connector.getEndNode().getId())] = connector
            
        else:
            oldEndNode = connector.getEndNode()
            
            # the connector should go from the newNode
            connector.setEndNode(newNode)
                
            # fix _linksByNodeIdPair
            del self._linksByNodeIdPair[(connector.getStartNode().getId(), oldEndNode.getId())]
            self._linksByNodeIdPair[(connector.getStartNode().getId(), newNode.getId())] = connector

    def insertVirtualNodeBetweenCentroidsAndRoadNodes(self):
        """
        In some situations (for example, for a Dynameq netork), there need to be intermediate nodes between
        :py:class:`Centroid` nodes and :py:class:`RoadNode` objects.
        
        .. image:: /images/addVirtualNode_before_after.png
           :height: 300px
           
        """
        
        allLinkNodeIDPairs = self._linksByNodeIdPair.keys()
        modifiedConnectorCount = 0
        
        for idPair in allLinkNodeIDPairs:
            # if we already took care of it when we did the reverse, it's not here anymore
            if idPair not in self._linksByNodeIdPair: continue
            
            connector = self._linksByNodeIdPair[idPair]
            
            # only look at connectors
            if not isinstance(connector, Connector): continue
            
            # if they connect a centroid directly to a road node
            startNode = connector.getStartNode()
            endNode   = connector.getEndNode()
            
            # Centroid => RoadNode
            if isinstance(startNode, Centroid) and connector.endIsRoadNode():
                DtaLogger.debug("Inserting virtualNode in Centroid(%6d) => RoadNode(%6d)" % (startNode.getId(), endNode.getId()))
                
                #TODO: option to start at arbitrary node id
                newNode = VirtualNode(id=self._maxNodeId+1,
                                      x=startNode.getX(),
                                      y=startNode.getY())
                self.addNode(newNode)
                
                # switch the node out
                self._switchConnectorNode(connector, switchStart=True, newNode=newNode)
                
                newConnector = None

                # add the virtualLink
                self.addLink(VirtualLink(id=self._maxLinkId + 1, startNode=startNode, endNode=newNode, label=None))
                # tally
                modifiedConnectorCount += 1
                
                # do it for the reverse
                if (endNode.getId(),startNode.getId()) in self._linksByNodeIdPair:
                    reverseConnector = self._linksByNodeIdPair[(endNode.getId(),startNode.getId())]
                    # switch the node out
                    self._switchConnectorNode(reverseConnector, switchStart=False, newNode=newNode)
                    # add the virtualLink
                    self.addLink(VirtualLink(id=self._maxLinkId + 1, startNode=newNode, endNode=startNode, label=None))
                    # tally
                    modifiedConnectorCount += 1
            
            # RoadNode => Centroid               
            elif connector.startIsRoadNode() and isinstance(endNode, Centroid):
                DtaLogger.debug("Inserting virtualNode in RoadNode(%6d) => Centroid(%6d)" % (startNode.getId(), endNode.getId()))
                
                newNode = VirtualNode(id=self._maxNodeId+1,
                                      x=endNode.getX(),
                                      y=endNode.getY())
                self.addNode(newNode)
                
                # switch the node out
                self._switchConnectorNode(connector, switchStart=False, newNode=newNode)
                # add the virtualLink
                self.addLink(VirtualLink(id=self._maxLinkId + 1, startNode=newNode, endNode=endNode, label=None))
                # tally
                modifiedConnectorCount += 1
                            
                # do it for the reverse
                if (endNode.getId(),startNode.getId()) in self._linksByNodeIdPair:
                    reverseConnector = self._linksByNodeIdPair[(endNode.getId(),startNode.getId())]
                    # switch the node out
                    self._switchConnectorNode(reverseConnector, switchStart=True, newNode=newNode)
                    # add the virtualLink
                    self.addLink(VirtualLink(id=self._maxLinkId + 1, startNode=endNode, endNode=newNode, label=None))
                    # tally
                    modifiedConnectorCount += 1
        
        DtaLogger.info("Network.insertVirtualNodeBetweenCentroidsAndRoadNodes() modified %d connectors" % modifiedConnectorCount)


    def iterNodes(self):
        """
        Return an iterator to the node collection
        """
        return self._nodes.itervalues()

    def iterLinks(self):
        """
        Return an iterator to the link collection
        """
        return self._linksById.itervalues()

    def hasNodeForId(self, nodeId):
        """
        Return True if there is a node with the given id
        """
        try:
            self.getNodeForId(nodeId)
            return True
        except DtaError:
            return False

    def hasLinkForId(self, linkId):
        """
        Return True if a link with the given id exists
        """
        try:
            self.getLinkForId(linkId)
            return True
        except DtaError:
            return False

    def hasLinkForNodeIdPair(self, startNodeId, endNodeId):
        """
        Return True if the network has a link with the given node ids 
        """
        try:
            self.getLinkForNodeIdPair(startNodeId, endNodeId)
            return True
        except DtaError:
            return False

    def removeLink(self, linkToRemove):
        """
        Remove the input link from the network
        """
        #remove all incoming and ougoing movements from the link 
        outMovsToRemove = [mov for mov in linkToRemove.iterOutgoingMovements()]
        inMovsToRemove = [mov for mov in linkToRemove.iterIncomingMovements()]
        
        for mov in outMovsToRemove:
            linkToRemove.removeOutgoingMovement(mov)

        for mov in inMovsToRemove:
            mov.getIncomingLink().removeOutgoingMovement(mov)

        #TODO: ugly code below 
        linkToRemove.getStartNode()._removeOutgoingLink(linkToRemove)
        linkToRemove.getEndNode()._removeIncomingLink(linkToRemove)

        del self._linksById[linkToRemove.id]
        del self._linksByNodeIdPair[linkToRemove.getStartNode().getId(),
                                linkToRemove.getEndNode().getId()]
        #TODO: do you want to update the maxIds?

    def removeNode(self, nodeToRemove):
        """
        Remove the input node from the network
        """
        iLinks = [link for link in nodeToRemove.iterIncomingLinks()]
        oLinks = [link for link in nodeToRemove.iterOutgoingLinks()]

        for link in iLinks:
            self.removeLink(link)

        for link in oLinks:
            self.removeLink(link)

        del self._nodes[nodeToRemove.getId()] 

        #TODO: do you want to update the maxIds? 

    def splitLink(self, linkToSplit):

        if isinstance(linkToSplit, VirtualLink):
            raise DtaError("Virtual link %s cannot be split" % linkToSplit.id)
        if isinstance(linkToSplit, Connector):
            raise DtaError("Connector %s cannot be split" % linkToSplit.id)

        midX = (linkToSplit.getStartNode().getX() + linkToSplit.getEndNode().getX()) / 2.0
        midY = (linkToSplit.getStartNode().getY() + linkToSplit.getEndNode().getY()) / 2.0

        midNode = RoadNode(self._maxNodeId + 1, midX, midY, 
                           RoadNode.GEOMETRY_TYPE_JUNCTION,
                           RoadNode.CONTROL_TYPE_UNSIGNALIZED,
                           RoadNode.PRIORITY_TEMPLATE_NONE)

        self.addNode(midNode)

        newLink1 = RoadLink(self._maxLinkId + 1,
                            linkToSplit.getStartNode(), 
                            midNode, 
                            None,
                            linkToSplit._facilityType,
                            linkToSplit._length / 2.0,
                            linkToSplit._freeflowSpeed,
                            linkToSplit._effectiveLengthFactor,
                            linkToSplit._responseTimeFactor,
                            linkToSplit._numLanes,
                            linkToSplit._roundAbout,
                            linkToSplit._level, 
                            ""
                            )

        self.addLink(newLink1)
 
        newLink2 = RoadLink(self._maxLinkId + 2,
                            midNode, 
                            linkToSplit.getEndNode(), 
                            None,
                            linkToSplit._facilityType,
                            linkToSplit._length / 2.0,
                            linkToSplit._freeflowSpeed,
                            linkToSplit._effectiveLengthFactor,
                            linkToSplit._responseTimeFactor,
                            linkToSplit._numLanes,
                            linkToSplit._roundAbout,
                            linkToSplit._level,
                            ""                            
                            )

        self.addLink(newLink2) 

        for inMov in linkToSplit.iterIncomingMovements():
            
            newMovement = Movement(linkToSplit.getStartNode(),
                                   inMov.getIncomingLink(),
                                   newLink1,
                                   inMov._freeflowSpeed,
                                   inMov._permission,
                                   inMov._numLanes,
                                   inMov._incomingLane,
                                   inMov._outgoingLane,
                                   inMov._followupTime)
        
       
            inMov.getIncomingLink().addOutgoingMovement(newMovement)


        for outMov in linkToSplit.iterOutgoingMovements():
            
            newMovement = Movement(linkToSplit.getEndNode(),
                                   newLink2,
                                   outMov.getOutgoingLink(),
                                   outMov._freeflowSpeed,
                                   outMov._permission,
                                   outMov._numLanes,
                                   outMov._incomingLane,
                                   outMov._outgoingLane,
                                   outMov._followupTime)

            newLink2.addOutgoingMovement(newMovement)

        #TODO: you have to update the vehClassGroup with defaults
        newMovement = Movement(midNode, 
                               newLink1,
                               newLink2,                               
                               newLink1._freeflowSpeed,
                               VehicleClassGroup("All", "*", "#ffff00"), 
                               newLink1._numLanes,
                               0,
                               newLink1._numLanes,
                               1.0
                               )                              
        newLink1.addOutgoingMovement(newMovement)
        self.removeLink(linkToSplit)
        
        return midNode 

    def getNumConnectors(self):
        """
        Return the number of connectors in the Network
        """
        return sum([1 for link in self.iterLinks() if link.isConnector()])

    def getNumRoadLinks(self):
        """
        Return the number of RoadLinks in the Network(excluding connectors)
        """
        return sum([1 for link in self.iterLinks() if link.isRoadLink()])
        
    def getScenario(self):
        """
        Return the scenario object associated with this network
        """
        return self._scenario 
        
