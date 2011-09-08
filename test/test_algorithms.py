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

from dta.Scenario import Scenario
from dta.DynameqScenario import DynameqScenario 
from dta.Network import Network
from dta.DtaError import DtaError 
from dta.DynameqNetwork import DynameqNetwork 

from dta.Algorithms import dfs, hasPath 
from dta.Utils import getReverseNetwork

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


