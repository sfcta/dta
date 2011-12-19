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
import sys
import pdb

from importExcelSignals import getNet, parseExcelCardFile,\
     convertSignalToDynameq, assignCardNames, mapIntersectionsByName, \
     mapMovements, addAllMovements
     

def verifySingleSignal(net, fileName):

    directory, fn = os.path.split(fileName)
    sd = parseExcelCardFile(directory, fn)
    cards = [sd]
    assignCardNames(cards)
    mapIntersectionsByName(net, cards)

    if not sd.mappedNodeId:
        print "The card was not mapped to a Cube node" 
    else:
        node = net.getNodeForId(sd.mappedNodeId)
        print "%20s,%s" % ("Cube int name", node.getStreetNames())
        print "%20s,%s" % ("Excel card name", str(sd.streetNames))
        cardsWithMovements = mapMovements(cards, net)

        nodeMovements = set([mov.getId() for mov in node.iterMovements()])
        mappedMovements = set()
        for mMovs in sd.mappedMovements.values():
            mappedMovements.update(mMovs)
            
        if len(mappedMovements) != node.getNumMovements():
            
            print "\t******************"
            print "\t*****  ERROR *****"
            print "\t******************"

        #for movDir, nodeTriplets in sd.mappedMovements.iteritems():
        #    print "Street or direction:", movDir            
        #    for nodeTriplet in nodeTriplets:
        #        print "\t\t%s" % nodeTriplet

        print "\nExcel links or movements"
        groupMovementNames = sd.phasingData.getElementsOfDimention(0)
        for gMov in groupMovementNames:
            print "\t\t%s" % gMov

        print "\nCube links and movements"

        for ilink in node.iterIncomingLinks():
            print "\t\t", ilink.getLabel(), ilink.getDirection(), "\t", ilink.getIid()
            for mov in ilink.iterOutgoingMovements():
                flag = ""
                if mov.getId() not in mappedMovements:
                    flag = "MISSING"
                print "\t\t\t\t", mov.getDirection(), "\t", mov.getId(), "\t", flag

        #now try converting the signal to dynameq
        START_TIME = 1500
        END_TIME = 1800 
        planInfo = net.addPlanCollectionInfo(START_TIME, END_TIME, "test", "excelSignalsToDynameq")
        try:
            dPlan = convertSignalToDynameq(node, sd, planInfo)
            dPlan.setPermittedMovements()            
            print dPlan
        except Exception, e:
            print str(e)


if __name__ == "__main__":

    net = getNet()
    addAllMovements(net)
    
    cardsDirectory = "/Users/michalis/Documents/workspace/dta/dev/testdata/cubeSubarea_sfCounty/excelSignalCards2/"

    if len(sys.argv) > 1:
        fileName = sys.argv[1]
    else:
        fileName = os.path.join(cardsDirectory, "10th Ave_California_Ch_12.xls")
        #fileName = os.path.join(cardsDirectory, "15th St_Market_Sanchez_Ch_32.xls")
        
    verifySingleSignal(net, fileName)    
    

