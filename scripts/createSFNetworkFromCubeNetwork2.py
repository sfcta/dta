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
import shapefile

import pdb 
import random 
import datetime
import dta
import os 
from dta.DynameqScenario import DynameqScenario
from dta.Algorithms import dfs 
from dta.demand import Demand

USAGE = """

 python createSFNetworkFromCubeNetwork.py
 
 """

def readShapefiles(): 
    """
    Read the nodes and links from the shapefiles below
    """

    linkShapefile = "/Users/michalis/Documents/workspace/dta/dev/testdata/CubeNetworkSource_renumberExternalsOnly/SanFranciscoSubArea_2010_Link"
    nodeShapefile = "/Users/michalis/Documents/workspace/dta/dev/testdata/CubeNetworkSource_renumberExternalsOnly/SanFranciscoSubArea_2010_Nodes"

    sanfranciscoScenario = getTestScenario() 
    cubeNetwork = dta.CubeNetwork(sanfranciscoScenario)
    
    cubeNetwork.readFromShapefiles(
        nodesShpFilename=nodeShapefile,
        nodeVariableNames=["N","X","Y"],
        linksShpFilename=linkShapefile,
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
        nodeControlEvalStr               = "RoadNode.CONTROL_TYPE_UNSIGNALIZED",
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
        linkLabelEvalStr                 = '(STREETNAME if STREETNAME else "") + (" " if TYPE and STREETNAME else "") + (TYPE if TYPE else "")'
        )

    #cubeNetwork.applyTurnProhibitions("/Users/michalis/Documents/workspace/dta/dev/testdata/CubeNetworkSource_renumberExternalsOnly/turnsam.pen")

def writeFeasibleDestinations(net):
    """
    This function runs a Depth First Tree to find the 
    which destinations are feasible from a given origin.
    This function was used to check the synthetic OD 
    matrix that was created (function writeDemandTable) 
    for testing purposes
    """
    output = open("feasibleDestinations.txt", "w")
    for cen in net.iterCentroids():
        dfs(net, cen)

        feasibleDestinations = []
        for cen2 in net.iterCentroids():
            if cen2.post > 0:
                feasibleDestinations.append(str(cen2.getId()))
        
        output.write("%d" % cen.getId())
        output.write(",")
        output.write(",".join(feasibleDestinations))
        output.write("\n")
        print cen.getId()

    output.close()

def writeDemandTable(net):
    """
    This function creates a uniform OD table demand is about 600K vehicles 
    """
    startTime = datetime.datetime(2010, 1, 1, 6, 30)
    endTime = datetime.datetime(2010, 1, 1, 9, 30)
    timeStep = datetime.timedelta(minutes=15) 
    demand = Demand(net, Demand.DEFAULT_VEHCLASS, startTime, endTime, timeStep)
    
    for i in range(demand.getNumSlices()):
        for j in range(net.getNumCentroids()):
            for k in range(net.getNumCentroids()):                
                demand._la[i, j, k] = random.randint(0, 4) / 4.0

    print demand.getTotalDemand() 
    return demand
    
def removePartOfTheNetwork(net):
    """
    This function removes all the nodes that are south of 
    node 4761. This function was used earlier in the 
    development process
    """
    n = net.getNodeForId(4761)
    nodesToDelete = []
    for node in net.iterNodes():
        if node.getY() < n.getY():
            nodesToDelete.append(node)

    for node in nodesToDelete:
        net.removeNode(node)

def removeVerySmallLinks(net):
    """
    This function removes very small links from the 
    network to avoid Dynameq errors 
    """
    linksToDelete = []
    for link in net.iterLinks():
        if link.isRoadLink():
            if link.getEuclidianLengthInMiles() < 0.004:
                #print link.getId() 
                linksToDelete.append(link) 
    
    #tmp = sorted([link.getEuclidianLengthInMiles() for link in net.iterLinks() if link.isRoadLink()])
    
    for link in linksToDelete:
        net.removeLink(link)
    
    print "Number of links to delete", len(linksToDelete)

def collectStats(net):
    """
    This function prints the number of shape points in the network
    """
    numShapePoints = 0
    for node in sanfranciscoCubeNet.iterNodes():
        if node.isShapePoint():
            numShapePoints +=1
    print "num shape points", numShapePoints


    numIntersections = 0
    for node in sanfranciscoCubeNet.iterNodes():
        if node.isRoadNode() and node.hasConnector():
            numIntersections += 1
    print "Num intersections with connectors", numIntersections

    exit()             
            

    from collections import defaultdict 
    conPerCentroid = defaultdict(int)
    for node in sanfranciscoCubeNet.iterNodes():
        if node.isCentroid():
            conPerCentroid[node.getNumAttachedConnectors()] += 1

    for i in sorted(conPerCentroid.keys()):
        print "num centroids=", conPerCentroid[i], " num connnectors=", i 
            

def removeOverlappingRoadLinks(net):
    """
    this function removes the overlapping links from the 
    network. Used in the earlier steps of the development
    """
    linksToDelete = []
    for node in net.iterNodes():
        if not node.isRoadNode():
            continue
        for rLink in node.iterAdjacentLinks():
            if not rLink.isRoadLink():
                continue
            hasOverlappingLinks = False
            
            for rLink2 in node.iterAdjacentLinks():
                if rLink2 == rLink:
                    continue 
                if not rLink2.isRoadLink():
                    continue
                if rLink.isOverlapping(rLink2):
                    hasOverlappingLinks = True 
                    linksToDelete.append(rLink2) 
                    break 
            if hasOverlappingLinks:
                break 

    for link in linksToDelete:
        net.removeLink(link) 

def getTestScenario(): 
    """
    return a test scenario
    """
    projectFolder = "/Users/michalis/Documents/workspace/dta/dev/testdata/dynameqNetwork_gearySubset"
    prefix = 'smallTestNet' 

    scenario = DynameqScenario(datetime.datetime(2010,1,1,0,0,0), 
                               datetime.datetime(2010,1,1,4,0,0))
    scenario.read(projectFolder, prefix) 

    return scenario 

 
if __name__ == '__main__':
    
    dta.setupLogging("dtaInfo.log", "dtaDebug.log", logToConsole=True)

    #this is just a test scenario that will be used for multiple networks
    sanfranciscoScenario = getTestScenario() 
    
    # The Geary network was created in an earlier Phase of work, so it already exists as
    # a Dynameq DTA network.  Initialize it from the Dynameq text files.
    #gearyScenario = dta.DynameqScenario(startTime=datetime.time(hour=0),
    #                                    endTime=datetime.time(hour=1))
    #gearyScenario.read(dir=".", file_prefix="Base_Final")
    #gearyScenario.write(dir="test", file_prefix="geary")

    #read the gearyDTA network    
    gearynetDta = dta.DynameqNetwork(scenario=sanfranciscoScenario)
    gearynetDta.read(dir="/Users/michalis/Documents/workspace/dta/dev/testdata/dynameqNetwork_geary", file_prefix="Base")

    #gearynetDta.write(dir="test", file_prefix="geary")
    
    # The rest of San Francisco currently exists as a Cube network.  Initialize it from
    # the Cube network files (which have been exported to dbfs.)

                           
    #projectFolder2 = "/Users/michalis/Documents/workspace/dta/dev/testdata/cubeSubarea_downtownSF" 
    projectFolder2 = "/Users/michalis/Documents/workspace/dta/dev/testdata/cubeSubarea_sfCounty" 
    #sanfranciscoScenario.read(dir=os.path.join(projectFolder2, "dynameqNetwork"), file_prefix="sf") 

            
    sanfranciscoCubeNet = dta.CubeNetwork(sanfranciscoScenario)

    sanfranciscoCubeNet.readCSVs(
      nodesCsvFilename=os.path.join(projectFolder2, "nodes.csv"), 
       nodeVariableNames=["N","X","Y"],
       linksCsvFilename=os.path.join(projectFolder2, "links.csv"), 
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
       nodeControlEvalStr               = "RoadNode.CONTROL_TYPE_UNSIGNALIZED",
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
       linkLabelEvalStr                 = '(STREETNAME if STREETNAME else "") + (" " if TYPE and STREETNAME else "") + (TYPE if TYPE else "")'
       )

    
    #create the San Francisco network 
    sanfrancsicoDynameqNet = dta.DynameqNetwork(scenario=sanfranciscoScenario)
    #copy the Cube SF network to a dynameq one
    sanfrancsicoDynameqNet.deepcopy(sanfranciscoCubeNet)
    
    #remove the shapepoints from the network
    sanfrancsicoDynameqNet.removeShapePoints()

    #this is not necessary
    #removePartOfTheNetwork(sanfrancsicoDynameqNet)
    
    #writeFeasibleDestinations(sanfrancsicoDynameqNet)
    #demand = writeDemandTable(sanfrancsicoDynameqNet)    
    #demand.write("testDemand3.txt")

    #exit()

    # add virtual nodes and links between Centroids and RoadNodes
    sanfrancsicoDynameqNet.insertVirtualNodeBetweenCentroidsAndRoadNodes(startVirtualNodeId=9000000, startVirtualLinkId=9000000)

    #remove nodes from the network that are not connected to the network
    nodes = [node for node in sanfrancsicoDynameqNet.iterRoadNodes() if node.getCardinality() == (0,0)]
    for node in nodes:
        sanfrancsicoDynameqNet.removeNode(node)


    sanfrancsicoDynameqNet.removeCentroidConnectorsFromIntersections(splitReverseLinks=True) 
    sanfrancsicoDynameqNet.moveVirtualNodesToAvoidOverlappingLinks()
   
    #removeOverlappingRoadLinks(sanfrancsicoDynameqNet)
    
    removeVerySmallLinks(sanfrancsicoDynameqNet)
    sanfrancsicoDynameqNet.moveVirtualNodesToAvoidShortConnectors()

    outputFolder = "/Users/michalis/Documents/workspace/dta/dev/testdata/cubeSubarea_sfCounty"

    #This is not ready yet and will throw and excep
    #gearynetDta.mergeSecondaryNetwork(sanfrancsicoDynameqNet)

    sanfrancsicoDynameqNet.write(dir=os.path.join(outputFolder, "dynameqNetwork"), file_prefix="sf11")
    sanfranciscoScenario.write(dir=os.path.join(outputFolder, "dynameqNetwork"), file_prefix="sf11")   

    exit(0)
    
    # Merge them together
    sanfranciscoNet = gearynetDta
    sanfranciscoNet.merge(sanfranciscoCubeNet)
    
    # Write the result.  sanfrancisco_dta is a DynameqNetwork
    sanfranciscoNet.write(dir = ".", file_prefix="SanFrancisco_")
    
