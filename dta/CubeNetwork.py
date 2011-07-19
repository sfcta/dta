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
import shutil
import subprocess
import sys
import tempfile
from .Centroid import Centroid
from .Connector import Connector
from .DtaError import DtaError
from .Logger import DtaLogger
from .Movement import Movement
from .Network import Network
from .Node import Node
from .RoadLink import RoadLink
from .RoadNode import RoadNode
from .VirtualLink import VirtualLink
from .VirtualNode import VirtualNode

class CubeNetwork(Network):
    """
    A DTA Network originating from a Cube network.
    """
    
    EXPORT_SCRIPTNAME = "ExportCubeForDta.s"
    EXPORT_SCRIPT = r"""
RUN PGM=NETWORK

NETI[1]=%s
 NODEO=%s\nodes.csv,FORMAT=SDF, INCLUDE=%s
 LINKO=%s\links.csv ,FORMAT=SDF, INCLUDE=%s
ENDRUN    
"""
    def __init__(self, scenario):
        """
        Constructor.  Initializes to an empty network.
        
        Keeps a reference to the given Scenario (a :py:class:`Scenario` instance)
        for :py:class:`VehicleClassGroup` lookups        
        """ 
        Network.__init__(self, scenario)
        
        #: node variable names; must include "N", "X" and "Y"
        self._nodeVariableNames = []
        #: id to variable list
        self._nodeVariables     = {}
        
        #: link variable names; must include "A" and "B"
        self._linkVariableNames = []
        #: id to variable list
        self._linkVariables     = {}

    def readNetfile(self, netFile, 
                    nodeVariableNames,
                    linkVariableNames,
                    **kwargs):
        """
        Reads the given netFile by exporting to CSV files and reading those.
        *nodeVariableNames* is a list of variable names for the nodes and
        *linkVariableNames* is a list of variable names for the links.
        See :py:meth:`CubeNetwork.readCSVs` for the description of the rest of the arguments.
        """
        tempdir = tempfile.mkdtemp()
        scriptFilename = os.path.join(tempdir, CubeNetwork.EXPORT_SCRIPTNAME)
        
        DtaLogger.info("Writing export script to %s" % scriptFilename)
        scriptFile = open(scriptFilename, "w")
        scriptFile.write(CubeNetwork.EXPORT_SCRIPT % 
                         (netFile, 
                          tempdir, ",".join(nodeVariableNames), 
                          tempdir, ",".join(linkVariableNames)))
        scriptFile.close()
        
        # run the script file
        DtaLogger.info("Running %s" % scriptFilename)
        cmd = "runtpp " + scriptFilename
        proc = subprocess.Popen( cmd, 
                                 cwd = tempdir, 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE )
        for line in proc.stdout:
            line = line.strip('\r\n')
            DtaLogger.info("  stdout: " + line)

        for line in proc.stderr:
            line = line.strip('\r\n')
            DtaLogger.info("stderr: " + line)
        retcode  = proc.wait()
        if retcode ==2:
            raise DtaError("Failed to export CubeNetwork using %s" % scriptFilename)

        DtaLogger.info("Received %d from [%s]" % (retcode, cmd))
        self.readCSVs(os.path.join(tempdir, "nodes.csv"), nodeVariableNames,
                      os.path.join(tempdir, "links.csv"), linkVariableNames,
                      **kwargs)
        shutil.rmtree(tempdir) 
        
    def readCSVs(self, 
                 nodesCsvFilename, nodeVariableNames,
                 linksCsvFilename, linkVariableNames,
                 centroidIds,
                 nodeGeometryTypeEvalStr,
                 nodeControlEvalStr,
                 nodePriorityEvalStr,
                 nodeLabelEvalStr,
                 nodeLevelEvalStr,
                 linkReverseAttachedIdEvalStr,
                 linkFacilityTypeEvalStr,
                 linkLengthEvalStr,
                 linkFreeflowSpeedEvalStr,
                 linkEffectiveLengthFactorEvalStr,
                 linkResponseTimeFactorEvalStr,
                 linkNumLanesEvalStr,
                 linkRoundAboutEvalStr,
                 linkLevelEvalStr,
                 linkLabelEvalStr):
        """
        Reads the network from the given csv files.
        * *nodesCsvFilename* is the csv with the node data; *nodeVariableNames* are the column names.
        * *linksCsvFilename* is the csv with the link data; *linkVariableNames* are the column names.
        * *centroidIds* is a list of the node Ids that should be interpreted as centroids
        
        The following strings are used to indicate how the **nodes** should be interpreted.  These
        will be eval()ed by python, and so they can reference one of the *nodeVariableNames*, or they
        can be constants.  
        
        For example, *nodeControlEvalStr* can be ``"RoadNode.CONTROL_TYPE_SIGNALIZED"`` if
        there are no useful node variables and we just want to default the control attribute of **all**
        :py:class:`RoadNode` to :py:attr:`RoadNode.CONTROL_TYPE_SIGNALIZED`.
        
        Alternatively, if a column in the file given by *nodesCsvFilename* could be used, then
        it can be referenced.  So if there is a column called "SIGNAL" which is 1 for signalized
        intersections and 0 otherwise, the *nodeControlEvalStr* could be 
        ``"RoadNode.CONTROL_TYPE_SIGNALIZED if int(SIGNAL)==1 else RoadNode.CONTROL_TYPE_UNSIGNALIZED"``.
        
        Note that the CSV fields are all strings, which is why SIGNAL is cast to an int here.
        
        * *nodeGeometryTypeEvalStr* indicates how to set the *geometryType* for each :py:class:`RoadNode`
        * *nodeControlEvalStr* indicates how to set the *control* for each :py:class:`RoadNode`
        * *nodePriorityEvalStr* indicates how to set the *priority* for each :py:class:`RoadNode`
        * *nodeLabelEvalStr* indicates how to set the *label* for each :py:class:`Node`
        * *nodeLevelEvalStr* indicates how to set the *level* for each :py:class:`Node`

        Similarly, the following strings are used to indicate how the **links** should be interpreted.
        
        * *linkReverseAttachedIdEvalStr* indicates how to set the *reversedAttachedId* for :py:class:`RoadLink`
          and :py:class:`Connector` instances
        * *linkFacilityTypeEvalStr* indicates how to set the *facilityType* for :py:class:`RoadLink`
          and :py:class:`Connector` instances
        * *linkLengthEvalStr* indicates how to set the *length* for :py:class:`RoadLink`
          and :py:class:`Connector` instances
        * *linkFreeflowSpeedEvalStr* indicates how to set the *freeflowSpeed* for :py:class:`RoadLink`
          and :py:class:`Connector` instances
        * *linkEffectiveLengthFactorEvalStr* indicates how to set the *effectiveLengthFactor* for :py:class:`RoadLink`
          and :py:class:`Connector` instances
        * *linkResponseTimeFactorEvalStr* indicates how to set the *responseTimeFactor* for :py:class:`RoadLink`
          and :py:class:`Connector` instances 
        * *linkNumLanesEvalStr* indicates how to set the *numLanes* for :py:class:`RoadLink`
          and :py:class:`Connector` instances
        * *linkRoundAboutEvalStr* indicates how to set the *roundAbout* for :py:class:`RoadLink`
          and :py:class:`Connector` instances
        * *linkLevelEvalStr* indicates how to set the *level* for :py:class:`RoadLink`
          and :py:class:`Connector` instances
        * *linkLabelEvalStr* indicates how to set the *label* for :py:class:`RoadLink`
          and :py:class:`Connector` instances
        
        """
        nIndex = nodeVariableNames.index("N")
        xIndex = nodeVariableNames.index("X")
        yIndex = nodeVariableNames.index("Y")
        
        aIndex = linkVariableNames.index("A")
        bIndex = linkVariableNames.index("B")
        
        countCentroids = 0
        countRoadNodes = 0        
        nodesFile = open(nodesCsvFilename, "r")
        for line in nodesFile:
            fields = line.strip().split(",")
            
            n = int(fields[nIndex])
            x = float(fields[xIndex])
            y = float(fields[yIndex])

            localsdict = {}
            for i,nodeVarName in enumerate(nodeVariableNames):
                localsdict[nodeVarName] = fields[i].strip("' ") # Cube csv strings are in single quotes
            
            newNode = None
            if n in centroidIds:
                newNode = Centroid(id=n,x=x,y=y,
                                   label=eval(nodeLabelEvalStr, globals(), localsdict),
                                   level=eval(nodeLevelEvalStr, globals(), localsdict))
                countCentroids += 1
            else:
                #TODO: allow user to set the defaults
                newNode = RoadNode(id=n,x=x,y=y,
                                   geometryType=eval(nodeGeometryTypeEvalStr, globals(), localsdict),
                                   control=eval(nodeControlEvalStr, globals(), localsdict),
                                   priority=eval(nodePriorityEvalStr, globals(), localsdict),
                                   label=eval(nodeLabelEvalStr, globals(), localsdict),
                                   level=eval(nodeLevelEvalStr, globals(), localsdict))
                countRoadNodes += 1
            self.addNode(newNode)
        DtaLogger.info("Read  %8d %-16s from %s" % (countCentroids, "centroids", nodesCsvFilename))
        DtaLogger.info("Read  %8d %-16s from %s" % (countRoadNodes, "roadnodes", nodesCsvFilename))
        nodesFile.close()
        
        linksFile = open(linksCsvFilename, "r")
        countConnectors = 0
        countRoadLinks  = 0
        for line in linksFile:
            fields = line.strip().split(",")
            
            a = int(fields[aIndex])
            b = int(fields[bIndex])
            
            nodeA = self.getNodeForId(a)
            nodeB = self.getNodeForId(b)
            
            localsdict = {}
            for i,linkVarName in enumerate(linkVariableNames):
                localsdict[linkVarName] = fields[i].strip("' ") # Cube csv strings are in single quotes
                
            newLink = None
            if isinstance(nodeA, Centroid) or isinstance(nodeB, Centroid):
                newLink = Connector \
                   (id                      = self._maxLinkId+1,
                    startNode               = nodeA,
                    endNode                 = nodeB,
                    reverseAttachedLinkId   = eval(linkReverseAttachedIdEvalStr, globals(), localsdict),
                    # facilityType            = eval(linkFacilityTypeEvalStr, globals(), localsdict),
                    length                  = eval(linkLengthEvalStr, globals(), localsdict),
                    freeflowSpeed           = eval(linkFreeflowSpeedEvalStr, globals(), localsdict),
                    effectiveLengthFactor   = eval(linkEffectiveLengthFactorEvalStr, globals(), localsdict),
                    responseTimeFactor      = eval(linkResponseTimeFactorEvalStr, globals(), localsdict),
                    numLanes                = eval(linkNumLanesEvalStr, globals(), localsdict),
                    roundAbout              = eval(linkRoundAboutEvalStr, globals(), localsdict),
                    level                   = eval(linkLevelEvalStr, globals(), localsdict),
                    label                   = eval(linkLabelEvalStr, globals(), localsdict))
                countConnectors += 1
            else:
                newLink = RoadLink \
                   (id                      = self._maxLinkId+1,
                    startNode               = nodeA,
                    endNode                 = nodeB,
                    reverseAttachedLinkId   = eval(linkReverseAttachedIdEvalStr, globals(), localsdict),
                    facilityType            = eval(linkFacilityTypeEvalStr, globals(), localsdict),
                    length                  = eval(linkLengthEvalStr, globals(), localsdict),
                    freeflowSpeed           = eval(linkFreeflowSpeedEvalStr, globals(), localsdict),
                    effectiveLengthFactor   = eval(linkEffectiveLengthFactorEvalStr, globals(), localsdict),
                    responseTimeFactor      = eval(linkResponseTimeFactorEvalStr, globals(), localsdict),
                    numLanes                = eval(linkNumLanesEvalStr, globals(), localsdict),
                    roundAbout              = eval(linkRoundAboutEvalStr, globals(), localsdict),
                    level                   = eval(linkLevelEvalStr, globals(), localsdict),
                    label                   = eval(linkLabelEvalStr, globals(), localsdict))
                countRoadLinks += 1
            self.addLink(newLink)
        DtaLogger.info("Read  %8d %-16s from %s" % (countConnectors, "connectors", linksCsvFilename))
        DtaLogger.info("Read  %8d %-16s from %s" % (countRoadLinks, "roadlinks", linksCsvFilename))
        linksFile.close()