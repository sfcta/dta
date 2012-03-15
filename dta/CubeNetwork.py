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
import pdb
import shapefile

import os
import shutil
import subprocess
import sys
import tempfile
from itertools import izip 

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
        
        #: "old" node number to node number, see discussion of *nodeOldNodeStr* in readCSVs()
        self._oldNodeNumToNodeNum = None

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
                 nodeOldNodeStr,
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
        * *nodeOldNodeStr* indicates how to correspond Node numbers to original Node numbers.  This is
          relevant if the cube network is the result of a Subarea Extraction, in which case node renumbering
          may have occurred but the old node numbers are still useful.  If passed, a node number to old node number
          correspondence will be retained.  Pass None if this feature won't be used; a typical use would be
          to pass ``"int(OLD_NODE)"``.

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
        if nodeOldNodeStr: self._oldNodeNumToNodeNum = {}
        
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
            
            if nodeOldNodeStr: self._oldNodeNumToNodeNum[eval(nodeOldNodeStr, globals(), localsdict)] = n

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
                localsdict['isConnector'] = True
                try: 
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
                except DtaError, e:
                    DtaLogger.error("Error adding Connector from %d to %d - skipping: %s" %
                                    (nodeA.getId(), nodeB.getId(), str(e)))
                    continue
            else:
                localsdict['isConnector'] = False
                try: 
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
                except DtaError, e:
                    DtaLogger.error("Error adding RoadLink from %d to %d - skipping: %s" %
                                    (nodeA.getId(), nodeB.getId(), str(e)))
                    continue 
            self.addLink(newLink)
        DtaLogger.info("Read  %8d %-16s from %s" % (countConnectors, "connectors", linksCsvFilename))
        DtaLogger.info("Read  %8d %-16s from %s" % (countRoadLinks, "roadlinks", linksCsvFilename))
        linksFile.close()
        
    def readFromShapefiles(self, nodesShpFilename, nodeVariableNames,
                 linksShpFilename, linkVariableNames,
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

        sf = shapefile.Reader(nodesShpFilename)
        shapes = sf.shapes()
        records = sf.records()

        fields = [field[0] for field in sf.fields[1:]]
        for shape, recordValues in izip(shapes, records):
            x, y = shape.points[0]
            localsdict = dict(izip(fields, recordValues))
            n = int(localsdict["N"])
            
            newNode = None
            if n in centroidIds:
                newNode = Centroid(id=n,x=x,y=y,
                                   label=eval(nodeLabelEvalStr, globals(), localsdict),
                                   level=eval(nodeLevelEvalStr, globals(), localsdict))
            else:
                newNode = RoadNode(id=n,x=x,y=y,
                                   geometryType=eval(nodeGeometryTypeEvalStr, globals(), localsdict),
                                   control=eval(nodeControlEvalStr, globals(), localsdict),
                                   priority=eval(nodePriorityEvalStr, globals(), localsdict),
                                   label=eval(nodeLabelEvalStr, globals(), localsdict),
                                   level=eval(nodeLevelEvalStr, globals(), localsdict))
            try:
                self.addNode(newNode)
            except DtaError, e:
                print e

        sf = shapefile.Reader(linksShpFilename)
        shapes = sf.shapes()
        records = sf.records()

        fields = [field[0] for field in sf.fields[1:]]
        for shape, recordValues in izip(shapes, records):

            localsdict = dict(zip(fields, recordValues))
            startNodeId = int(localsdict["A"])
            endNodeId = int(localsdict["B"])

            try:
                startNode = self.getNodeForId(startNodeId)
                endNode = self.getNodeForId(endNodeId)
            except DtaError, e:
                print e 
                continue

            newLink = None
            if isinstance(startNode, Centroid) or isinstance(endNode, Centroid):
                localsdict['isConnector'] = True
                try: 
                    newLink = Connector \
                        (id                      = self.getMaxLinkId() + 1,
                        startNode               = startNode,
                        endNode                 = endNode,
                        reverseAttachedLinkId   = eval(linkReverseAttachedIdEvalStr, globals(), localsdict),
                        #facilityType            = eval(linkFacilityTypeEvalStr, globals(), localsdict),
                        length                  = -1, # eval(linkLengthEvalStr, globals(), localsdict),
                        freeflowSpeed           = 30, #eval(linkFreeflowSpeedEvalStr, globals(), localsdict),
                        effectiveLengthFactor   = 1.0, #eval(linkEffectiveLengthFactorEvalStr, globals(), localsdict),
                        responseTimeFactor      = 1.0, # eval(linkResponseTimeFactorEvalStr, globals(), localsdict),
                        numLanes                = 1, # eval(linkNumLanesEvalStr, globals(), localsdict),
                        roundAbout              = 0, # eval(linkRoundAboutEvalStr, globals(), localsdict),
                        level                   = 0, #eval(linkLevelEvalStr, globals(), localsdict),
                        label                   = "") # eval(linkLabelEvalStr, globals(), localsdict))
                except DtaError, e:
                    DtaLogger.error("%s" % str(e))
                    continue
            else:
                localsdict['isConnector'] = False
                try: 
                    newLink = RoadLink \
                       (id                      = self.getMaxLinkId()+1,
                        startNode               = startNode,
                        endNode                 = endNode,
                        reverseAttachedLinkId   = eval(linkReverseAttachedIdEvalStr, globals(), localsdict),
                        facilityType            = eval(linkFacilityTypeEvalStr, globals(), localsdict),
                        length                  = -1, # eval(linkLengthEvalStr, globals(), localsdict),
                        freeflowSpeed           = 30, #eval(linkFreeflowSpeedEvalStr, globals(), localsdict),
                        effectiveLengthFactor   = 1.0, #eval(linkEffectiveLengthFactorEvalStr, globals(), localsdict),
                        responseTimeFactor      = 1.0, #eval(linkResponseTimeFactorEvalStr, globals(), localsdict),
                        numLanes                = 1, #eval(linkNumLanesEvalStr, globals(), localsdict),
                        roundAbout              = 0, #eval(linkRoundAboutEvalStr, globals(), localsdict),
                        level                   = 0, #eval(linkLevelEvalStr, globals(), localsdict),
                        label                   = 0) #eval(linkLabelEvalStr, globals(), localsdict))
                except DtaError, e:
                    DtaLogger.error("%s" % str(e))
                    continue
            newLink._shapePoints = shape.points
            self.addLink(newLink)
            
    def applyTurnProhibitions(self, fileName):
        """
        Apply the turn prohibitions found in the filename
        """
        inputStream = open(fileName, 'r')
        movements_removed = 0
        lines_read        = 0
        
        for line in inputStream:
            fields      = line.strip().split()
            startNodeId = int(fields[0])
            nodeId      = int(fields[1])
            endNodeId   = int(fields[2])
            lines_read += 1
            
            try:
                link = self.getLinkForNodeIdPair(startNodeId, nodeId)
                mov = link.getOutgoingMovement(endNodeId)                
            except DtaError, e:
                DtaLogger.error("Error finding movement %d %d %d - skipping: %s" %
                                (startNodeId, nodeId, endNodeId, str(e)))                
                continue
            
            # DtaLogger.info("Removing movement %d-%d-%d found in turn prohibition file" % (startNodeId, nodeId, endNodeId))
            link.removeOutgoingMovement(mov)
            movements_removed += 1
        
        DtaLogger.info("Removed %d movements out of %d found in %s" % (movements_removed, lines_read, fileName))
        
    def readLinkShape(self, linkShapefile, startNodeIdField, endNodeIdField, useOldNodeNum=False, skipField=None, skipValueList=None):
        """
        Uses the given *linkShapefile* to add shape points to the network, in order to more accurately
        represent the geometry of the roads.  For curvey or winding roads, this will help reduce errors in understanding
        intersections because of the angles involved.
        
        *startNodeIdField* and *endNodeIdField* are the column headers (so they're strings)
        of the start node and end node IDs within the *linkShapefile*.
        
        If *useOldNodeNum* is passed, the shapefile will be assumed to be referring to the old node numbers rather
        than the current node numbers; see :py:meth:`CubeNetwork.readCSVs` discussion of the arg *nodeOldNodeStr* for
        more information on the old node numbers.
        
        If *skipField* is passed, then the field given by this name will be checked against the list of values given
        by *skipValueList*.  This is useful for when there are some bad elements in your shapefile that you want to skip.
        
        If a link with the same (node1,node2) pair is specified more than once in the shapefile, only the first one
        will be used.
        
        Does this in two passes; in the first pass, the (a,b) from the shapefile is looked up in the network, and used
        to add shape points.  In the second pass, the (b,a) from the shapefile is looked up in the network, and used
        to add shape points **if that link has not already been updated from the first pass**.
        
        .. todo:: Dynameq warns/throws away shape points when there is only one, which makes me think the start or end
                  node should be included too.  However, if we include either the first or the last shape point below,
                  everything goes crazy.  I'm not sure why?
        """ 

        sf      = shapefile.Reader(linkShapefile)
        shapes  = sf.shapes()
        records = sf.records()
        
        links_found         = 0
        shapepoints_added   = 0

        fields = [field[0] for field in sf.fields]
        
        # if the first field is the 'DeletionFlag' -- remove
        if fields[0] == 'DeletionFlag':
            fields.pop(0)
            
        # If a link with the same (node1,node2) pair is specified more than 
        # once in the shapefile, only the first one will be used.
        links_done = {}
        
        # two passes - regular and reverse
        for direction in ["regular","reverse"]:
            
            for shape, recordValues in izip(shapes, records):

                assert(len(fields)==len(recordValues))
                
                localsdict  = dict(zip(fields, recordValues))
                
                # check if we're instructed to skip this one
                if skipField and (skipField in fields) and (localsdict[skipField] in skipValueList): continue
                
                if direction == "regular":
                    startNodeId = int(localsdict[startNodeIdField])
                    endNodeId   = int(localsdict[endNodeIdField])
                else:
                    startNodeId = int(localsdict[endNodeIdField])
                    endNodeId   = int(localsdict[startNodeIdField])
                        
                # DtaLogger.debug("shape %d %d" % (startNodeId, endNodeId))
    
                if useOldNodeNum:
                    try:
                        startNodeId = self._oldNodeNumToNodeNum[startNodeId]
                        endNodeId   = self._oldNodeNumToNodeNum[endNodeId]
                    except:
                        # couldn't find relevant nodes
                        continue
                
                if (startNodeId, endNodeId) in links_done: continue 
                    
                if self.hasLinkForNodeIdPair(startNodeId, endNodeId):
                    link = self.getLinkForNodeIdPair(startNodeId, endNodeId)
                    links_found += 1
                    
                    # just a straight line - no shape points necessary
                    if len(shape.points) == 2: continue
                    
                    # Dynameq throws away a single, see todo above
                    if len(shape.points) == 3: continue
                    
                    # don't include the first and last, they're already there
                    link._shapePoints = shape.points[1:-1]
                    if direction == "reverse": link._shapePoints.reverse()
                    shapepoints_added += len(shape.points)-2
                    
                    links_done[(startNodeId, endNodeId)] = True

        DtaLogger.info("Read %d shape points for %d links from %s" % (shapepoints_added, links_found, linkShapefile))