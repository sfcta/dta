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
import datetime
import dta


from importExcelSignals import parseExcelCardFile,\
     convertSignalToDynameq, assignCardNames, mapIntersectionsByName, \
     mapMovements, addAllMovements


def getNet(netFile):
    
    dta.setupLogging("dtaInfo.log", "dtaDebug.log", logToConsole=True)

    # The rest of San Francisco currently exists as a Cube network.  Initialize it from
    # the Cube network files (which have been exported to dbfs.)
    sanfranciscoScenario = dta.DynameqScenario(datetime.datetime(2010,1,1,0,0,0), 
                                               datetime.datetime(2010,1,1,4,0,0))

    sanfranciscoScenario.read(r"X:\mx\dta\dev\testdata\CubeNetworkSource_renumberExternalsOnly\dynameqNetwork", "sf13")
    
    sanfranciscoCubeNet = dta.CubeNetwork(sanfranciscoScenario)
    sanfranciscoCubeNet.readNetfile \
       (netFile=netFile,
      #(netFile=r"Y:\dta\SanFrancisco\2010\CubeNetworkSource\SanFranciscoSubArea_2010.net",
       nodeVariableNames=["N","X","Y"],
       linkVariableNames=["A","B","TOLL","USE",
                          "CAP","AT","FT","STREETNAME","TYPE",
                          "MTYPE","SPEED","DISTANCE","TIME",
                          "LANE_AM","LANE_OP","LANE_PM",
                          "BUSLANE_AM","BUSLANE_OP","BUSLANE_PM",
                          "TOLLAM_DA","TOLLAM_SR2","TOLLAM_SR3",
                          "TOLLPM_DA","TOLLPM_SR2","TOLLPM_SR3",
                          "TOLLEA_DA","TOLLEA_SR2","TOLLEA_SR3",
                          "TOLLMD_DA","TOLLMD_SR2","TOLLMD_SR3",
                          "TOLLEV_DA","TOLLEV_SR2","TOLLEV_SR3",
                          "VALUETOLL_FLAG","PASSTHRU",
                          "BUSTPS_AM","BUSTPS_OP","BUSTPS_PM",
                          ],
       centroidIds                      = range(1,999),
       nodeGeometryTypeEvalStr          = "Node.GEOMETRY_TYPE_INTERSECTION",
       nodeControlEvalStr               = "RoadNode.CONTROL_TYPE_SIGNALIZED",
       nodePriorityEvalStr              = "RoadNode.PRIORITY_TEMPLATE_NONE",
       nodeLabelEvalStr                 = "None",
       nodeLevelEvalStr                 = "None",
       linkReverseAttachedIdEvalStr     = "None", #TODO: fix?
       linkFacilityTypeEvalStr          = "int(FT)",
       linkLengthEvalStr                = "float(DISTANCE)",
       linkFreeflowSpeedEvalStr         = "float(SPEED)",
       linkEffectiveLengthFactorEvalStr = "1",
       linkResponseTimeFactorEvalStr    = "1.05",
       linkNumLanesEvalStr              = "2 if isConnector else (int(LANE_PM) + (1 if int(BUSLANE_PM)>0 else 0))",
       linkRoundAboutEvalStr            = "False",
       linkLevelEvalStr                 = "None",
       linkLabelEvalStr                 = '(STREETNAME if STREETNAME else "")'
       #linkLabelEvalStr                 = '(STREETNAME if STREETNAME else "") + (" " if TYPE and STREETNAME else "") + (TYPE if TYPE else "")'
       )
    
    addAllMovements(sanfranciscoCubeNet)


    #sanfranciscoCubeNet.applyTurnProhibitions(r"X:\mx\dta\dev\testdata\regional_test_network\turnspm.pen")
    sanfranciscoDynameqNet = dta.DynameqNetwork(scenario=sanfranciscoScenario)
    sanfranciscoDynameqNet.deepcopy(sanfranciscoCubeNet)
    #sanfranciscoDynameqNet.removeShapePoints()
    
    # add virtual nodes and links between Centroids and RoadNodes
    sanfranciscoDynameqNet.insertVirtualNodeBetweenCentroidsAndRoadNodes()
    sanfranciscoDynameqNet.moveCentroidConnectorsFromIntersectionsToMidblocks()
    
    return sanfranciscoDynameqNet


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
            print "\t\t", ilink.getLabel(), ilink.getDirection(), "\t", ilink.getId()
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
        except dta.DtaError, e:
            print str(e)


if __name__ == "__main__":
    
    cubeNetworkName = r"X:\mx\dta\dev\testdata\regional_test_network\FREEFLOW.net"
    cubeNetworkName = r"X:\mx\dta\dev\testdata\CubeNetworkSource_renumberExternalsOnly\SanFranciscoSubArea_2010.net"
    
    net = getNet(cubeNetworkName)

    pdb.set_trace()
    
    cardsDirectory = r"X:\mx\dta\dev\testdata\cubeSubarea_sfCounty\excelSignalCards2"

    if len(sys.argv) > 1:
        fName = sys.argv[1]
        fileName = os.path.join(cardsDirectory, fName)
    else:
        fileName = os.path.join(cardsDirectory, "10th Ave_California_Ch_12.xls")
        #fileName = os.path.join(cardsDirectory, "15th St_Market_Sanchez_Ch_32.xls")
    
    pdb.set_trace()    
    verifySingleSignal(net, fileName)    
    

