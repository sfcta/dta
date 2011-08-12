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
import nose.tools

import os
import datetime
import math 
from itertools import izip 

from dta.Scenario import Scenario
from dta.DynameqScenario import DynameqScenario 
from dta.Network import Network
from dta.Node import Node
from dta.RoadNode import RoadNode
from dta.RoadLink import RoadLink, lineSegmentsCross
from dta.Link import Link
from dta.Movement import Movement 
from dta.VirtualNode import VirtualNode
from dta.Connector import Connector

from dta.VehicleClassGroup import VehicleClassGroup
from dta.DtaError import DtaError 
from dta.DynameqNetwork import DynameqNetwork
from dta.DynameqNetwork import *  


def getTestScenario():
 

    projectFolder = os.path.join(os.path.dirname(__file__), '..', 'testdata', 'dynameqNetwork_gearySubset')
    prefix = 'smallTestNet' 

    scenario = DynameqScenario(datetime.time(0,0,0), datetime.time(4,0,0))
    scenario.read(projectFolder, prefix) 

    return scenario 

def getTestNet():

    projectFolder = os.path.join(os.path.dirname(__file__), '..', 'testdata', 'dynameqNetwork_gearySubset')
    prefix = 'smallTestNet' 

    scenario = DynameqScenario(datetime.time(0,0,0), datetime.time(4,0,0))
    scenario.read(projectFolder, prefix) 
    net = DynameqNetwork(scenario) 
    net.read(projectFolder, prefix) 

    return net 


def simpleRoadNodeFactory(id_, x, y):

    rn = RoadNode(id_,
                  x,
                  y,
                  Node.GEOMETRY_TYPE_INTERSECTION,
                  RoadNode.CONTROL_TYPE_UNSIGNALIZED, 
                  RoadNode.PRIORITY_TEMPLATE_NONE)

    return rn

def simpleRoadLinkFactory(id_, startNode, endNode):

    length = math.sqrt((endNode.getX()  - startNode.getX()) ** 2 + (endNode.getY() - startNode.getY()) ** 2)

    return RoadLink(id_, startNode, endNode,
                    None, 0, length, 30, 1.0, 1.0, 3,
                    0, 0, "")

def simpleConnectorFactory(id_, startNode, endNode):

    length = math.sqrt((endNode.getX()  - startNode.getX()) ** 2 + (endNode.getY() - startNode.getY()) ** 2)
    return Connector(id_, startNode, endNode,
                    None, length, 30, 1.0, 1.0, 3,
                    0, 0, "")


def simpleMovementFactory(incomingLink, outgoingLink):

    mov = Movement(incomingLink.getEndNode(),
                   incomingLink,
                   outgoingLink,
                   30,
                   VehicleClassGroup("all", "-", "#ffff00"))

    return mov                                                                                           

def getSimpleNet():


    sc = DynameqScenario(datetime.time(0, 0, 0), datetime.time(1, 0, 0))
    net = DynameqNetwork(sc)
    
    v1 = simpleRoadNodeFactory(1, 0,   100)
    v2 = simpleRoadNodeFactory(2, 100, 200)
    v3 = simpleRoadNodeFactory(3, 100, 0)
    v4 = simpleRoadNodeFactory(4, 200, 100)
    v5 = simpleRoadNodeFactory(5, 100, 100)
    v6 = simpleRoadNodeFactory(6, 200, 200)
    v7 = simpleRoadNodeFactory(7, 300, 100)
    v8 = simpleRoadNodeFactory(8, 200, 0)

    net.addNode(v1)
    net.addNode(v2)
    net.addNode(v3)
    net.addNode(v4)
    net.addNode(v5)
    net.addNode(v6)
    net.addNode(v7)
    net.addNode(v8)


#
#                2         6
#                |         |
#                |         |
#      1 ------- 5 ------- 4 -------- 7
#                |         |
#                |         |
#                |         |
#                3         8
#


    e15 = simpleRoadLinkFactory(1, v1, v5)
    e51 = simpleRoadLinkFactory(2, v5, v1)
    e35 = simpleRoadLinkFactory(3, v3, v5)
    e53 = simpleRoadLinkFactory(4, v5, v3)
    e45 = simpleRoadLinkFactory(5, v4, v5)
    e54 = simpleRoadLinkFactory(6, v5, v4)
    e52 = simpleRoadLinkFactory(7, v5, v2)
    e25 = simpleRoadLinkFactory(8, v2, v5)

    e48 = simpleRoadLinkFactory(9, v4, v8)
    e84 = simpleRoadLinkFactory(10, v8, v4)
    e74 = simpleRoadLinkFactory(11, v7, v4)
    e47 = simpleRoadLinkFactory(12, v4, v7)
    e46 = simpleRoadLinkFactory(13, v4, v6)
    e64 = simpleRoadLinkFactory(14, v6, v4)

    links = [e15, e51, e35, e53, e45, e54, e52, e25, e48, e84, e74, e47, 
             e46, e64]

    net.addLink(e15)
    net.addLink(e51)
    net.addLink(e35)
    net.addLink(e53)
    net.addLink(e45)
    net.addLink(e54)
    net.addLink(e52)
    net.addLink(e25)
    net.addLink(e48)
    net.addLink(e84)
    net.addLink(e74)
    net.addLink(e47)
    net.addLink(e46)
    net.addLink(e64)

    return net

def addAllMovements(net):
    
    for node in net.iterNodes():
        for incomingLink in node.iterIncomingLinks():
            for outgoingLink in node.iterOutgoingLinks():
                    mov = simpleMovementFactory(incomingLink, outgoingLink)
                    incomingLink.addOutgoingMovement(mov) 

class TestNetwork(object):


    def test_1getNum(self):

        net = getSimpleNet() 
        assert net.getNumNodes() == 8
        assert net.getNumLinks() == 14

        assert net.getNumRoadNodes() == 8
        assert net.getNumCentroids() == 0
        assert net.getNumVirtualNodes() == 0

    def test_2hasMethods(self):

        net = getSimpleNet()
        assert net.hasNodeForId(1)
        #assert not net.hasNodeForId("1")
        assert not net.hasNodeForId(-1)

        assert net.hasLinkForId(1)
        #assert not net.hasLinkForId("1")

        assert net.hasLinkForNodeIdPair(1, 5)
        assert not net.hasLinkForNodeIdPair(1, 4)

            

    def test_3addMovements(self):

        net = getSimpleNet()
        mov = simpleMovementFactory(net.getLinkForNodeIdPair(1, 5),
                                       net.getLinkForNodeIdPair(5, 2))

        link_15 = net.getLinkForNodeIdPair(1, 5)
        link_51 = net.getLinkForNodeIdPair(5, 1)

        #nose.tools.assert_raises(DtaError, link_51.addOutgoingMovement, "")


        #add the movement to a different link 
        #nose.tools.assert_raises(DtaError, link_51.addOutgoingMovement, mov)

        

        
        link_15.addOutgoingMovement(mov)
        assert link_15.getNumOutgoingMovements() == 1

        #add the movement twice 
        nose.tools.assert_raises(DtaError, link_15.addOutgoingMovement, mov)

    def test_4removeMovement(self):

        net = getSimpleNet()
        mov = simpleMovementFactory(net.getLinkForNodeIdPair(1, 5),
                                       net.getLinkForNodeIdPair(5, 2))

        link_15 = net.getLinkForNodeIdPair(1, 5)
        link_51 = net.getLinkForNodeIdPair(5, 1)
        link_52 = net.getLinkForNodeIdPair(5, 2)

        link_15.addOutgoingMovement(mov)
        assert link_15.getNumOutgoingMovements() == 1

        assert link_52.getNumIncomingMovements() == 1

        nose.tools.assert_raises(DtaError, link_51.removeOutgoingMovement, mov)
        
        link_15.removeOutgoingMovement(mov)
        assert link_15.getNumOutgoingMovements() == 0
        assert link_52.getNumIncomingMovements() == 0

    def test_5node_has(self):

        net = getSimpleNet()
        #link_15 = net.getLinkForNodeIdPair(1, 5)

        n = net.getNodeForId(5)
        assert n.hasIncomingLinkForNodeId(1)
        assert n.hasIncomingLinkForNodeId(4)
        assert n.hasIncomingLinkForNodeId(3)
        assert not n.hasIncomingLinkForNodeId(5)

        assert n.hasOutgoingLinkForNodeId(1)
        assert n.hasOutgoingLinkForNodeId(4)
        assert n.hasOutgoingLinkForNodeId(3)
        assert not n.hasOutgoingLinkForNodeId(18)
        

    def test_6removeLink(self):

        net = getSimpleNet()
        link_15 = net.getLinkForNodeIdPair(1, 5)

        assert net.hasLinkForNodeIdPair(1, 5)
        assert net.getNumLinks() == 14        
        net.removeLink(link_15) 
    
        assert not net.hasLinkForNodeIdPair(1, 5) 
        assert net.getNumLinks() == 13
        
    def test_7removeLink2(self):

        net = getSimpleNet()
        addAllMovements(net)

        link_15 = net.getLinkForNodeIdPair(1, 5)
        link_51 = net.getLinkForNodeIdPair(5, 1)
        link_52 = net.getLinkForNodeIdPair(5, 2)

        assert link_15.hasOutgoingMovement(2)
        assert link_15.hasOutgoingMovement(4)
        assert link_15.hasOutgoingMovement(3)

    def test_removeConnector(self):

        net = getSimpleNet()
        
        vn = VirtualNode(9, 0, 200) 
        n5 = net.getNodeForId(5) 

        net.addNode(vn) 
        con = simpleConnectorFactory(15, vn, n5)
        con2 = simpleConnectorFactory(16, n5, vn) 

        net.addLink(con)
        net.addLink(con2)
        assert net.getNumLinks() == 16

        assert n5.getNumAdjacentLinks() == 10 
        assert n5.getNumAdjacentNodes() == 5

        net.removeLink(con) 
        assert net.getNumLinks() == 15
        net.removeLink(con2)
        assert net.getNumLinks() == 14

        assert n5.getNumAdjacentLinks() == 8 
        assert n5.getNumAdjacentNodes() == 4

    def test_8removeNode(self):

        net = getSimpleNet()
        addAllMovements(net)

        n = net.getNodeForId(5)
        net.removeNode(n)

        assert not net.hasNodeForId(5)
        assert net.getNumNodes() == 7
        assert not net.hasLinkForNodeIdPair(1, 5)
        assert not net.hasLinkForNodeIdPair(5, 2)
        
    def test_9splitLink(self):

        net = getSimpleNet()
        addAllMovements(net)

        l = net.getLinkForNodeIdPair(1, 5)

        assert net.getNumNodes() == 8 
        assert net.getNumLinks() == 14

        net.splitLink(l) 

        assert net.getNumNodes() == 9
        assert net.getNumLinks() == 15

        link1 = net.getLinkForNodeIdPair(1, 9) 
        link2 = net.getLinkForNodeIdPair(9, 5) 

        link1.getNumOutgoingMovements() == 1

        assert link1.hasOutgoingMovement(5)
        assert link2.hasOutgoingMovement(2) 
        assert link2.hasOutgoingMovement(4)
        assert link2.hasOutgoingMovement(3)

    
    def test_10link_getCenterline(self):

        net = getSimpleNet()

        link = net.getLinkForNodeIdPair(1, 5) 

        assert link.getCenterLine() == ((0.0, 82.0), (100.0, 82.0))

        link = net.getLinkForNodeIdPair(3, 5) 
        
        assert link.getCenterLine() == ((118.0, 0.0), (118.0, 100.0))


    def test_11link_lineSegmentsIntersect(self):


        net = getSimpleNet() 

        link51 = net.getLinkForNodeIdPair(5, 1) 
        p1, p2 = link51.getCenterLine() 

        link25 = net.getLinkForNodeIdPair(2, 5) 
        p3, p4 = link25.getCenterLine() 

        assert lineSegmentsCross(p1, p2, p3, p4)

        link15 = net.getLinkForNodeIdPair(1, 5) 
        p5, p6 = link15.getCenterLine()

        assert not lineSegmentsCross(p5, p6, p3, p4)
        assert not lineSegmentsCross(p3, p4, p5, p6)

        p7 = (50, 0)
        p8 = (50, 100 - 18) 
    
        assert not lineSegmentsCross(p7, p8, p5, p6)

        p9 = (50, 0)
        p10 = (50, 100 - 17) 

        assert lineSegmentsCross(p9, p10, p5, p6)

    def test_12getNumAdjacentNodesAndLinks(self):

        net = getSimpleNet() 

        n5 = net.getNodeForId(5) 

        assert n5.getNumAdjacentLinks() == 8
        assert n5.getNumAdjacentNodes() == 4

        n1 = net.getNodeForId(1) 

        link51 = net.getLinkForNodeIdPair(5, 1) 

        assert not link51.hasOutgoingMovement(5) 

        assert n1.getNumAdjacentLinks() == 2
        assert n1.getNumAdjacentNodes() == 1

    def test_13IsShapePoint(self):

        net = getSimpleNet() 

        n5 = net.getNodeForId(5) 
        n1 = net.getNodeForId(1) 
        assert not n5.isShapePoint() 
        assert not n1.isShapePoint()

        link15 = net.getLinkForNodeIdPair(1, 5) 

        midNode = net.splitLink(link15) 

        assert midNode.isShapePoint()

    def test_hasConnector(self):

        net = getSimpleNet()

        n5 = net.getNodeForId(5) 

        assert not hasConnector(n5)
        
        vn = VirtualNode(9, 0, 200) 

        net.addNode(vn) 
        assert isinstance(n5, RoadNode) 
        assert isinstance(vn, VirtualNode)
        con = simpleConnectorFactory(15, vn, n5)

        net.addLink(con)
        assert net.getNumLinks() == 15 

        assert hasConnector(n5)

    def test_getCandidateLinks(self):

        net = getSimpleNet()
        n5 = net.getNodeForId(5) 

        assert not hasConnector(n5)
        
        vn = VirtualNode(9, 0, 200) 

        net.addNode(vn) 
        con = simpleConnectorFactory(15, vn, n5)
        con2 = simpleConnectorFactory(16, n5, vn) 

        net.addLink(con)
        net.addLink(con2)
        assert net.getNumLinks() == 16

        assert hasConnector(n5)

        clinks = getCandidateLinks(n5, con) 
        assert len(clinks) == 2
        assert 2 in [link.getId() for link in clinks]
        assert 8 in [link.getId() for link in clinks]

        clinks = getCandidateLinks(n5, con2) 
        assert len(clinks) == 2
        assert 2 in [link.getId() for link in clinks]
        assert 8 in [link.getId() for link in clinks]

    def test_removeConnectorFromIntersection(self):
        
        net = getSimpleNet()
        n5 = net.getNodeForId(5) 

        assert not hasConnector(n5)
        
        vn = VirtualNode(9, 0, 200) 

        net.addNode(vn) 
        con = simpleConnectorFactory(15, vn, n5)
        con2 = simpleConnectorFactory(16, n5, vn) 

        net.addLink(con)
        net.addLink(con2)
        assert net.getNumLinks() == 16
        assert hasConnector(n5)
        #this is the connector to be removed 
        assert net.hasLinkForNodeIdPair(9, 5) 
        assert net.hasLinkForNodeIdPair(5, 9)
        assert net.hasLinkForId(15) 
        assert net.hasLinkForId(16)

        newConnector = net.removeCentroidConnectorFromIntersection(n5, con) 
        #the old connector is no longer there 
        assert not net.hasLinkForNodeIdPair(9, 5) 
        #but a connector with the same id is attached to newly created midblock 
        assert net.hasLinkForId(15) 
        assert net.getNumLinks() == 17  #one more link than before
        assert net.getNumNodes() == 10  #one more node than before 

        assert hasConnector(n5)         #there is still one connector at intersection 5 
        newConnector.getRoadNode().getX(), newConnector.getRoadNode().getY()
        assert newConnector.getRoadNode().isShapePoint(countRoadNodesOnly=True) 

        newConnector2 = net.removeCentroidConnectorFromIntersection(n5, con2)
        #the old connector is no longer there
        assert not net.hasLinkForNodeIdPair(5, 9)
        #a new connector is there with the same id 
        assert net.hasLinkForId(16)
        assert net.getNumLinks() == 17  #same links as before the algorithm picked the newly created block 
        assert net.getNumNodes() == 10  #same nodes as before. No new link was split
        
    def test_removeAllCentroidConnectorsFromIntersections(self):
        
        net = getSimpleNet()
        n5 = net.getNodeForId(5) 

        assert not hasConnector(n5)
        
        vn = VirtualNode(9, 0, 200) 

        net.addNode(vn) 
        con = simpleConnectorFactory(15, vn, n5)
        con2 = simpleConnectorFactory(16, n5, vn) 

        net.addLink(con)
        net.addLink(con2)
        assert net.getNumLinks() == 16
        assert hasConnector(n5)
        #this is the connector to be removed 
        assert net.hasLinkForNodeIdPair(9, 5) 
        assert net.hasLinkForNodeIdPair(5, 9)
        assert net.hasLinkForId(15) 
        assert net.hasLinkForId(16)

        assert net.getNumConnectors() == 2 

        net.removeCentroidConnectorsFromIntersections() 
        
        #the connectors have been removed from the intersection 
        assert not net.hasLinkForNodeIdPair(9, 5) 
        assert not net.hasLinkForNodeIdPair(5, 9)
        assert net.getNumConnectors() == 2 

        assert net.hasLinkForId(15) 
        assert net.hasLinkForId(16)

        assert net.getNumLinks() == 17 
        assert net.getNumNodes() == 10  

        assert not hasConnector(n5)         #there is no connector at intersection 5


    def test_aaa(self):

        
        net = getSimpleNet()
        n5 = net.getNodeForId(5) 

        assert not hasConnector(n5)
        
        centroid = Centroid(9, 0, 200) 
        net.addNode(centroid) 
        


        #net.addNode(vn) 
        con = simpleConnectorFactory(15, centroid, n5)
        con2 = simpleConnectorFactory(16, n5, centroid) 

        net.addLink(con)
        net.addLink(con2)
    
        #net.removeCentroidConnectorsFromIntersections() 
        
        print "****" , net.getNumLinks() 
        net.insertVirtualNodeBetweenCentroidsAndRoadNodes()
        net.write("test", "test") 
        print "****" , net.getNumLinks()         

        scenario = getTestScenario() 
        
        net = DynameqNetwork(scenario) 
        net.read("test", "test") 


    def test_readScenario(self):

        net = getTestNet()
        projectFolder = os.path.join(os.path.dirname(__file__), '..', 'testdata', 'dynameqNetwork_gearySubset')

        prefix = 'smallTestNet' 
        sc = DynameqScenario(datetime.time(0,0,0), datetime.time(4,0,0))
        sc.read(projectFolder, prefix) 

        
        assert 'All' in sc.vehicleClassGroups.keys() 
        assert 'Transit' in sc.vehicleClassGroups.keys() 
        assert 'Prohibited' in sc.vehicleClassGroups.keys() 

    def test_writeScenario(self):

        net = getTestNet() 
        sc = net.getScenario() 

        sc.write(os.path.join(os.path.dirname(__file__), '..', 'testdata', 'dynameqNetwork_gearySubset_copy'), 'smallTestNet')

    def test_readDynameqNetwork(self):

        net = getTestNet()

        assert net.getNumNodes() == 299 
        assert  net.getNumLinks() == 560

    def test_writeDynameqNetwork(self): 

        net = getTestNet()

        net.write(os.path.join(os.path.dirname(__file__), '..', 'testdata', 'dynameqNetwork_gearySubset_copy'), 'smallTestNet')

              
    def test_mycopy(self):

        net1 = getSimpleNet() 
        addAllMovements(net1)

        link1_15 = net1.getLinkForNodeIdPair(1, 5) 
        link1_15._label = "123" 
        
        sc = net1.getScenario() 
        net2 = DynameqNetwork(sc) 
        net2.copy(net1)
        
        link2_15 = net2.getLinkForNodeIdPair(1, 5) 
        assert link2_15._label == "123"
        #now change the label of the first link 
        link1_15._label = "342"
        #make sure that the label of the copied link does not change 
        assert link2_15._label == "123"        
        #more rigorously 
        assert id(link1_15) != id(link2_15) 

        assert net1.getNumNodes() == net2.getNumNodes()
        assert net2.getNumLinks() == net2.getNumLinks() 

        #check that links from the second network contain references to nodes in the second network 
        for link2 in net2.iterLinks():
            assert id(link2._startNode) == id(net2.getNodeForId(link2._startNode._id))
            assert id(link2._endNode) == id(net2.getNodeForId(link2._endNode._id))

        node1_5 = net1.getNodeForId(5) 
        node2_5 = net2.getNodeForId(5) 

        assert node1_5.getNumIncomingLinks() == node2_5.getNumIncomingLinks() 

        for link1, link2 in izip (node1_5._incomingLinks, node2_5._incomingLinks):
            assert not id(link1) == id(link2) 
            assert id(link1) == id(net1.getLinkForId(link1.getId()))
            assert id(link2) == id(net2.getLinkForId(link2.getId()))

            assert link1.getNumIncomingMovements() == link2.getNumIncomingMovements() 
            assert link1.getNumOutgoingMovements() == link2.getNumOutgoingMovements() 

            for mov2 in link2.iterIncomingMovements():
                assert id(mov2._node) == id(net2.getNodeForId(mov2._node.getId()))
                assert id(mov2._incomingLink) == id(net2.getLinkForId(mov2._incomingLink.getId()))
                assert id(mov2._outgoingLink) == id(net2.getLinkForId(mov2._outgoingLink.getId()))

            for mov2 in link2.iterOutgoingMovements():
                assert id(mov2._node) == id(net2.getNodeForId(mov2._node.getId()))
                assert id(mov2._incomingLink) == id(net2.getLinkForId(mov2._incomingLink.getId()))
                assert id(mov2._outgoingLink) == id(net2.getLinkForId(mov2._outgoingLink.getId()))

                
    def test_readWrite(self):

        projectFolder = "/Users/michalis/Documents/workspace/dta/dev/test/"
        prefix = 'test' 

        scenario = DynameqScenario(datetime.time(0,0,0), datetime.time(4,0,0))
        scenario.read(projectFolder, prefix)

        net = DynameqNetwork(scenario) 
        net.read(projectFolder, prefix) 

        net.write("test", "crossHair")

        net.removeCentroidConnectorsFromIntersections() 

        net.write("test", "crossHair3") 
        

