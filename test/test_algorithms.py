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
import datetime
import nose 

from dta.Scenario import Scenario
from dta.DynameqScenario import DynameqScenario 
from dta.Network import Network
from dta.DtaError import DtaError 
from dta.DynameqNetwork import DynameqNetwork 

from dta.Algorithms import dfs, hasPath, getConvexHull, getConvexHull2, getTightHull, getConvexHull3
from dta.Utils import *

def getTestNet():

    projectFolder = os.path.join(os.path.dirname(__file__), '..', 'testdata', 'dynameqNetwork_gearySubset')
    prefix = 'smallTestNet' 

    scenario = DynameqScenario(datetime.datetime(2010,1,1,0,0,0), datetime.datetime(2010,1,1,4,0,0))
    scenario.read(projectFolder, prefix) 
    net = DynameqNetwork(scenario) 
    net.read(projectFolder, prefix) 

    return net 


class TestAlgorithms:

    def test_dfs(self):

        net = getTestNet()
        root = net.getNodeForId(9)

        dfs(net, root)

        assert root.pred == None

        assert hasPath(net, root, net.getNodeForId(26520))
        assert not hasPath(net, root, net.getNodeForId(66))


        #for node in sorted(net.iterNodes(), key=lambda n:n.getId()):
        #    print node.getId(), node.visited, node.pre, node.post

    def test_reverse(self):

        net = getTestNet()
        rNet = getReverseNetwork(net) 

        assert net.hasLinkForNodeIdPair(26497, 26503) 
        assert not net.hasLinkForNodeIdPair(26503, 26497)

        assert not rNet.hasLinkForNodeIdPair(26497, 26503) 
        assert rNet.hasLinkForNodeIdPair(26503, 26497)

        rNet.getNumNodes() == net.getNumNodes() 
        rNet.getNumLinks() == net.getNumLinks() 

    def test_lexicographicSort(self):

        elements = [[1,2], [3,4], [0, 3], [0,4], [1,7], [2,3], [2,1], [3,2]]

        def predicate(elem1, elem2):

            if elem1[0] == elem2[0]:                
                if elem1[1] < elem2[1]:
                    return -1 
                elif elem1[1] == elem2[1]:
                    return 0
                else:
                    return 1
            else:
                if elem1[0] < elem2[0]:
                    return -1
                else:
                    return 1

        answer = [[0, 3], [0, 4], [1, 2], [1, 7], [2, 1], [2, 3], [3, 2], [3, 4]]
        result = sorted(elements, cmp=predicate)
        assert result == answer 

    def test_getConvexHull(self):
        
        data = [[0,0], [5, -1], [0, 10], [5,10], [8,10], [10, 10], [3,10], 
                [3,3], [4,4], [5,5], [10, 0], [11,0]] 


        #writePoints(data, "test/covHullPoints") 
        result = getConvexHull(data)
        print 
        print result 
        #writePolygon(result, "test/conHull") 

        net = getTestNet() 

        points = [[n.getX(), n.getY()] for n in net.iterNodes()]
        #writePoints(points, "test/gearySubset")
                    
        hull = getConvexHull(points)
        #writePolygon(hull, "test/gearySubsetHull")

    def test_convexHull2(self):
        
        data = [[0,0], [5, -1], [0, 10], [5,10], [8,10], [10, 10], [3,10], 
                [3,3], [4,4], [5,5], [10, 0], [11,0]] 

        result = getConvexHull2(data)
        print 
        print result 

    def test_getTightHull(self):

        data = [[0,0], [5, -1], [0, 10], [5,10], [8,10], [10, 10], [3,10], 
                [3,3], [4,4], [5,5], [10, 0], [11,0]] 


        result = getTightHull(data, 2)

        print result 

    def test_getConvexHull3(self):
        
        data = [[0,0], [5, -1], [0, 10], [5,10], [8,10], [10, 10], [3,10], 
                [3,3], [4,4], [5,5], [10, 0], [11,0]] 

        hull = getConvexHull3(data, 2) 
        #writePolygon(hull, "test/gearySubsetHull3")
