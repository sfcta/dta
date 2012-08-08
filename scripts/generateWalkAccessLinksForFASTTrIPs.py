__copyright__   = "Copyright 2012 SFCTA"
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
import dta
import getopt
import itertools
import os
import sys

# requires pyproj for projecting lat,long to the SF network coordinate space
# requires transitfeed for parsing the GTFS


USAGE = r"""

 
"""

    
if __name__ == "__main__":
    optlist, args = getopt.getopt(sys.argv[1:], "")

    #if len(args) != 4:
    #    print USAGE
    #    sys.exit(2)
        
    INPUT_DYNAMEQ_NET_DIR         = r"Q:\Model Development\FastTrips\Transit.Dynameq\sf_gtfs_50pctdemand.iter0"  # args[0]
    INPUT_DYNAMEQ_NET_PREFIX      = "sf_final" # args[1]
    OUTPUT_ACCESSLINKS_FILE       = "ft_input_accessLinks.dat"
    
    # these are the units of the dynameq input files
    dta.VehicleType.LENGTH_UNITS= "feet"
    dta.Node.COORDINATE_UNITS   = "feet"
    dta.RoadLink.LENGTH_UNITS   = "miles"

    dta.setupLogging("generateWalkAccessLinksForFASTTrIPs.INFO.log", "generateWalkAccessLinksForFASTTrIPs.DEBUG.log", logToConsole=True)

    # reads the dynameq input (scenario, network)
    scenario = dta.DynameqScenario(dta.Time(0,0), dta.Time(23,0))
    scenario.read(INPUT_DYNAMEQ_NET_DIR, INPUT_DYNAMEQ_NET_PREFIX) 
    net = dta.DynameqNetwork(scenario)
    net.read(INPUT_DYNAMEQ_NET_DIR, INPUT_DYNAMEQ_NET_PREFIX)
    
    # { stopid -> (link, position) }
    stopid_to_linkpos = {}
    # { nodeid -> set( (stopids,dist) ) }
    nodeid_to_stopidset = {}
    
    # read the transit file
    input_transit_filename = os.path.join(INPUT_DYNAMEQ_NET_DIR, "%s_ptrn.dqt" % INPUT_DYNAMEQ_NET_PREFIX)
    for transitline in dta.TransitLine.read(net, input_transit_filename):
        tripid = str(transitline.id)
    
        for transit_seg in transitline.iterSegments():
            # we don't care about no stop links
            if transit_seg.label == "nostop": continue
            if transit_seg.label.startswith("label"): continue
            
            # get stopid
            label_parts = transit_seg.label.split(",")
            if len(label_parts) != 2:
                dta.DtaLogger.error("Don't understand transit segment label %s for %s" % (transit_seg.label, str(transit_seg)))
                continue
            
            stopid = label_parts[0]
            prop   = float(label_parts[1])
            linklen= transit_seg.link.euclideanLength(includeShape=True)
            
            stopid_to_linkpos[stopid] = (transit_seg.link, prop)
            
            # fill in nodeid_to_stopidset
            dist_from_start = prop*linklen
            dist_from_end   = (1.0-prop)*linklen
            
            startnodeid = transit_seg.link.getStartNode().getId()
            if startnodeid not in nodeid_to_stopidset:
                nodeid_to_stopidset[startnodeid] = set()
            nodeid_to_stopidset[startnodeid].add( (stopid,dist_from_start) )
            
            endnodeid = transit_seg.link.getEndNode().getId()
            if endnodeid not in nodeid_to_stopidset:
                nodeid_to_stopidset[endnodeid] = set()
            nodeid_to_stopidset[endnodeid].add( (stopid,dist_from_end) )
                        
    
    dta.DtaLogger.debug("nodeid_to_stopidset = %s" % str(nodeid_to_stopidset))
    # to use for cutoff
    stopid_to_coords = {}
    
    # here - add reverse links so people can walk backwards on one-way links
    new_id = 9500000
    # create roadlink list to iterate through since we'll be modifying the network
    roadlinks = []
    for roadlink in net.iterRoadLinks():
        roadlinks.append(roadlink)
        
    # iterate
    for roadlink in roadlinks:
        startid = roadlink.getStartNode().getId()
        endid   = roadlink.getEndNode().getId()
        
        try:
            revlink = net.getLinkForNodeIdPair(endid, startid)
        except:
            # no reverse link!  create one and add it
            revlink = roadlink.createReverseLink(new_id) 
            net.addLink(revlink)
            
            new_id += 1
    
    # generate the access link for each taz centroid to each walkable stop
    for taz in range(1,982):
        
        # get the centroid
        try:
            centroid = net.getNodeForId(taz)
        except:
            dta.DtaLogger.info("No centroid for %d -- Skipping" % taz)
            continue
        
        vertices_set = dta.ShortestPaths.labelSettingWithLabelsOnNodes(net, sourceVertex=centroid, endVertex=None, 
                                                                       includeVirtual=True, maxLabel=5280.0/2.0,
                                                                       filterRoadLinkEvalStr="roadlink.getFacilityType() in [1,2,3,8]")
        
        dta.DtaLogger.debug("TAZ %d" % taz)
        for node in vertices_set:
            dta.DtaLogger.debug("  Node %7d  Dist %10.3f  PrevNode %7d  stopids? %s" % 
                                (node.getId(), node.label, node.predVertex.getId() if node.predVertex else 0,
                                str(nodeid_to_stopidset[node.getId()]) if (node and node.getId() in nodeid_to_stopidset) else ""))
            
    sys.exit(0)
    
    
    # start the output file
    output_transit_filename = "%s_ptrn.dqt" % OUTPUT_DYNAMEQ_NET_PREFIX
    output_transit_file = open(output_transit_filename, mode='w')
    output_transit_file.write(dta.TransitLine.getDynameqFileHeaderStr())
    
    output_transit_file.close()
    dta.DtaLogger.info("Wrote %8d %-16s to %s" % (transit_line_num, "TRANSIT LINES", output_transit_filename))
    dta.DtaLogger.info("Updated %d out of %d dwell times" % (dwell_updated, (dwell_updated+dwell_notupdated)))