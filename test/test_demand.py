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

import dta
import os
import pdb

import la
import nose.tools 
import numpy as np

import dta
from dta.Demand import Demand
from dta.Utils import Time
from dta.DynameqNetwork import DynameqNetwork 
from dta.DynameqScenario import DynameqScenario 
from dta.Utils import Time

dta.VehicleType.LENGTH_UNITS= "feet"
dta.Node.COORDINATE_UNITS   = "feet"
dta.RoadLink.LENGTH_UNITS   = "miles"


def getTestNet():

    projectFolder = os.path.join(os.path.dirname(__file__), '..', 'testdata', 'dynameqNetwork_gearySubset')
    prefix = 'smallTestNet' 

    scenario = DynameqScenario(Time(0,0), Time(12,0))
    scenario.read(projectFolder, prefix) 
    #nose.tools.set_trace()

    dta.VehicleType.LENGTH_UNITS= "feet"
    dta.Node.COORDINATE_UNITS   = "feet"
    dta.RoadLink.LENGTH_UNITS   = "miles"
    
    net = DynameqNetwork(scenario) 
    net.read(projectFolder, prefix) 
    return net 


class TestDemand:

    def test_1getTimePeriods(self):

        net = getTestNet()

        startTime = Time(8, 30)
        endTime = Time(9, 30)
        timeStep = Time(0, 15)
        demand = Demand(net, Demand.DEFAULT_VEHCLASS, startTime, endTime, timeStep)

        print [tp for tp in demand.iterTimePeriods()]
        


    def test_1read(self):
        
        fileName = os.path.join(os.path.dirname(__file__), '..', 'testdata', 
                                'dynameqNetwork_gearySubset', 'gearysubnet_matx.dqt')

        net = getTestNet() 

        demand = Demand.read(net, fileName)
        assert demand.getNumSlices() == 4

        assert demand.getValue(Time(0, 15), 56, 8) == 4000
        assert demand.getValue(Time(0, 45), 8, 2) == 34

        demand.setValue(Time(0, 45), 8, 2, 35)
        assert demand.getValue(Time(0, 45), 8, 2) == 35

        demand.setValue(Time(0, 15), 56, 8, 4001) 
        assert not demand.getValue(Time(0, 15), 56, 8) == 4000
        assert demand.getValue(Time(0, 15), 56, 8) == 4001

    def test_larry(self):
        
        x = np.array([[[1,2], [3,4]],[[1,2], [3,4]]])
        label = [['a', 'b'], ['c', 'd'], ['e', 'f']]
        m = la.larry(x, label, dtype=float)

        assert m.lix[['a'], ['d'], ['e']] == 3.0

        y = np.array([[[1,2], [3,4]],[[1,2], [3,4]]])
        label2 = [['a', 'b'], ['c', 'd'], ['e', 'f']]
        m2 = la.larry(y, label2, dtype=float)

        #nose.tools.set_trace()

        m1 = m.copyx()
        m2 = m2.copyx() 

        result = m1 == m2
    
        for elem in result.flat:
            assert elem 

    def test_write(self):
        """
        """

        fileName = os.path.join(os.path.dirname(__file__), '..', 'testdata', 
                                'dynameqNetwork_gearySubset', 'gearysubnet_matx.dqt')

        net = getTestNet() 
        demand = Demand.read(net, fileName)

        # TODO: this requires subdir test to exist.  Write this to tempfile.mkdtemp()
        outFileName = "test/testDemand.dqt" 

        demand.write(outFileName)
        demand2 = Demand.read(net, outFileName)
        assert demand == demand2
        os.remove("test/testDemand.dqt")

    def test_readCubeDemand(self):

        fileName = os.path.join(os.path.dirname(__file__), '..', 'testdata', 
                                'dynameqNetwork_gearySubset', 'cubeTestDemand.txt')
        
        net = getTestNet()

        demand = Demand.readCubeODTable(fileName, net, "AUTO", Time(7,0), Time(8, 0))
                                     
        assert demand.getValue(Time(8, 0), 2, 6) == 1000
        assert demand.getValue(Time(8, 0), 6, 2) == 4000

    def NOtest_applyTimeOfDayFactors(self):

        fileName = os.path.join(os.path.dirname(__file__), '..', 'testdata', 
                                'dynameqNetwork_gearySubset', 'cubeTestDemand.txt')
        
        net = getTestNet()
        demand = Demand.readCubeODTable(fileName, net, "AUTO", Time(7,0), Time(8, 0))
                                     
        d2 = demand.applyTimeOfDayFactors([0.5, 0.5])

        assert d2.getValue(730, 2, 6) == 500
        assert d2.getValue(800, 2, 6) == 500

# Create the demand matrix 
# remove all the very short links. This is the only way to move forward.
# you may need to write the algoritm that finds invalid demand pairs 
# make a run. Maybe you should make a simple run first 
# you will need to apply the algorithm that takes care of the overlapping links 
