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

        demand = Demand.readDynameqTable(net, fileName)
        assert demand.getNumSlices() == 4

        assert demand.getValue(Time(0, 15), 56, 8) == 4000
        assert demand.getValue(Time(0, 45), 8, 2) == 34

        demand.setValue(Time(0, 45), 8, 2, 35)
        assert demand.getValue(Time(0, 45), 8, 2) == 35

        demand.setValue(Time(0, 15), 56, 8, 4001) 
        assert not demand.getValue(Time(0, 15), 56, 8) == 4000
        assert demand.getValue(Time(0, 15), 56, 8) == 4001

    def test_write(self):
        """
        """

        fileName = os.path.join(os.path.dirname(__file__), '..', 'testdata', 
                                'dynameqNetwork_gearySubset', 'gearysubnet_matx.dqt')

        net = getTestNet() 
        demand = Demand.readDynameqTable(net, fileName)

        # TODO: this requires subdir test to exist.  Write this to tempfile.mkdtemp()
        outFileName = "test/testDemand.dqt" 

        demand.writeDynameqTable(outFileName)
        demand2 = Demand.readDynameqTable(net, outFileName)
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

