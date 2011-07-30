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

import nose.tools

import datetime
from dta.Scenario import Scenario
from dta.Network import Network
from dta.Node import Node
from dta.RoadNode import RoadNode
from dta.RoadLink import RoadLink
from dta.Link import Link
from dta.Movement import Movement 
from dta.VehicleClassGroup import VehicleClassGroup
from dta.DtaError import DtaError 

def simpleRoadNodeFactory(id_, x, y):

    rn = RoadNode(id_,
                  x,
                  y,
                  Node.GEOMETRY_TYPE_INTERSECTION,
                  RoadNode.CONTROL_TYPE_UNSIGNALIZED, 
                  RoadNode.PRIORITY_TEMPLATE_NONE)

    return rn

def simpleRoadLinkFactory(id_, startNode, endNode):

    return RoadLink(id_, startNode, endNode,
                    None, 0, 100, 30, 1.0, 1.0, 3,
                    0, 0, "")

def simpleMovementFactory(incomingLink, outgoingLink):

    mov = Movement(incomingLink.getEndNode(),
                   incomingLink,
                   outgoingLink,
                   30,
                   VehicleClassGroup("all", "-", "#ffff00"))

    return mov                                                                                           
def getSimpleNet():


    sc = Scenario(datetime.time(0, 0, 0), datetime.time(1, 0, 0))
    net = Network(sc)
    
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


    def test_getNum(self):

        net = getSimpleNet() 
        assert net.getNumNodes() == 8
        assert net.getNumLinks() == 14

        assert net.getNumRoadNodes() == 8
        assert net.getNumCentroids() == 0
        assert net.getNumVirtualNodes() == 0

    def test_hasMethods(self):

        net = getSimpleNet()
        assert net.hasNodeForId(1)
        #assert not net.hasNodeForId("1")
        assert not net.hasNodeForId(-1)

        assert net.hasLinkForId(1)
        #assert not net.hasLinkForId("1")

        assert net.hasLinkForNodeIdPair(1, 5)
        assert not net.hasLinkForNodeIdPair(1, 4)

            

    def test_addMovements(self):

        net = getSimpleNet()
        mov = simpleMovementFactory(net.getLinkForNodeIdPair(1, 5),
                                       net.getLinkForNodeIdPair(5, 2))

        link_15 = net.getLinkForNodeIdPair(1, 5)
        link_51 = net.getLinkForNodeIdPair(5, 1)

        nose.tools.assert_raises(DtaError, link_51.addOutgoingMovement, "")

        #add the movement to a different link 
        nose.tools.assert_raises(DtaError, link_51.addOutgoingMovement, mov)

        
        link_15.addOutgoingMovement(mov)
        assert link_15.getNumOutgoingMovements() == 1

        #add the movement twice 
        nose.tools.assert_raises(DtaError, link_15.addOutgoingMovement, mov)

    def test_removeMovement(self):

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

    def test_node_has(self):

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
        

    def test_removeLink(self):

        net = getSimpleNet()
        link_15 = net.getLinkForNodeIdPair(1, 5)

        assert net.hasLinkForNodeIdPair(1, 5)
        assert net.getNumLinks() == 14        
        net.removeLink(link_15) 
    
        assert not net.hasLinkForNodeIdPair(1, 5) 
        assert net.getNumLinks() == 13
        
    def test_removeLink2(self):

        net = getSimpleNet()
        addAllMovements(net)

        link_15 = net.getLinkForNodeIdPair(1, 5)
        link_51 = net.getLinkForNodeIdPair(5, 1)
        link_52 = net.getLinkForNodeIdPair(5, 2)

        assert link_15.hasOutgoingMovement(2)
        assert link_15.hasOutgoingMovement(4)
        assert link_15.hasOutgoingMovement(3)

    def test_removeNode(self):

        net = getSimpleNet()
        addAllMovements(net)

        n = net.getNodeForId(5)
        net.removeNode(n)

        assert not net.hasNodeForId(5)
        assert net.getNumNodes() == 7
        assert not net.hasLinkForNodeIdPair(1, 5)
        assert not net.hasLinkForNodeIdPair(5, 2)
        



        

        


    
