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

import datetime
import os 

import la
import nose.tools 
import numpy as np

from dta.demand import Demand
from dta.DynameqNetwork import DynameqNetwork 
from dta.DynameqScenario import DynameqScenario 


def getTestNet():

    projectFolder = os.path.join(os.path.dirname(__file__), '..', 'testdata', 'dynameqNetwork_gearySubset')
    prefix = 'smallTestNet' 

    scenario = DynameqScenario(datetime.datetime(2010,1,1,0,0), datetime.datetime(2010,1,1,4,0))
    scenario.read(projectFolder, prefix) 
    #nose.tools.set_trace()
    net = DynameqNetwork(scenario) 

    net.read(projectFolder, prefix) 

    return net 


class TestDemand:


    def test_time(self):

        d = datetime.time(8, 30)
        print d.hour
        print d.minute
        print d.second 

        timeStep = datetime.timedelta(minutes=15) 
        d2 = datetime.time(9, 30)


        #d2 - timeStep

        d3 = datetime.datetime(2010, 1, 1, 8, 0)
        d4 = datetime.datetime(2010, 1, 1, 9, 0)


        data = {}
        date = d3
        while date != d4:
            date += timeStep
            print date 
            data[date] = 1798798723

        #print d4 - d3 

        print data[datetime.datetime(2010, 1, 1, 8, 15)]

        print d4.hour
        print d4.minute

    def test_time(self):

        net = getTestNet()
        timeStep = datetime.timedelta(minutes=15) 
        
        startTime = datetime.datetime(2010, 1, 1, 8, 30)
        endTime = datetime.datetime(2010, 1, 1, 9, 30)
        timeStep = datetime.timedelta(minutes=15) 
        demand = Demand(net, Demand.DEFAULT_VEHCLASS, startTime, endTime, timeStep)

        d3 = datetime.datetime(2010, 1, 1, 8, 30)
        assert demand._timeInMin(d3) == 8 * 60 + 30
        timeStep = datetime.timedelta(minutes=15) 
        assert demand._timeInMin(timeStep) == 15

    def test_inMilitaryTime(self):

        net = getTestNet()

        startTime = datetime.datetime(2010, 1, 1, 8, 30)
        endTime = datetime.datetime(2010, 1, 1, 9, 30)
        timeStep = datetime.timedelta(minutes=15) 
        demand = Demand(net, Demand.DEFAULT_VEHCLASS, startTime, endTime, timeStep)

        d3 = datetime.datetime(2010, 1, 1, 8, 30)
        assert demand._datetimeToMilitaryTime(d3) == 830

    def test_militaryTimeToDateTime(self):

        net = getTestNet()

        startTime = datetime.datetime(2010, 1, 1, 8, 30)
        endTime = datetime.datetime(2010, 1, 1, 9, 30)
        timeStep = datetime.timedelta(minutes=15) 
        demand = Demand(net, Demand.DEFAULT_VEHCLASS, startTime, endTime, timeStep)

        d3 = datetime.datetime(2010, 1, 1, 8, 30)
        assert demand._datetimeToMilitaryTime(d3) == 830

        answer = demand._militaryTimeToDayTime(830)
        assert answer == d3

    def test_getTimePeriods(self):

        net = getTestNet()

        startTime = datetime.datetime(2010, 1, 1, 8, 30)
        endTime = datetime.datetime(2010, 1, 1, 9, 30)
        timeStep = datetime.timedelta(minutes=15) 
        demand = Demand(net, Demand.DEFAULT_VEHCLASS, startTime, endTime, timeStep)

        d3 = datetime.datetime(2010, 1, 1, 8, 0)
        d4 = datetime.datetime(2010, 1, 1, 9, 0)

        answer = map(demand._datetimeToMilitaryTime, demand._getTimePeriods(d3, d4, timeStep))
        assert answer == [815, 830, 845, 900]

    def test_read(self):
        
        fileName = os.path.join(os.path.dirname(__file__), '..', 'testdata', 
                                'dynameqNetwork_gearySubset', 'gearysubnet_matx.dqt')

        net = getTestNet() 

        demand = Demand.read(net, fileName)
        assert demand.getNumSlices() == 4

        assert demand.getValue(15, 56, 8) == 1000
        assert demand.getValue(45, 8, 2) == 8.5

        demand.setValue(45, 8, 2, 35)
        assert demand.getValue(45, 8, 2) == 35

        demand.setValue(15, 56, 8, 4001) 
        assert not demand.getValue(15, 56, 8) == 4000
        assert demand.getValue(15, 56, 8) == 4001

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

        outFileName = "test/testDemand.dqt" 

        demand.write(outFileName)
        demand2 = Demand.read(net, outFileName)
        assert demand == demand2
        os.remove("test/testDemand.dqt")

    def test_readCubeDemand(self):

        fileName = os.path.join(os.path.dirname(__file__), '..', 'testdata', 
                                'dynameqNetwork_gearySubset', 'cubeTestDemand.txt')
        
        net = getTestNet()

        demand = Demand.readCubeODTable(fileName, net, "AUTO", datetime.datetime(2010, 1, 1, 7,0,0),
                                     datetime.datetime(2010, 1, 1, 8, 0, 0))

        assert demand.getValue(800, 2, 6) == 1000
        assert demand.getValue(800, 6, 2) == 4000

    def test_applyTimeOfDayFactors(self):

        fileName = os.path.join(os.path.dirname(__file__), '..', 'testdata', 
                                'dynameqNetwork_gearySubset', 'cubeTestDemand.txt')
        
        net = getTestNet()
        demand = Demand.readCubeODTable(fileName, net, "AUTO", datetime.datetime(2010, 1, 1, 7,0,0),
                                     datetime.datetime(2010, 1, 1, 8, 0, 0))
        

        
        d2 = demand.applyTimeOfDayFactors([0.5, 0.5])

        assert d2.getValue(730, 2, 6) == 500
        assert d2.getValue(800, 2, 6) == 500




# Create the demand matrix 
# remove all the very short links. This is the only way to move forward.
# you may need to write the algoritm that finds invalid demand pairs 
# make a run. Maybe you should make a simple run first 
# you will need to apply the algorithm that takes care of the overlapping links 
