
## What is DTA? ##

DTA stands for Dynamic Traffic Assignment.  What is that?  It is a tool for figuring out how drivers route themselves through a transportation network taking into account things like congestion from other drivers, transit vehicles, signal timings, stop signs, slope, etc.

For a more comprehensive and technical overview of DTA, see: ["A Primer on Dynamic Traffic Assignment"](http://www.fsutmsonline.net/images/uploads/mtf-files/dta_primer.pdf) published by the [Transportation Research Board](http://www.trb.org)

## What is the DTA Anyway Project? ##
It's a few things...

**It's a San Francisco DTA Model!**


**It's a code base!**


**It's a research project!**

We are trying to simultaneously _develop an open-source code base_ to lower the barrier to entry to large-scale DTA modeling and reduce the amount a brute force effort necessary (its more fun to write code than hand-draw millions of lines), while _researching how a large-scale DTA model works_ both by itself, and when integrated with an activity-based travel demand model....all while creating _a working and calibrated DTA model of San Francisco County_ for us to use for the many projects here that want to use it!

**About the name**: we applied for a huge federal grant to do DTA here in San Francisco a while ago and got passed over.  After crying a few days, we decided "Hey, we are going to do DTA Anyway!" and started working on it in our spare time/weekends.  Soon afterwards, we actually won a separate federal grant (thanks, [FHWA](http://www.fhwa.gov)!) and were able to move forward with the project during daylight/weekday hours.

## What Can It Be Used For? ##

It is a tool that we can use to see what happens if we change various parts of a street network (i.e. update signal timing, make a street two-way, re-route a bus line), or what happens in the future when traffic shift based on development patterns.

Currently, the San Francisco DTA Model (we'll think up a snazzier name for it soon, we promise) is being used to analyze the [Geary BRT](http://gearybrt.org) project and was used to analyze the impact of ramp closures for the construction of the [Presidio Parkway](http://presidioparkway.org/).

## What Do You Use To Answer Those Questions Now? ##
(AKA shouldn't you already be able to do that?)

The long-winded answer is below.  The short answer is: we have a way, it is just icky and time-consuming.

There are two types of tools that we use to answer these types of questions now.  They generally fall under the category of _macroscopic_ and _microscopic_ traffic models - incidentally, DTA is often described as a _mesoscopic_ traffic model.

  * _macroscopic_ traffic models are generally used to answer the question _where do the cars go?_ and is analyzed on a regional scale (i.e. the entire Bay Area)
  * _microscopic_ traffic models are generally used to answer the question _if there are X vehicles who want to use street Y, how well does it work?_ and is generally the size of a few blocks.

There significant differences in what _micro_ and _macro_ models are good at.  You can think of them like a road bike and a mountain bike, each good at a specific type of biking, but you probably don't want use a road bike on a mountain bike trail or visa versa. Here's the quick low-down:

**Macroscopic Traffic Models**:

Good For:
  * Analyzing where cars travel on a regional scale
Knows About:
  * How people find the best route (shortest path)
  * A rough idea of the effect of other vehicles on somebody's travel time
Doesn't Know About:
  * traffic signals/stop signs
  * having to wait your turn to make a left turn
  * queues spilling back for several blocks (congestion on each link is analyzed by itself)
  * physical impossibilities of a roadway. It will keep cramming people on to a road that doesn't have any available capacity and just assign them a really long travel time.
Data Requirements:
  * very small.  It only really needs the capacity of each road and the speed that vehicles would travel if they were the only ones on the road (free flow speed)

**Microscopic Travel Models**:

Good For:
  * Answering a specific question about a particular area
  * Visualizing various alternatives
Knows About:
  * Details about intersections, like: turn lanes, signal timing, stop signs
  * Driver behavior, like: cars moving in flocks (platooning), drivers having to wait for an available space to be able to make turns or change lanes
  * Queues, bottlenecks, and physical constraints
Doesn't Know About:
  * How vehicles route themselves - that all has to be directly input into the model
Data Requirements:
  * Huge level of effort. Every detail matters and it can be very costly to do on a large scale.

### Current Practice: Sequential Approach ###
The current practice is to take the 'number of vehicles' on a street from the _macro_ model and analyze a small sub-area in the _micro_ model.  There are a few problems with this approach, notably that when you look at the nitty gritty details of the _macro_ model, it doesn't make a lot of sense.  For example, it doesn't know anything about left turns being hard at intersection X, so it probably assumes too many people are doing that.  If you directly feed what the macro model estimates into the micro model, you will likely crash the micro model because it knows that there is a limitation on the number of people that can make that left turn.  Thus, in practice, the traffic volumes that are fed into a _micro_ model are "massaged" by a qualified technician until they start to make sense.  This is all fine and dandy until you want to analyze alternatives...then you have to make sure that each subsequent "number massage" is consistent.  This is theoretically possible to do, but difficult in practice.

### Future Practice: Hybrid Approach (AKA DTA) ###
So why not take what the macro model knows about optimal path routing and smoosh that together with all those details that the micro model knows about like signal timing and queues and create a _hybrid_ of the two?  Well, that's what DTA is!  It's a _mesoscopic_ model, so it doesn't do _quite_ as good a job at analyzing the nitty gritty traffic details as the micro model, but heck, its doing it for the whole city!

**Why hasn't somebody done that before? It seems so obvious**

There is a really short answer to this one: computers have gotten faster.

DTA is not a newcomer to the transportation industry or to researchers.  _Actually using DTA_ in practice for a large-scale network is what is new.  We even wrote a [paper about our big plans](http://www.sfcta.org/images/stories/IT/SFCHAMP/PDFs/Xyntarakis,Sall,Hicks,CharltonDRAFT.pdf) that was presented at [www.trb.org TRB] a few years ago.



