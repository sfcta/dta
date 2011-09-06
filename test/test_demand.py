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
        demand = Demand(net, timeStep)

        d3 = datetime.datetime(2010, 1, 1, 8, 30)
        assert demand._timeInMin(d3) == 8 * 60 + 30
        timeStep = datetime.timedelta(minutes=15) 
        assert demand._timeInMin(timeStep) == 15

    def test_inMilitaryTime(self):

        net = getTestNet()
        timeStep = datetime.timedelta(minutes=15) 
        demand = Demand(net, timeStep) 
        d3 = datetime.datetime(2010, 1, 1, 8, 30)
        assert demand._datetimeToMilitaryTime(d3) == 830

    def test_militaryTimeToDateTime(self):

        net = getTestNet()
        timeStep = datetime.timedelta(minutes=15) 
        demand = Demand(net, timeStep) 
        d3 = datetime.datetime(2010, 1, 1, 8, 30)
        assert demand._datetimeToMilitaryTime(d3) == 830

        answer = demand._militaryTimeToDayTime(830)
        assert answer == d3

    def test_getTimeLabels(self):

        net = getTestNet()

        d3 = datetime.datetime(2010, 1, 1, 8, 0)
        d4 = datetime.datetime(2010, 1, 1, 9, 0)
        timeStep = datetime.timedelta(minutes=15) 

        demand = Demand(net, timeStep) 
        answer = map(demand._datetimeToMilitaryTime, demand._getTimeLabels(d3, d4, timeStep))
        assert answer == [815, 830, 845, 900]


