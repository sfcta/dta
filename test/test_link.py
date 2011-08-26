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

import nose.tools 

from dta.DynameqScenario import DynameqScenario 
from dta.DynameqNetwork import DynameqNetwork

def getTestNet():

    projectFolder = os.path.join(os.path.dirname(__file__), '..', 'testdata', 'cubeSubarea_downtownSF/dynameqNetwork')
    prefix = 'sf' 

    scenario = DynameqScenario(datetime.time(0,0,0), datetime.time(4,0,0))
    scenario.read(projectFolder, prefix) 
    net = DynameqNetwork(scenario) 
    net.read(projectFolder, prefix) 

    return net 


class TestLink(object):

    def test_acuteAngle(self):

        net = getTestNet()
        
        for node in net.iterNodes():
            if not node.isRoadNode():
                continue

            for link1 in node.iterAdjacentLinks():
                for link2 in node.iterAdjacentLinks():
                    if link1.getAcuteAngle(link2) <= 1:
                        print link1.getId(), link2.getId(), link1.getAcuteAngle(link2)
