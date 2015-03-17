This is really a historic document at this point as the draft functional spec, since the actual design and implementation has evolved over time and we didn't keep this document up-to-date.  See http://dta.googlecode.com/git-history/master/doc/_build/html/index.html


---


# Overview #

The goal is to do these in phases, so from the beginning the core libraries will be able to read and write the DTA network files.  That way each subsequent phase can build on the network built by the previous one, and manual (GUI-based) DTA network editing can also be done between steps if that's the most effective way to incorporate updates.

## Phase I: Cube Network Import ##

**Input**: A Cube Roadway Network:
  * Cube network (.net file)
  * Cube turn penalties (.pen file)
**Output**: Dynameq ascii network files:
  * Base Network File (nodes, centroids, links, lane permissions, link events, lane events, virtual links, movements, movement events)
  * Advanced Network file (shift, vertices)
  * Custom Priorities file (movement priorities)

**Description**: This script will transform Cube network files into a set of Dynameq network files.  It should be pretty straightforward because of the limited set of attributes that will come from the Cube network files.  It should be able to read its output and write it out identically as well, to verify the read/write functionality is there and symmetric.

**Open issues**:
  * Defaults should be well documented here when established, and probably configurable.  Including a required option (e.g. no default).
  * Some scenario definitions are required from the beginning, like the vehicle types and classes; Need to determine how are those input.
  * Streetnames: Can these be in the label?  If not, why not?

GIS-based imports will probably go next because they are more fundamental changes, especially in terms of node numbering.

## GIS-based Road Geometry Import ##
For introducing extra points into links, to give them curvature.  Shifts may be here?  Or is this more trouble than it's worth?

## GIS-based Parking Lot Import ##
Or should this be manual? => punted to a later date

## Signal Card Import ##

## Synchro Network Import ##

## Stop Sign Import ##
From a GIS shapefile

## Transit Route Import ##

## Technical Spec Diagram ##
Placeholder until technical spec is more fleshed out and requires a new page.
<img src='http://dta.googlecode.com/files/TechnicalSpec.png'>