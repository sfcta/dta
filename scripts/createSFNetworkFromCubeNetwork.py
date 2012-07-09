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
import getopt
import os
import sys
import pdb

USAGE = r"""

 python createSFNetworkFromCubeNetwork.py  [-n output_nodes.shp] [-l output_links.shp]  sf_cube_net_file sf_cube_turnpen_file [cube_attach_shapefile]
 
 e.g.
 
 python createSFNetworkFromCubeNetwork.py -n sf_nodes.shp -l sf_links.shp Y:\dta\SanFrancisco\2010\SanFranciscoSubArea_2010.net Y:\dta\SanFrancisco\2010\network\turnspm.pen Q:\GIS\Road\SFCLINES\AttachToCube\stclines.shp
 
 This script reads the San Francisco Cube network and optionally the *cube_attach_shapefile*
 and converts it to a Dynameq network, writing it out to the current directory as sf_*.dqt.
 
  * The first arg is the San Francisco Cube network for conversion to a Dynameq DTA network
  * The second arg is the turn penalty file to use
  * An optional third argument is the shapefile to use to add shape points to the roadway network (to show road curvature, etc)
  * Optional shapefile outputs: -n to specify a node shapefile output, -l to specify a link shapefile output
 
 """

def addShifts(sanfranciscoCubeNet):
    """
    The San Francisco network has a few places where the roadway geometries need clarification via "shifts" --
    e.g. some local lanes need to be shifted to be outside the through lanes.
    """
    # geary local
    sanfranciscoCubeNet.getLinkForNodeIdPair(26594,26590).addShifts(3,3, addShapepoints=True)  # Steiner to Fillmore
    sanfranciscoCubeNet.getLinkForNodeIdPair(26590,26587).addShifts(3,3, addShapepoints=True)  # Fillmore to Webster
    
    # geary - lyon 2 baker
    geary_lyon2baker = sanfranciscoCubeNet.getLinkForNodeIdPair(26835,26811)
    geary_lyon2baker.addShifts(0,1, addShapepoints=True) # shift access lane  
    geary_lyon2baker.findOutgoingMovement(26762)._outgoingLane = 1
    
    sanfranciscoCubeNet.getLinkForNodeIdPair(26587,26590).addShifts(3,3, addShapepoints=True)  # Webster to Fillmore
    sanfranciscoCubeNet.getLinkForNodeIdPair(26590,26596).addShifts(3,3, addShapepoints=True)  # Fillmore to Avery
    sanfranciscoCubeNet.getLinkForNodeIdPair(26596,26594).addShifts(3,3, addShapepoints=True)  # Avery to Steiner
    
    # broadway tunnel - access links
    sanfranciscoCubeNet.getLinkForNodeIdPair(25117,25111).addShifts(0,2, addShapepoints=True)  # Mason to Powell
    
    # HWY 101 N On-Ramp at Marin / Bayshore
    sanfranciscoCubeNet.getLinkForNodeIdPair(33751,33083).addShifts(1,0, addShapepoints=True)

def createTransitOnlyLanes(sanfranciscoCubeNet, allVCG, transitVCG):
    """
    Creates transit-only lanes based on the BUSLANE_PM field.
    """
    for link in sanfranciscoCubeNet.iterRoadLinks():
        ab_tuple = (link.getStartNode().getId(), link.getEndNode().getId())
        if ab_tuple not in sanfranciscoCubeNet.additionalLinkVariables: continue
        
        buslane_pm = int(sanfranciscoCubeNet.additionalLinkVariables[ab_tuple]["BUSLANE_PM"])
        
        # no transit lanes, don't worry about it
        if buslane_pm == 0: continue
        
        for lane_id in range(link.getNumLanes()):
            # diamond lane or side BRT lane
            if lane_id == 0 and (buslane_pm == 1 or buslane_pm == 2):
                link.addLanePermission(lane_id, transitVCG)
            # center BRT lane
            elif lane_id == link.getNumLanes()-1 and buslane_pm == 3:
                link.addLanePermission(lane_id, transitVCG)
            else:
                link.addLanePermission(lane_id, allVCG)
        
def removeHOVStubs(sanfranciscoDynameqNet):
    """
    The San Francisco network has a few "HOV stubs" -- links intended to facilitate future coding of HOV lanes
    Find these and remove them
    """    
    nodesToRemove = []
    for node in sanfranciscoDynameqNet.iterNodes():
        # one incomine link, one outgoing link
        if node.getNumIncomingLinks() != 1: continue
        if node.getNumOutgoingLinks() != 1: continue
        
        removalCandidate = True
        # the incoming/outgoing links must each be a road link of facility type 6
        for link in node.iterAdjacentLinks():
            if not link.isRoadLink(): 
                removalCandidate = False
                break
            if link.getFacilityType() != 9:
                removalCandidate = False
                break
        
        if removalCandidate:
            nodesToRemove.append(node)
    
    for node in nodesToRemove:
        dta.DtaLogger.info("Removing HOV Stub node %d" % node.getId())
        sanfranciscoDynameqNet.removeNode(node)

#: this_is_main
if __name__ == '__main__':
    
    optlist, args = getopt.getopt(sys.argv[1:], "n:l:")

    if len(args) <= 2:
        print USAGE
        sys.exit(2)
    
    SF_CUBE_NET_FILE            = args[0]
    SF_CUBE_TURN_PROHIBITIONS   = args[1]
    
    SF_CUBE_SHAPEFILE           = None
    if len(args) > 2:
        SF_CUBE_SHAPEFILE       = args[2]

    OUTPUT_NODE_SHAPEFILE       = None
    OUTPUT_LINK_SHAPEFILE       = None
    for (opt,arg) in optlist:
        if opt=="-n":
            OUTPUT_NODE_SHAPEFILE  = arg
        elif opt=="-l":
            OUTPUT_LINK_SHAPEFILE  = arg
            
    # The SanFrancisco network will use feet for vehicle lengths and coordinates, and miles for link lengths
    dta.VehicleType.LENGTH_UNITS= "feet"
    dta.Node.COORDINATE_UNITS   = "feet"
    dta.RoadLink.LENGTH_UNITS   = "miles"

    dta.setupLogging("createSFNetworkFromCubeNetwork.INFO.log", "createSFNetworkFromCubeNetwork.DEBUG.log", logToConsole=True)
        
    # The rest of San Francisco currently exists as a Cube network.  Initialize it from
    # the Cube network files (which have been exported to dbfs.)
    # This is where we define the :py:class:`dta.Scenario`
    sanfranciscoScenario = dta.DynameqScenario(dta.Time(0,0), dta.Time(23,0))

    # We will have 4 vehicle classes: Car_NoToll, Car_Toll, Truck_NoToll, Truck_Toll 
    # We will provide demand matrices for each of these classes
    sanfranciscoScenario.addVehicleClass("Car_NoToll")
    sanfranciscoScenario.addVehicleClass("Car_Toll")
    sanfranciscoScenario.addVehicleClass("Truck_NoToll")
    sanfranciscoScenario.addVehicleClass("Truck_Toll")
    # Transit is an implicit type
    
    # length is in feet (from above), response time is in seconds, maxSpeed is in mi/hour
    # We have only 2 vehicle types                      Type        VehicleClass    Length  RespTime    MaxSpeed    SpeedRatio
    sanfranciscoScenario.addVehicleType(dta.VehicleType("Car",      "Car_NoToll",   14,     1,          100.0,      100.0))
    sanfranciscoScenario.addVehicleType(dta.VehicleType("Car",      "Car_Toll",     14,     1,          100.0,      100.0))
    sanfranciscoScenario.addVehicleType(dta.VehicleType("Truck",    "Truck_NoToll", 30,     1.6,        70.0,       90.0))
    sanfranciscoScenario.addVehicleType(dta.VehicleType("Truck",    "Truck_Toll",   30,     1.6,        70.0,       90.0))
    sanfranciscoScenario.addVehicleType(dta.VehicleType("LRT1",     "Transit",      75,     1.6,        35.0,       90.0))
    sanfranciscoScenario.addVehicleType(dta.VehicleType("LRT2",     "Transit",     150,     1.6,        35.0,       90.0))
    sanfranciscoScenario.addVehicleType(dta.VehicleType("Trolley_Std",  "Transit",  40,     1.6,        70.0,       90.0))
    sanfranciscoScenario.addVehicleType(dta.VehicleType("Trolley_Artic","Transit",  60,     1.6,        70.0,       90.0))
    sanfranciscoScenario.addVehicleType(dta.VehicleType("Motor_Std",    "Transit",  40,     1.6,        70.0,       90.0))
    sanfranciscoScenario.addVehicleType(dta.VehicleType("Motor_Artic",  "Transit",  60,     1.6,        70.0,       90.0))
    sanfranciscoScenario.addVehicleType(dta.VehicleType("CableCar",     "Transit",  27.5,   1.6,         9.5,       90.0))    
    # Generic is an implicit type

    # VehicleClassGroups
    allVCG     = dta.VehicleClassGroup(dta.VehicleClassGroup.CLASSDEFINITION_ALL,        dta.VehicleClassGroup.CLASSDEFINITION_ALL,          "#bebebe")
    transitVCG = dta.VehicleClassGroup(dta.VehicleClassGroup.CLASSDEFINITION_TRANSIT,    dta.VehicleClassGroup.CLASSDEFINITION_TRANSIT,      "#55ff00")
    sanfranciscoScenario.addVehicleClassGroup(allVCG)
    sanfranciscoScenario.addVehicleClassGroup(transitVCG)
    sanfranciscoScenario.addVehicleClassGroup(dta.VehicleClassGroup(dta.VehicleClassGroup.CLASSDEFINITION_PROHIBITED, dta.VehicleClassGroup.CLASSDEFINITION_PROHIBITED,   "#ffff00"))
    sanfranciscoScenario.addVehicleClassGroup(dta.VehicleClassGroup("Toll",                           "Car_Toll|Truck_Toll",                              "#0055ff"))
    
    # Generalized cost
    # TODO: Make this better!?!
    sanfranciscoScenario.addGeneralizedCost("Expression_0", # name
                                            "Seconds",      # units
                                            "ptime+(left_turn_pc*left_turn)+(right_turn_pc*right_turn)", # turn_expr
                                            "0",            # link_expr
                                            ""              # descr
                                            )
    
    # Read the Cube network
    sanfranciscoCubeNet = dta.CubeNetwork(sanfranciscoScenario)
    centroidIds         = range(1,982)  # centroids 1-981 are internal to SF
    centroidIds.extend([1204,1205,1207,1191,1192,1206,6987,6994,7144,7177,
                        7654,7677,7678,7705,7706,7709,7721,7972,7973,8338,
                        8339,8832])     # externals
    # Derived in Y:\dta\TrafficFlowParameters.xlsx
    # Updated for freeways and expressways based on Caltrans sensors for freeways in SF
    # Updated for locals/collectors and arterials based on MTA speed data
    speedLookup = { \
        'FT1 AT0':35, 'FT1 AT1':40, 'FT1 AT2':45, 'FT1 AT3':45, 'FT1 AT4':55, 'FT1 AT5':55, 
        'FT2 AT0':60, 'FT2 AT1':65, 'FT2 AT2':65, 'FT2 AT3':65, 'FT2 AT4':70, 'FT2 AT5':70, 
        'FT3 AT0':60, 'FT3 AT1':65, 'FT3 AT2':65, 'FT3 AT3':65, 'FT3 AT4':65, 'FT3 AT5':65, 
        'FT4 AT0':25, 'FT4 AT1':25, 'FT4 AT2':30, 'FT4 AT3':30, 'FT4 AT4':35, 'FT4 AT5':35, 
        'FT5 AT0':30, 'FT5 AT1':30, 'FT5 AT2':35, 'FT5 AT3':35, 'FT5 AT4':40, 'FT5 AT5':40, 
        'FT7 AT0':30, 'FT7 AT1':30, 'FT7 AT2':35, 'FT7 AT3':35, 'FT7 AT4':40, 'FT7 AT5':40, 
        'FT11 AT0':25, 'FT11 AT1':25, 'FT11 AT2':30, 'FT11 AT3':30, 'FT11 AT4':35, 'FT11 AT5':35, 
        'FT12 AT0':30, 'FT12 AT1':30, 'FT12 AT2':35, 'FT12 AT3':35, 'FT12 AT4':40, 'FT12 AT5':40, 
        'FT15 AT0':30, 'FT15 AT1':30, 'FT15 AT2':35, 'FT15 AT3':35, 'FT15 AT4':50, 'FT15 AT5':50, 
    }
    # Derived in Y:\dta\TrafficFlowParameters.xlsx
    responseTimeLookup = { \
        'FT1 AT0':1.3747, 'FT1 AT1':1.4146, 'FT1 AT2':1.3973, 'FT1 AT3':1.3973, 'FT1 AT4':1.3967, 'FT1 AT5':1.3967, 
        'FT2 AT0':1.3332, 'FT2 AT1':1.3535, 'FT2 AT2':1.3295, 'FT2 AT3':1.3438, 'FT2 AT4':1.3172, 'FT2 AT5':1.3172, 
        'FT3 AT0':1.9918, 'FT3 AT1':1.9918, 'FT3 AT2':1.7999, 'FT3 AT3':1.8142, 'FT3 AT4':1.7480, 'FT3 AT5':1.7480, 
        'FT4 AT0':4.7892, 'FT4 AT1':4.4273, 'FT4 AT2':4.1113, 'FT4 AT3':3.7949, 'FT4 AT4':3.2806, 'FT4 AT5':3.0688, 
        'FT5 AT0':1.8427, 'FT5 AT1':1.8427, 'FT5 AT2':1.7377, 'FT5 AT3':1.7377, 'FT5 AT4':1.7776, 'FT5 AT5':1.7776, 
        'FT7 AT0':3.0156, 'FT7 AT1':2.8806, 'FT7 AT2':2.7521, 'FT7 AT3':2.7521, 'FT7 AT4':2.7521, 'FT7 AT5':2.7521, 
        'FT11 AT0':9.1528, 'FT11 AT1':9.2273, 'FT11 AT2':9.2806, 'FT11 AT3':7.9091, 'FT11 AT4':7.9091, 'FT11 AT5':7.9091, 
        'FT12 AT0':4.0581, 'FT12 AT1':3.7416, 'FT12 AT2':3.5605, 'FT12 AT3':3.3205, 'FT12 AT4':3.3205, 'FT12 AT5':3.3205, 
        'FT15 AT0':3.0688, 'FT15 AT1':2.9205, 'FT15 AT2':2.7831, 'FT15 AT3':2.8080, 'FT15 AT4':2.8080, 'FT15 AT5':2.8080, 
    }
    # see http://code.google.com/p/dta/wiki/NetworkDescriptionForSF
    ftToDTALookup = {"2":1,
                     "3":2,
                     "1":3,
                     "7":4,
                     "15":4,
                     "12":5,
                     "4":6,
                     "11":7,
                     "5":8,
                     # centroid connectors should be what?
                     "6":9,
                     }
    
    sanfranciscoCubeNet.readNetfile \
      (netFile=SF_CUBE_NET_FILE,
       nodeVariableNames=["N","X","Y","OLD_NODE"],
       linkVariableNames=["A","B","TOLL","USE",
                          "CAP","AT","FT","STREETNAME","TYPE",
                          "MTYPE","SPEED","DISTANCE","TIME",
                          "LANE_AM","LANE_OP","LANE_PM",
                          "BUSLANE_AM","BUSLANE_OP","BUSLANE_PM",
                          "TOLLAM_DA","TOLLAM_SR2","TOLLAM_SR3",
                          "TOLLPM_DA","TOLLPM_SR2","TOLLPM_SR3",
                          "TOLLEA_DA","TOLLEA_SR2","TOLLEA_SR3",
                          "TOLLMD_DA","TOLLMD_SR2","TOLLMD_SR3",
                          "TOLLEV_DA","TOLLEV_SR2","TOLLEV_SR3 ",
                          "VALUETOLL_FLAG","PASSTHRU",
                          "BUSTPS_AM","BUSTPS_OP","BUSTPS_PM",
                          ],
       centroidIds                      = centroidIds,
       useOldNodeForId                  = True,
       nodeGeometryTypeEvalStr          = "Node.GEOMETRY_TYPE_INTERSECTION",
       nodeControlEvalStr               = "RoadNode.CONTROL_TYPE_SIGNALIZED",
       nodePriorityEvalStr              = "RoadNode.PRIORITY_TEMPLATE_NONE",
       nodeLabelEvalStr                 = "None",
       nodeLevelEvalStr                 = "None",
       linkReverseAttachedIdEvalStr     = "None", #TODO: fix?
       linkFacilityTypeEvalStr          = "ftToDTALookup[FT]",
       linkLengthEvalStr                = "float(DISTANCE)",
       linkFreeflowSpeedEvalStr         = "45.0 if FT=='6' else float(speedLookup['FT'+FT+' AT'+AT])",
       linkEffectiveLengthFactorEvalStr = "1.17", # estimated based on queue length survey data
       linkResponseTimeFactorEvalStr    = "1.1 if FT=='2' else 1.2",  # estimated based on saturation flow analysis on survey data and PeMS freeway sensors
       linkNumLanesEvalStr              = "2 if isConnector else (int(LANE_PM) + (1 if int(BUSLANE_PM)>0 else 0))",
       linkRoundAboutEvalStr            = "False",
       linkLevelEvalStr                 = "None",
       linkLabelEvalStr                 = '(STREETNAME if STREETNAME else "") + (" " if TYPE and STREETNAME else "") + (TYPE if TYPE else "")',
       linkGroupEvalStr                 = "-1",
       linkSkipEvalStr                  = "FT=='13'", # skip bike-only
       additionalLocals                 = {'ftToDTALookup':ftToDTALookup,
                                           'speedLookup':speedLookup,
                                           'responseTimeLookup':responseTimeLookup
                                           })

    # Apply the transit lanes
    createTransitOnlyLanes(sanfranciscoCubeNet, allVCG, transitVCG)
        
    # create the movements for the network for all vehicles
    sanfranciscoCubeNet.addAllMovements(allVCG, includeUTurns=False)
    
    # Apply the turn prohibitions
    sanfranciscoCubeNet.applyTurnProhibitions(SF_CUBE_TURN_PROHIBITIONS)
    
    # Read the shape points so curvy streets look curvy
    # 3, 4 are the Broadway Tunnel, being routed too far south in GIS file
    # 5234 # Skip this one link at Woodside/Portola because it overlaps
    # 2798, # Skip this Central Freeway link because Dynameq hates it but I DON'T KNOW WHY
    if SF_CUBE_SHAPEFILE:
        sanfranciscoCubeNet.readLinkShape(SF_CUBE_SHAPEFILE, "A", "B",
                                          skipEvalStr="(OBJECTID in [3,4,5234,2798]) or (MEDIANDIV==1)")
     
    # Some special links needing shifts
    addShifts(sanfranciscoCubeNet)
    
    # Convert the network to a Dynameq DTA network
    sanfranciscoDynameqNet = dta.DynameqNetwork(scenario=sanfranciscoScenario)
    sanfranciscoDynameqNet.deepcopy(sanfranciscoCubeNet)
    
    # the San Francisco network has a few "HOV stubs" -- links intended to facilitate future coding of HOV lanes
    removeHOVStubs(sanfranciscoDynameqNet)
    
    # Add virtual nodes and links between Centroids and RoadNodes; required by Dynameq
    sanfranciscoDynameqNet.insertVirtualNodeBetweenCentroidsAndRoadNodes(startVirtualNodeId=9000000, startVirtualLinkId=9000000,
                                                                         distanceFromCentroid=50)
    
    # Move the centroid connectors from intersection nodes to midblock locations
    # TODO: for dead-end streets, is this necessary?  Or are the midblocks ok?        
    sanfranciscoDynameqNet.moveCentroidConnectorsFromIntersectionsToMidblocks(splitReverseLinks=True, moveVirtualNodeDist=50, externalNodeIds=[], 
                                                                              disallowConnectorEvalStr="True if self.getFacilityType() in [1,8] else False")

    # Warn on overlapping links, and move virtual nodes up to 100 feet if that helps
    sanfranciscoDynameqNet.handleOverlappingLinks(warn=True, moveVirtualNodeDist=100)
    
    # finally -- Dynameq requires links to be longer than the longest vehicle
    sanfranciscoDynameqNet.handleShortLinks(1.05*sanfranciscoScenario.maxVehicleLength()/5280.0,
                                            warn=True,
                                            setLength=True)

    # if we have too many nodes for the license 10
    if sanfranciscoDynameqNet.getNumRoadNodes() > 12500:
        sanfranciscoDynameqNet.removeUnconnectedNodes()
    sanfranciscoDynameqNet.write(dir=r".", file_prefix="sf")
 
    # export the network as shapefiles if requested 
    if OUTPUT_NODE_SHAPEFILE: sanfranciscoDynameqNet.writeNodesToShp(OUTPUT_NODE_SHAPEFILE)
    if OUTPUT_LINK_SHAPEFILE: sanfranciscoDynameqNet.writeLinksToShp(OUTPUT_LINK_SHAPEFILE) 
 
    
    
