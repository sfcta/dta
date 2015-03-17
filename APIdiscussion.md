This is just a take on what a desirable API to work with would be.

# Network Object #
## Network Import ##
```
net = loadNet(filename or list of files, from='dynameq,'cubeNet','shp','dynust',etc) 
```
Alternately, this could be autodetected..

Michalis: Agree. One can do this now by introducing what they call a "simple factory method". This is a good idea provided that 1) there is not a big difference in the number of input files. 2) This is important: the net object that is being returned has to adhere to one common interface. Therefore one should prepare cube, transcad, dynusT etc network objects......which we have but we need to polish all this stuff

Lisa: Ok, this brings up the question of which network types we will support?  My initial understanding was that the Network would be a DTA Network and not a Cube network, but I am fine with having Network with a Cube subclass and a DTA subclass (with Dynameq being either a subclass or just an output format, depending on how inherently different the properties/structures of different DTA flavors are?  Which I have no idea.)  BUT given this, what is the goal of a generic factory method that hides these details -- why not be explicit in the calling code?
```
cubenet = CubeNetwork(cube args, like files but maybe more, like info about what the link attributes are)
```

## Network addition ##
```
net2 = net.addNet(filename or set,
                  from='dta-object','dynameq,'cubeNet','shp','dynust',etc
                  priority=which network rules when there are conflicts)
```
This would load the new net and and merge it with the original probably by
first converting whatever you were adding to a dta object, and then merging the dta object.

Michalis: this is a good idea or a long term goal. Let's discuss on the phone how we are going to do it because if we do it naively we are going have each network object import every other network object plus the class that does the conversion. We probably need to define an interface for all the classes that deal with network conversions and then do a design pattern. Also we may consider having this add or merge logic not attached to the network namespace. Depends on how often one would add or merge networks.

Alternatively, we could do an explicit add for each type
```
net = net.addNodes('nodes.dbf',type='cubeNodes')
net = net.addLinks('links.dbf',type='cubeLinks')
net = net.addSignals(filename or dir,type='sfmtaSignalCards')
net = net.addTurnPens(filename,type='cubeTurnPens')
net = net.addTransit(filename,type='cubeLIN')
net = net.addCounts(filename,type='mvmtCounts')
etc.
```

Lisa: Again, this assumes the only inputs to reading a network are file names and hides potential other details.  I would prefer:
```
gearynet_dta = !DynameqNetwork(dtanetfiles, other args?)
sfnet_cube = !CubeNetwork(cubenetfiles, other args?)
gearynet_dta.add(sfnet_cube, priority args, etc)
```


## Network Contents ##
```
net.links
net.nodes
net.transitLines
net.movements
net.zones / net.centroids
net.intersections
net.centroidConnectors
net.paths
net.shapepoints
etc.
```

This is more or less what is going on but with a few differences. Nodes and links, zones, centroidConnectors and paths are stored the way Elizabeth describes. Movements are accessed from nodes and movements. Shapepoints are part of nodes.
## Network Iterators ##
which I guess would be built in if the contents were true lists.

```
for l in net.links
for n in net.nodes
for i in net.intersections
etc.
```

Michalis: I suggest we use the iter keyword. For example if you were to access the keys of a dictonary you would write for key in myDict.iterkeys()

Lisa: I like the iter convention.