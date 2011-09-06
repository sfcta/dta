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

    scenario = DynameqScenario(datetime.datetime(2010,1,1,0,0), datetime.datetime(2010,1,1,4,0))

    scenario.read(projectFolder, prefix) 
    net = DynameqNetwork(scenario) 
    net.read(projectFolder, prefix) 

    return net 


class TestLink(object):

    def test_acuteAngle(self):

        net =getTestNet()

        link1 = net.getLinkForNodeIdPair(3178, 3183)
        link2 = net.getLinkForNodeIdPair(3183, 3185)

        assert link1.getAcuteAngle(link2) < 0.001 
        assert link2.getAcuteAngle(link1) == link1.getAcuteAngle(link2)

    def NOtest_acuteAngle(self):

        net = getTestNet()
        

        link1 = net.getLinkForId(2221)
        link2 = net.getLinkForId(902480) 

                             
        nodes = net.iterNodes()
        #nodes = [net.getNodeForId(2085)]

        for node in nodes:
            if not node.isRoadNode():
                continue
 
#            for link in node.iterAdjacentLinks():
#                if node.isOverlapping(link, 2):
#                    pass

            for link1 in node.iterIncomingLinks():
                for link2 in node.iterIncomingLinks():
                    if link1 == link2:
                        continue

#                    if not (link1.isRoadLink() and link2.isRoadLink()):
#                        continue
                    
                    if not link1.isConnector() and not link2.isConnector():
                        continue 

                    if link1.getAcuteAngle(link2) <= 1:
                        print node.getId(), link1.getId(), link2.getId(), link1.getAcuteAngle(link2)



            for link1 in node.iterOutgoingLinks():
                for link2 in node.iterOutgoingLinks():
                    if link1 == link2:
                        continue


#                    if not (link1.isRoadLink() and link2.isRoadLink()):
#                        continue

                    if not link1.isConnector() and not link2.isConnector():
                        continue 


                    if link1.getAcuteAngle(link2) <= 1:
                        print node.getId(), link1.getId(), link2.getId(), link1.getAcuteAngle(link2)


        
