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
import copy
import random

import shapefile 

from .Centroid import Centroid
from .Connector import Connector
from .DtaError import DtaError
from .Link import Link
from .RoadLink import RoadLink
from .Logger import DtaLogger
from .RoadNode import RoadNode
from .TimePlan import PlanCollectionInfo
from .Scenario import Scenario
from .VirtualLink import VirtualLink
from .VirtualNode import VirtualNode
from .VehicleClassGroup import VehicleClassGroup
from .Movement import Movement
from .Algorithms import * 

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
        self._planInfo = {}
        
        self._nodeType = random.randint(0, 100000)
        self._linkType = random.randint(0, 100000)
        
    def __del__(self):
        pass
    
    def deepcopy(self, originNetwork):
        """
        Copies the contents of the originNetwork by creating copies of all its 
        constituent elements into self (Nodes and Links and Movements
        , not the scenario). If the originNetwork contains an element 
        with an already existing id this method will throw an exception. 
        """
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

    def addPlanCollectionInfo(self, militaryStartTime, militaryEndTime, name, description):
        """
        Add a time plan colection wth the given characteristics
        """
        if self.hasPlanCollectionInfo(militaryStartTime, militaryEndTime):
            raise DtaError("The network already has a plan collection info from %d to %d"
                           % (militaryStartTime, militaryEndTime))
        planInfo = PlanCollectionInfo(militaryStartTime, militaryEndTime, name, description)   
        self._planInfo[militaryStartTime, militaryEndTime] = planInfo
        return planInfo

    def hasPlanCollectionInfo(self, militaryStartTime, militaryEndTime):
        """
        Return True if the network has a time plan connection for the given
        start and end times
        """
        return True if (militaryStartTime, militaryEndTime) in self._planInfo else False

    def getPlanCollectionInfo(self, militaryStartTime, militaryEndTime):
        """
        Return the plan collection info for the given input times
        """
        if self.hasPlanCollectionInfo(militaryStartTime, militaryEndTime):
            return self._planInfo[militaryStartTime, militaryEndTime]
        else:
            raise DtaError("The network does not have a plan collection from %d to %d"
                           % (militaryStartTime, militaryEndTime))

    def iterPlanCollectionInfo(self):
        """
        Return an iterator to the planInfo objects
        """
        for sTime, eTime in sorted(self._planInfo.keys()):
            yield self.getPlanCollectionInfo(sTime, eTime)

        #return iter(sorted(self._planInfo.values(), key=lambda pi:pi._startTime))
                        
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

        if newLink.getId() in self._linksById:
            raise DtaError("Link with id %s already exists in the network" % newLink.getId())
        if (newLink.getStartNode().getId(), newLink.getEndNode().getId()) in self._linksByNodeIdPair:
            raise DtaError("Link for nodes (%d,%d) already exists in the network" % 
                           (newLink.getStartNode().getId(), newLink.getEndNode().getId()))
        
        self._linksById[newLink.getId()] = newLink
        self._linksByNodeIdPair[(newLink.getStartNode().getId(), newLink.getEndNode().getId())] = newLink
        
        if newLink.getId() > self._maxLinkId:
            self._maxLinkId = newLink.getId()
        
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

    def insertVirtualNodeBetweenCentroidsAndRoadNodes(self, startVirtualNodeId=None, startVirtualLinkId=None):
        """
        In some situations (for example, for a Dynameq netork), there need to be intermediate nodes between
        :py:class:`Centroid` nodes and :py:class:`RoadNode` objects.
        
        .. image:: /images/addVirtualNode_before_after.png
           :height: 300px

        If defined, the virtual nodes that will be added will begin from startVirtualNodeId and the 
        virtual links from startVirtualLinkId
           
        """
        
        allLinkNodeIDPairs = self._linksByNodeIdPair.keys()
        modifiedConnectorCount = 0

                #TODO: option to start at arbitrary node id
        if startVirtualNodeId:
            if startVirtualNodeId < self._maxNodeId:
                raise DtaError("The startVirtualNodeId %d cannot be less than equal to the current max node id %d" %
                               (startVirtualNodeId, self._maxNodeId))                                
            self._maxNodeId = startVirtualNodeId 
        if startVirtualLinkId:
            if startVirtualLinkId < self._maxLinkId:
                raise DtaError("The startVirtualLinkId %d cannot be less than equal to hte current max link id %d" %
                               (startVirtualLinkId, self._maxLinkId))
            self._maxLinkId = startVirtualLinkId 
        
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
                #DtaLogger.debug("Inserting virtualNode in Centroid(%6d) => RoadNode(%6d)" % (startNode.getId(), endNode.getId()))
                
                newNode = VirtualNode(id=self._maxNodeId + 1,
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
                #DtaLogger.debug("Inserting virtualNode in RoadNode(%6d) => Centroid(%6d)" % (startNode.getId(), endNode.getId()))
                
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

    def iterRoadNodes(self):
        """
        Return an iterator to the road node collection
        """
        for node in self.iterNodes():
            if node.isRoadNode():
                yield node

    def iterLinks(self):
        """
        Return an iterator to the link collection
        """
        return self._linksById.itervalues()

    def iterRoadLinks(self):
        """
        Return an iterator to all the RoadLinks in the network (that are not connectors)
        """
        for link in self.iterLinks():
            if link.isRoadLink():
                return link

    def iterConnectors(self):
        """
        Return an iterator to all the connectors in the network
        """
        for link in self.iterLinks():
            if link.isConnector():
                yield link 

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
        if not linkToRemove.isVirtualLink():
            outMovsToRemove = [mov for mov in linkToRemove.iterOutgoingMovements()]
            inMovsToRemove = [mov for mov in linkToRemove.iterIncomingMovements()]

            for mov in outMovsToRemove:
                linkToRemove.removeOutgoingMovement(mov)

            for mov in inMovsToRemove:
                mov.getIncomingLink().removeOutgoingMovement(mov)

        linkToRemove.getStartNode()._removeOutgoingLink(linkToRemove)
        linkToRemove.getEndNode()._removeIncomingLink(linkToRemove)

        del self._linksById[linkToRemove.getId()]
        del self._linksByNodeIdPair[linkToRemove.getStartNode().getId(),
                                linkToRemove.getEndNode().getId()]
        #TODO: do you want to update the maxIds?

    def removeNode(self, nodeToRemove):
        """
        Remove the input node from the network
        """
        if not self.hasNodeForId(nodeToRemove.getId()):
            raise DtaError("Network does not have node %d" % nodeToRemove.getId())
        
        linksToRemove = []
        for link in nodeToRemove.iterAdjacentLinks():
            linksToRemove.append(link)

        for link in linksToRemove:
            self.removeLink(link) 
        
        del self._nodes[nodeToRemove.getId()] 
        
        #TODO: do you want to update the maxIds? 

    def splitLink(self, linkToSplit, splitReverseLink=False):
        """
        Split the input link in half. The two new links have the 
        attributes of the input link. If there is a link in the 
        opposing direction then split that too. 
        """ 
        if isinstance(linkToSplit, VirtualLink):
            raise DtaError("Virtual link %s cannot be split" % linkToSplit.getId())
        if isinstance(linkToSplit, Connector):
            raise DtaError("Connector %s cannot be split" % linkToSplit.getId())

        midX = (linkToSplit.getStartNode().getX() + linkToSplit.getEndNode().getX()) / 2.0
        midY = (linkToSplit.getStartNode().getY() + linkToSplit.getEndNode().getY()) / 2.0

        midNode = RoadNode(self._maxNodeId + 1, midX, midY, 
                           RoadNode.GEOMETRY_TYPE_JUNCTION,
                           RoadNode.CONTROL_TYPE_UNSIGNALIZED,
                           RoadNode.PRIORITY_TEMPLATE_NONE)

        self.addNode(midNode)

        def _split(linkToSplit, midNode): 

            newLink1 = RoadLink(self._maxLinkId + 1,
                                linkToSplit.getStartNode(), 
                                midNode, 
                                None,
                                linkToSplit._facilityType,
                                linkToSplit.euclideanLength() / 2.0,
                                linkToSplit._freeflowSpeed,
                                linkToSplit._effectiveLengthFactor,
                                linkToSplit._responseTimeFactor,
                                linkToSplit._numLanes,
                                linkToSplit._roundAbout,
                                linkToSplit._level, 
                                linkToSplit.getLabel() 
                                )

            self.addLink(newLink1)

            newLink2 = RoadLink(self._maxLinkId + 1,
                                midNode, 
                                linkToSplit.getEndNode(), 
                                None,
                                linkToSplit._facilityType,
                                linkToSplit.euclideanLength() / 2.0,
                                linkToSplit._freeflowSpeed,
                                linkToSplit._effectiveLengthFactor,
                                linkToSplit._responseTimeFactor,
                                linkToSplit._numLanes,
                                linkToSplit._roundAbout,
                                linkToSplit._level,
                                linkToSplit.getLabel()
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

        _split(linkToSplit, midNode) 

        if splitReverseLink == True:
            if self.hasLinkForNodeIdPair(linkToSplit.getEndNode().getId(), linkToSplit.getStartNode().getId()):
                linkToSplit2 = self.getLinkForNodeIdPair(linkToSplit.getEndNode().getId(), linkToSplit.getStartNode().getId())
                _split(linkToSplit2, midNode)
                self.removeLink(linkToSplit2)

                link1 = self.getLinkForNodeIdPair(linkToSplit.getStartNode().getId(), 
                                                 midNode.getId())
                link2 = self.getLinkForNodeIdPair(midNode.getId(), linkToSplit.getStartNode().getId())
                prohibitedMovement = Movement.simpleMovementFactory(link1, link2,
                     self.getScenario().getVehicleClassGroup(VehicleClassGroup.PROHIBITED))
                link1.addOutgoingMovement(prohibitedMovement)

                link1 = self.getLinkForNodeIdPair(linkToSplit.getEndNode().getId(), 
                                                 midNode.getId())
                link2 = self.getLinkForNodeIdPair(midNode.getId(), linkToSplit.getEndNode().getId())
                prohibitedMovement = Movement.simpleMovementFactory(link1, link2,
                     self.getScenario().getVehicleClassGroup(VehicleClassGroup.PROHIBITED))

                link1.addOutgoingMovement(prohibitedMovement)

        self.removeLink(linkToSplit)
                      
        return midNode 

    def getNumVirtualLinks(self):
        """
        Return the number of connectors in the Network
        """
        return sum([1 for link in self.iterLinks() if link.isVirtualLink()])

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

    def getNumTimePlans(self):
        """
        Return the number of nodes with a time plan
        """
        num = 0
        for node in self.iterRoadNodes():
            if node.hasTimePlan():
                num += 1
        return num
               
    def getScenario(self):
        """
        Return the scenario object associated with this network
        """
        return self._scenario 

    def areIDsUnique(self, net2):
        """
        Returns True if the node and link Ids are unique 
        """
        areIDsUnique = True
        #RoadNodes 
        nodeIds1 = set([node.getId() for node in self.iterRoadNodes()])
        nodeIds2 = set([node.getId() for node in net2.iterRoadNodes()])
        commonNodeIds = ",".join(["%d" % node
                                for node in nodeIds1.intersection(nodeIds2)])
        if commonNodeIds != "":            
            DtaLogger.error("The two networks have the following road nodes with a common id: %s" % commonNodeIds)
            areIDsUnique = False            

        #Virtual nodes
        nodeIds1 = set([node.getId() for node in self.iterVirtualNodes()])
        nodeIds2 = set([node.getId() for node in net2.iterVirtualNodes()])
        commonNodeIds = ",".join(["%d" % node
                                for node in nodeIds1.intersection(nodeIds2)])
        if commonNodeIds != "":            
            DtaLogger.error("The two networks have the following virtual nodes with a common id: %s" % commonNodeIds)
            areIDsUnique = False 

        #centroids
        nodeIds1 = set([node.getId() for node in self.iterCentroids()])
        nodeIds2 = set([node.getId() for node in net2.iterCentroids()])
        commonNodeIds = ",".join(["%d" % node
                                for node in nodeIds1.intersection(nodeIds2)]) 
        if commonNodeIds != "":            
            DtaLogger.error("The two networks have the following virtual nodes with a common id: %s" % commonNodeIds)
            areIDsUnique = False 
        
        #RoadLinks
        linkIds1 = set([link.getId() for link in self.iterRoadLinks()])
        linkIds2 = set([link.getId() for link in net2.iterRoadLinks()])

        commonLinkIds = ",".join(["%d" % link for link in linkIds1.intersection(linkIds2)])
        if commonLinkIds != "":
            DtaLogger.error("The two networks have the following common roadlinks %s" % commonLinkIds)
            areIDsUnique = False                          

        #virtual links
        linkIds1 = set([link.getId() for link in self.iterRoadLinks()])
        linkIds2 = set([link.getId() for link in net2.iterRoadLinks()])

        commonLinkIds = ",".join(["%d" % link for link in linkIds1.intersection(linkIds2)])
        
        if commonLinkIds != "":
            DtaLogger.error("The two networks have the following common virtual links %s" % commonLinkIds)
            areIDsUnique = False                          

        #connectors 
        linkIds1 = set([link.getId() for link in self.iterConnectors()])
        linkIds2 = set([link.getId() for link in net2.iterConnectors()])

        commonLinkIds = ",".join(["%d" % link for link in linkIds1.intersection(linkIds2)])
        
        if commonLinkIds != "":
            DtaLogger.error("The two networks have the following common connectors %s" % commonLinkIds)
            areIDsUnique = False

        return areIDsUnique

    def mergeSecondaryNetworkBasedOnLinkIds(self, secondaryNetwork):
        """
        This method will add all the elements of the secondary
        network to the current one. The method will throw an
        exception if there is an element of the current and
        secondary network have a common id
        """ 

        if not self.areIDsUnique(secondaryNetwork):
            raise DtaError("The two networks cannot be merge because they "
                           "have conflicting node and/or link ids") 

        #copy the secondary network 
        for node in secondaryNetwork.iterNodes():            
            cNode = copy.copy(node) 
            cNode._incomingLinks = []
            cNode._outgoingLinks = []
            self.addNode(cNode)

        for link in secondaryNetwork.iterLinks():
            cLink = copy.copy(link)
            cLink._startNode = self.getNodeForId(link._startNode.getId())
            cLink._endNode = self.getNodeForId(link._endNode.getId())
            if link.isRoadLink() or link.isConnector():
                cLink._outgoingMovements = []
                cLink._incomingMovements = [] 
            self.addLink(cLink) 

        for link in secondaryNetwork.iterLinks():
            if link.isRoadLink() or link.isConnector():
                for mov in link.iterOutgoingMovements():
                    cLink = self.getLinkForId(link.getId())
                    cMov = copy.copy(mov)
                    cMov._node = self.getNodeForId(mov._node.getId())
                    try: 
                        cMov._incomingLink = self.getLinkForId(mov._incomingLink.getId())                    
                        cMov._outgoingLink = self.getLinkForId(mov._outgoingLink.getId())
                        cLink.addOutgoingMovement(cMov) 
                    except DtaError, e:
                        DtaLogger.error(str(e))



    
        
    def mergeSecondaryNetworkBasedOnLinkIds2(self, secondaryNetwork):
        """
        This method will create copies of all the elements of the 
        secondary network that do not exist in the current network 
        and add them to the current network. The method will merge the 
        networks using node and link ids. Elements of the secondary 
        network having an id that exists in this network will not be 
        coppied.
        """ 

        if not self._areIDsUnique(self, secondaryNetwork):
            raise DtaError("The two networks cannot be merge because they "
                           "have conflicting node and/or link ids") 
        

        primaryNodesToDelete = set()
        primaryLinksToDelete = set()

        for node in self.iterNodes():
            if node.isCentroid():
                if secondaryNetwork.hasNodeForId(node.getId()) and secondaryNetwork.getNodeForId(node.getId()).isRoadNode():
                    for vLink in node.iterAdjacentLinks():
                        primaryLinksToDelete.add(vLink)

                        try:
                            cLink = vLink.getAdjacentConnector()
                            linksToSkip.append(cLink) 
                        except DtaError, e:
                            DtaLogger.error(str(e))

                        primaryNodesToDelete.add(vLink.getOtherEnd(node))


        for link in primaryLinksToDelete:
            self.removeLink(link)
        for node in primaryNodesToDelete:
            self.remove(node)
            

        nodesToSkip = set()
        linksToSkip = set()
        
        #first find the common centroids and skip all the links associated with them
        for node in secondaryNetwork.iterNodes():

            if node.getId() == 286:
                pdb.set_trace() 

            if node.isCentroid():
                if self.hasNodeForId(node.getId()):
                    nodesToSkip.add(node.getId())
                    for vLink in node.iterAdjacentLinks():
                        linksToSkip.add(vLink.getId())                    
                        cLink = vLink.getAdjacentConnector()
                        linksToSkip.add(cLink) 
                    nodesToSkip.add(vLink.getOtherEnd(node).getId())                        
            else:
                if self.hasNodeForId(node.getId()):
                    nodesToSkip.add(node.getId())

                
        #links with common ids. 
        for link in secondaryNetwork.iterLinks():
            if self.hasLinkForId(link.getId()):
                linksToSkip.add(link.getId())
                if link.isVirtualLink(): print "skipping virtual link", link.getId()
            if link.getStartNode().getId() in nodesToSkip:
                linksToSkip.add(link.getId())
                if link.isVirtualLink(): print "skipping virtual link", link.getId()
            if link.getEndNode().getId() in nodesToSkip:
                linksToSkip.add(link.getId())
                if link.isVirtualLink(): print "skipping virual link", link.getId()
         
        #copy the secondary network 
        for node in secondaryNetwork.iterNodes():            
            if node.getId() in nodesToSkip:
                continue 
            cNode = copy.copy(node) 
            cNode._incomingLinks = []
            cNode._outgoingLinks = []
            self.addNode(cNode)

        for link in secondaryNetwork.iterLinks():
            if link.getId() in linksToSkip:
                continue 
            cLink = copy.copy(link)
            cLink._startNode = self.getNodeForId(link._startNode.getId())
            cLink._endNode = self.getNodeForId(link._endNode.getId())
            if isinstance(link, RoadLink):                
                cLink._outgoingMovements = []
                cLink._incomingMovements = [] 
            self.addLink(cLink) 

        for link in secondaryNetwork.iterLinks():
            if link.getId() in linksToSkip:
                continue
            if link.isRoadLink() or link.isConnector():
                for mov in link.iterOutgoingMovements():
                    cLink = self.getLinkForId(link.getId())
                    cMov = copy.copy(mov)
                    cMov._node = self.getNodeForId(mov._node.getId())

                    try: 
                        cMov._incomingLink = self.getLinkForId(mov._incomingLink.getId())                    
                        cMov._outgoingLink = self.getLinkForId(mov._outgoingLink.getId())
                        cLink.addOutgoingMovement(cMov) 
                    except DtaError, e:
                        DtaLogger.error(str(e))

    def getNumOverlappingConnectors(self):
        """
        Return the number of connectors that overlap with a RoadLink or 
        another connector
        """
        num = 0
        for node in self.iterNodes():
            if not node.isRoadNode():
                continue
            for con in node.iterAdjacentLinks():
                if not con.isConnector():
                    continue
                for link in node.iterAdjacentLinks():
                    if link == con:
                        continue
                    if con.isOverlapping(link):
                        num += 1
        return num

    def moveVirtualNodesToAvoidShortConnectors(self):
        """
        Connectors are sometimes too short. This method tries to move 
        the virtual node attached to the connector in the vicinity 
        of the current virtual node so that the connector length is 
        greater than Link.MIN_LENGTH_IN_MILES
        """
        MAX_DIST_TO_MOVE = 50
        for link in self.iterLinks():
            if not link.isConnector():
                continue
            if link.getEuclidianLengthInMiles() > Link.MIN_LENGTH_IN_MILES:
                continue
            virtualNode = link.getVirtualNode()
            numMoves = 0

            while link.getEuclidianLengthInMiles() < Link.MIN_LENGTH_IN_MILES \
                    and numMoves < 4:
                virtualNode._x += random.randint(0, MAX_DIST_TO_MOVE)
                virtualNode._y += random.randint(0, MAX_DIST_TO_MOVE)
                numMoves += 1

            DtaLogger.info("Moved virtual node  %8d associated with connector %8d to avoid overlappig links" % (virtualNode.getId(), link.getId()))
                                                
    def moveVirtualNodesToAvoidOverlappingLinks(self):
        """
        Virtual nodes are being moved + or minus 100 feet in either the X or the Y
        dimension to avoid overapping links
        """
        
        MAX_NUM_MOVES = 8
        MAX_DIST_TO_MOVE = 100
        
        for node in self.iterNodes():
            if not node.isRoadNode():
                continue
            numMoves = 0
            for con in node.iterAdjacentLinks():
                if not con.isConnector():
                    continue
                
                virtualNode = con.getOtherEnd(node)
                vNodeNeedsToMove = True 
                while vNodeNeedsToMove:
                    
                    for link in node.iterAdjacentLinks():
                        if link == con:
                            continue

                        if con.isOverlapping(link):
                            vNodeNeedsToMove = True
                            break 
                    else:
                        vNodeNeedsToMove = False
                    
                    if vNodeNeedsToMove:
                        virtualNode._x += random.randint(0, MAX_DIST_TO_MOVE)
                        virtualNode._y += random.randint(0, MAX_DIST_TO_MOVE)
                        numMoves += 1
                        if numMoves > MAX_NUM_MOVES:
                            vNodeNeedsToMove = False

    def writeNodesToShp(self, name):
        """
        Export all the nodes to a shapefile with the given name (without the shp extension)"
        """
        w = shapefile.Writer(shapefile.POINT)
        w.field("ID", "N", 10)
        w.field("IsRoad", "C", 10)
        w.field("IsCentroid", "C", 10)
        w.field("IsVNode", "C", 10) 

        for node in self.iterNodes():
            w.point(node.getX(), node.getY())
            w.record(node.getId(), str(node.isRoadNode()), str(node.isCentroid()), str(node.isVirtualNode()))

        w.save(name) 

    def writeLinksToShp(self, name):
        """
        Export all the links to a shapefile with the given name (without the shp extension)
        """
        w = shapefile.Writer(shapefile.POLYLINE) 
        w.field("ID", "N", 10)
        w.field("Start", "N", 10)
        w.field("End", "N", 10)

        w.field("IsRoad", "C", 10) 
        w.field("IsConn", "C", 10) 
        w.field("IsVirtual", "C", 10)
        w.field("Label", "C", 60)

        for link in self.iterLinks():
            if link.isVirtualLink():
                centerline = ((link._startNode.getX(), link._startNode.getY()),
                            (link._endNode.getX(), link._endNode.getY()))
                w.line(parts=[centerline])
            elif link.getNumShapePoints() == 0:                
                w.line(parts=[link.getCenterLine()])
            else:
                w.line(parts=[link._shapePoints])
            if link.isVirtualLink():
                label = ""
            else:
                label = link.getLabel()
            w.record(link.getId(), link.getStartNode().getId(), link.getEndNode().getId(),                     
                     str(link.isRoadLink()), str(link.isConnector()), str(link.isVirtualLink()), label)

        w.save(name)

    def writeMovementsToShp(self, name, planInfo=None):
        """
        Export all the movements to a shapefile with the given name
        """
        w = shapefile.Writer(shapefile.POLYLINE)
        w.field("Start", "N", 10)
        w.field("Middle", "N", 10)
        w.field("End", "N", 10)
        w.field("NumLanes", "N", 10)
        w.field("Capacity", "N", 10)
        w.field("TurnType", "C", 10)

        if not planInfo and self._planInfo.values():
            planInfo = self._planInfo.values()[0]
            
        for link in self.iterLinks():
            if link.isVirtualLink():
                continue
            for mov in link.iterOutgoingMovements():
                w.line(parts=[mov.getCenterLine()])
                w.record(mov.getStartNodeId(), mov.getAtNode().getId(), mov.getEndNodeId(),
                         mov.getNumLanes(), mov.getProtectedCapacity(planInfo),
                         mov.getTurnType())
        w.save(name)
                
    def mergeLinks(self, link1, link2):
        """
        Merge the two input sequential links. If any of the characteristics of the 
        two links are different (except their length) the method will throw an 
        error
        """
        if link1.getEndNode() != link2.getStartNode():
            raise DtaError("Links %d and %d are not sequential and therefore cannot be merged" % (link1.getId(), link2.getId()))
        if not link1.isRoadLink() or not link2.isRoadLink():
            raise DtaError("Links %d and %d should both be road links" % (link1.getId(), link2.getId()))
        
        if not link1.getEndNode().isShapePoint():
            raise DtaError("Links %d and %d cannot be merged because node %d is not "
                           "a shape point" % (link1.getId(), link2.getId(), link1.getEndNode().getId()))

        if not link1.hasSameAttributes(link2):
            raise DtaError("Links %d and %d cannot be merged because they have different attributes"
                            % (link1.getId(), link2.getId()))
            
        if link1._facilityType != link2._facilityType:
            raise DtaError("Links %d and %d cannot be merged because the have different facility types"
                           % (link1.getId(), link2.getId()))
            
        if link1._freeflowSpeed != link2._freeflowSpeed:
            raise DtaError("Links %d and %d cannot be merged because the have different free flow speeds"
                           % (link1.getId(), link2.getId()))            
        
        if link1._effectiveLengthFactor != link2._effectiveLengthFactor:
            raise DtaError("Links %d and %d cannot be merged because the have different effective "
                           "lenth factors" % (link1.getId(), link2.getId()))
                           
        
        if link1._responseTimeFactor != link2._responseTimeFactor:
            raise DtaError("Links %d and %d cannot be merged because the have different response "
                           "time factors" % (link1.getId(), link2.getId()))            
        
        if link1._numLanes != link2._numLanes:
            raise DtaError("Links %d and %d cannot be merged because the have different number "
                           "of lanes" % (link1.getId(), link2.getId()))                        

        if link1._roundAbout != link2._roundAbout:
            raise DtaError("Links %d and %d cannot be merged because the have different round about "
                           "classification" % (link1.getId(), link2.getId()))                                    

        if link1._level != link2._level:
            raise DtaError("Links %d and %d cannot be merged because they belong to different levels "
                           % (link1.getId(), link2.getId())) 

        label = ""
        if link1._label:
            label = link1._label 
        elif link2._label:
            label = link2._label

        newLink = RoadLink(self._maxLinkId + 1,
                           link1.getStartNode(), 
                           link2.getEndNode(), 
                            None,
                            link1._facilityType,
                            link1.getLength() + link2.getLength(), 
                            link1._freeflowSpeed,
                            link1._effectiveLengthFactor,
                            link1._responseTimeFactor,
                            link1._numLanes,
                            link1._roundAbout,
                            link1._level, 
                            label
                            )
        
        self.addLink(newLink)

        
        for inMov in link1.iterIncomingMovements():
                
            newMovement = Movement(link1.getStartNode(),
                                   inMov.getIncomingLink(),
                                   newLink,
                                   inMov._freeflowSpeed,
                                   inMov._permission,
                                   inMov._numLanes,
                                   inMov._incomingLane,
                                   inMov._outgoingLane,
                                   inMov._followupTime)


            inMov.getIncomingLink().addOutgoingMovement(newMovement)

        for outMov in link2.iterOutgoingMovements():

            newMovement = Movement(link2.getEndNode(),
                                   newLink,
                                   outMov.getOutgoingLink(),
                                   outMov._freeflowSpeed,
                                   outMov._permission,
                                   outMov._numLanes,
                                   outMov._incomingLane,
                                   outMov._outgoingLane,
                                   outMov._followupTime)

            newLink.addOutgoingMovement(newMovement)

        
        self.removeLink(link1)
        self.removeLink(link2)
        if link1.getEndNode().getCardinality() == (0,0):
            self.removeNode(link1.getEndNode()) 
                
    def removeShapePoints(self):
        """
        Remove shape points from the network 
        """
        for node in [node for node in self.iterRoadNodes()]:
            if node.isShapePoint():
                if node.getCardinality() == (2,2):

                    pair1 = None
                    pair2 = None
                    linki1 = node._incomingLinks[0]
                    linki2 = node._incomingLinks[1]
                    linko1 = node._outgoingLinks[0]
                    linko2 = node._outgoingLinks[1] 

                    if abs(linki1.getReferenceAngleInDegrees() - linko1.getReferenceAngleInDegrees()) < 10:
                           pair1 = (linki1, linko1)
                           if abs(linki2.getReferenceAngleInDegrees() - linko2.getReferenceAngleInDegrees()) < 10:
                               pair2 = (linki2, linko2)
                               
                    elif abs(linki1.getReferenceAngleInDegrees() - linko2.getReferenceAngleInDegrees()) < 10:
                           pair1 = (linki1, linko2)
                           if abs(linki2.getReferenceAngleInDegrees() - linko1.getReferenceAngleInDegrees()) < 10:
                               pair2 = (linki2, linko1)                    
                    else:
                        continue 
                    if pair1 and pair1[0].hasSameAttributes(pair1[1]):                        
                        self.mergeLinks(*pair1) 
                        DtaLogger.info("Merged links  %8d and %8d" % (pair1[0].getId(), pair1[1].getId()))
                    if pair2 and pair2[0].hasSameAttributes(pair2[1]):
                        self.mergeLinks(*pair2) 
                        DtaLogger.info("Merged links  %8d and %8d" % (pair2[0].getId(), pair2[1].getId()))
                                                        
                elif node.getCardinality() == (1,1):                    
                        
                    link1 = node._incomingLinks[0]
                    link2 = node._outgoingLinks[0]
                    if abs(link1.getReferenceAngleInDegrees() - link2.getReferenceAngleInDegrees()) < 10:
                        if link1.hasSameAttributes(link2):
                            self.mergeLinks(link1, link2) 
                            DtaLogger.info("Merged links  %8d and %8d" % (link1.getId(), link2.getId()))

    def renameLink(self, oldLinkId, newLinkId):
        """
        Give the newLinkId to the link with oldLinkId
        """
        if self.hasLinkForId(newLinkId):
            raise DtaError("A link with id %d already exists in the network" % newLinkId)
        
        linkToRename = self.getLinkForId(oldLinkId)

        linkToRename._id = newLinkId 
        del self._linksById[oldLinkId]
        self._linksById[newLinkId] = linkToRename 

        if newLinkId > self._maxLinkId:
            self._maxLinkId = newLinkId 

    def renameNode(self, oldNodeId, newNodeId):
        """
        Give the node with oldNodeId the new id 
        """
        if self.hasNodeForId(newNodeId):
            raise DtaError("A node with id %d already exists in the network" % newNodeId) 
        
        nodeToRename = self.getNodeForId(oldNodeId)
        if nodeToRename.isCentroid():
            raise DtaError("I cannot rename centroid %d" % newNodeId) 

        nodeToRename._id = newNodeId 

        if self._maxNodeId < newNodeId:
            self._maxNodeId = newNodeId 

        del self._nodes[oldNodeId] 

        self._nodes[newNodeId] = nodeToRename 

        for oLink in nodeToRename.iterOutgoingLinks():
            del self._linksByNodeIdPair[oldNodeId, oLink.getEndNode().getId()]
            self._linksByNodeIdPair[(oLink.getStartNode().getId(), oLink.getEndNode().getId())] = oLink

        for iLink in nodeToRename.iterIncomingLinks():
            del self._linksByNodeIdPair[iLink.getStartNode().getId(), oldNodeId]
            self._linksByNodeIdPair[(iLink.getStartNode().getId(), iLink.getEndNode().getId())] = iLink


    def getMaxLinkId(self):
        """
        Return the max link Id in the network
        """
        return self._maxLinkId

    def getMaxNodeId(self):
        """
        REturn the max noe id in the network
        """
        return self._maxNodeId

    def mergeSecondaryNetwork(self, secondaryNetwork):
        """
        This method will create a polygon around the current 
        (primary network). Every node or link of the secondary network 
        that is not in the polygon will be copied. 
        """ 
        print "\n\n*********************\nStarting network merge" 
        #primaryPolygon = getConvexHull([(node.getX(), node.getY()) for node in self.iterNodes()])
        primaryPolygon = getConvexHull([link.getMidPoint() for link in self.iterLinks() if not link.isVirtualLink()])        

        exitConnectors = []
        entryConnectors = []
        #the follwoing code will identify external links. Some of those links will be connectors
        # in the primary network and some of them may be roadway links. You do not need to add 
        # roadway links
        for sLink in secondaryNetwork.iterLinks():
            if not sLink.isRoadLink():
                continue
            point1 = (sLink.getStartNode().getX(), sLink.getStartNode().getY())
            point2 = (sLink.getEndNode().getX(), sLink.getEndNode().getY())
            if isPointInPolygon(point1, primaryPolygon) and not isPointInPolygon(point2, primaryPolygon):
                exitConnectors.append(sLink)
            if not isPointInPolygon(point1, primaryPolygon) and isPointInPolygon(point2, primaryPolygon):
                entryConnectors.append(sLink)

        print "\nEntryConnectors", [(link.getStartNodeId(), link.getEndNodeId()) for link in entryConnectors]
        print "\nExit connectors", [(link.getStartNodeId(), link.getEndNodeId()) for link in exitConnectors]



        #delete all the centroids in the primary polygon
        sNodesToDelete = []
        numCentroidsToDelete = 0
        for sCentroid in secondaryNetwork.iterCentroids():
            point = (sCentroid.getX(), sCentroid.getY())
            
            if isPointInPolygon(point, primaryPolygon):
                sNodesToDelete.append(sCentroid)
                numCentroidsToDelete += 1
                for vNode in sCentroid.iterAdjacentNodes():
                    sNodesToDelete.append(vNode)

        for sNode in sNodesToDelete:
            secondaryNetwork.removeNode(sNode)
            
        DtaLogger.info("Deleted %d centroids from the secondary network" % numCentroidsToDelete)

        #delete all the nodes and their associated links in the primary region
        sNodesToDelete = set()
        for sRoadNode in secondaryNetwork.iterRoadNodes():
            point = (sRoadNode.getX(), sRoadNode.getY())
            if isPointInPolygon(point, primaryPolygon):
                sNodesToDelete.add(sRoadNode)

                #TODO: why do I need this/ 
                for link in sRoadNode.iterAdjacentLinks():
                    if link.isConnector():
                        sNodesToDelete.add(link.getOtherEnd(sRoadNode))
        
        for sNode in sNodesToDelete:
            secondaryNetwork.removeNode(sNode)

        DtaLogger.info("Deleted %d roadNodes from the secondary network" % len(sNodesToDelete))            
        
        #rename all the nodes in the secondary network that conflict with primary nodes
        for sNode in secondaryNetwork.iterNodes():
            if self.hasNodeForId(sNode.getId()):
                secondaryNetwork.renameNode(sNode.getId(), max(secondaryNetwork.getMaxNodeId() + 1, self.getMaxNodeId() + 1))
                
        #rename all the links in the secondary network that conflict with primary links
        for sLink in secondaryNetwork.iterLinks():
            if self.hasLinkForId(sLink.getId()):
                secondaryNetwork.renameLink(sLink.getId(), max(secondaryNetwork.getMaxLinkId() + 1, self.getMaxLinkId() + 1))

        #identify external centroids
        externalCentroids = {}
        for centroid in self.iterCentroids():
            point = (centroid.getX(), centroid.getY())
            if not isPointInPolygon(point, primaryPolygon):
                externalCentroids[centroid.getId()] = centroid

        #delete externalCentroids
        for centroid in externalCentroids.itervalues():
            for vNode in centroid.iterAdjacentNodes():
                self.removeNode(vNode)
            self.removeNode(centroid)
        
        self.mergeSecondaryNetworkBasedOnLinkIds(secondaryNetwork)
    

        #add external links 
        for sLink in exitConnectors:            
            if not sLink.isRoadLink():
                continue


            pNode1, dist = getClosestNode(self, sLink.getStartNode())
            if dist > 10:
                continue 
            pNode2, dist = getClosestNode(self, sLink.getEndNode())
            if dist > 10:
                continue 
            print "Adding exit connector", pNode1.getId(), pNode2.getId() 

            pLink = copy.copy(sLink)

            if self.hasLinkForId(pLink.getId()):
                pLink._id = self.getMaxLinkId() + 1

            pLink._startNode = pNode1
            pLink._endNode = pNode2
        
            pLink._outgoingMovements = []
            pLink._incomingMovements = [] 
            
            if not self.hasLinkForNodeIdPair(pLink.getStartNodeId(), pLink.getEndNodeId()):
                self.addLink(pLink) 
                
        for sLink in entryConnectors:

            if not sLink.isRoadLink():
                continue
            
            pNode1, dist = getClosestNode(self, sLink.getStartNode())
            if dist > 50:
                continue 
            pNode2, dist = getClosestNode(self, sLink.getEndNode())
            if dist > 50:
                continue 
            
            print "Adding entry connector", pNode1.getId(), pNode2.getId() 

            pLink = copy.copy(sLink)
            pLink._startNode = pNode1
            pLink._endNode = pNode2

            if self.hasLinkForId(pLink.getId()):
                pLink._id = self.getMaxLinkId() + 1

            pLink._outgoingMovements = []
            pLink._incomingMovements = [] 

            if not self.hasLinkForNodeIdPair(pLink.getStartNodeId(), pLink.getEndNodeId()):                   
                self.addLink(pLink)

    def getNodeType(self):
        """
        Return a unique integer representing the node type
        """
        return self._nodeType

    def getLinkType(self):
        """
        Return a unique integer representing the link type
        """
        return self._linkType 
    

                
