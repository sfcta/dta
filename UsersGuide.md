

## Introduction ##

**Important**: These specific directions only work if you have access to the SFCTA Computer Network. You may follow a similar processes to complete runs using the test data or your own data.

The entire process is split into three phases:

  1. Network and demand data processing to prepare it for Dynameq.
  1. Running the DTA model in Dynameq (including setting up a scenario, etc.).
  1. Exporting Dynameq results and processing output.


## Subarea Extraction ##
[Note: Required files needed for subarea extraction -which are the same for all projects- can be found in a folder called `SupportFiles` at Y:\dta\Instructions.]

  1. SUBAREA: You might be able to use previously extracted subareas, but in case you need to extract your own subarea:
    * Copy the `FREEFLOW.NET` from your Champ model run dir into your run dir.
    * Open your network in Cube and draw your subarea: Drawing Layer->Edit Polygon
    * Extract the drawn subarea: Drawing Layer->Polygon Tools->Subarea Extraction, and then give it a name.
> If you want to extract the SF subarea, you may use our previously drawn polygon for `dtaAnyway` subarea:
    * Copy the `FREEFLOW.VPR` file from `SupportFiles` folder into the same location as your `FREEFLOW.NET` file.
    * Go to Cube->Edit Polygon->Restore, choose the `dtaAnyway_subarea` and you'll see the polygon.
    * Extract the subarea: Drawing Layer->Polygon Tools->Subarea Extraction, and then give it a name.

  1. DEMAND: Create a sub-folder named 'demand' in your dir. Copy these two files from `SupportFiles` folder:
    * `DemandProfile.csv` and `DemandProfile_Truck.csv` - If you are working with AM scenarios, you may want to produce your own files, as the current AM `DemandProfile` files we have are based on the counts for the Broadway study area.
    * `subareaExtract{EA,AM,MD,PM,EV}.s` - If ou want to run PM scenario you need MD,PM and EV, and if you want to go for AM scenario you need EA,AM and MD; because for each time period in addition to the main period you also need one period before for warm-up and one period after for cool-down.
    * `createRenumberingMapping.s`
    * `createDemand.bat` - Modify this script accordingly, and run it.

  1. NETWORK: Create a sub-folder named 'network' in your dir. Copy `turns{am,pm,op}.pen` from your Champ model run dir, and copy the followings from the `SupportFiles` folder:
    * `excelSignalCards` folder
    * `movement_override.csv` and `uturnPros.csv`

  1. TRANSIT: Create a sub-folder named 'transit' in your dir. Copy `bus.lin`, `rail.lin` and `muni.lin` from your Champ model run dir.


## Pre-Processing Using Code Base ##
Note: This step requires a computer that has access to Cube/TP Plus in order to export the cube network to text files.

  1. Map the following network drives:
    * `\\files\GIS` maps to   `Q:\`
    * `\\files\Model` maps to `Y:\`
    * `\\castro\data` maps to `X:\`
  1. [Checkout the code base from the google code repository](http://code.google.com/p/dta/source/checkout).
  1. Set the following environment variables. You may want to do this by copying the `importFullSanFranciscoNetworkDataset.bat` from dtaAnyway scripts into your local directory and setting these variables at the top, so that it's obvious what settings were used.
    * **`DTA_CODE_DIR`** should be the file path where the DTA Anyway repository is checked out
    * **`DTA_NET_FILE`** should be the name of the Cube network file
    * **`DTA_NET_DIR`** should be the directory in which the `DTA_NET_FILE` can be found
  1. Run batch file `%DTA_CODE_DIR%\scripts\importFullSanFranciscoNetworkDataset.bat` (use the one with `_AM` at the end for AM run). If the code runs successfully, this phase is complete.

## Setting Up and Running DTA in Dynameq ##

  1. Create new Dynameq scenario
  1. Import network properties
  1. Import demand matrices
  1. Calculate "left\_turn" and "right\_turn" movement attributes.
    1. (This only needs to happen once per project) Project -> Filters,  Domain: Movements.  Click the button `Create...`.  Define `filter_left_turn` as having the Expression `angle>=45 && angle<165`.  Define `filter_right_turn` as having the Expression `angle>=-180 && angle<-45`.
    1. (This only needs to happen once per project) Project -> User Attributes, Domain: Movements.  Click the button `Create...`.  Name the value `left_turn` and make it an integer Data Type.  Ditto for `right_turn`.
    1. Network -> Calculator..., Domain: Movements.  Use the left turn filter to isolate left turns and then calculate `left_turn=1`. Use the right turn filter to isolate right turns and then calculate `right_turn=1`.  Press Enter in the text field to make it take effect; you should get a confirmation dialog.
  1. (This only needs to happen once per project) Project -> Constants...  left\_turn\_pc = 30 and right\_turn\_pc=10 if not already set.
  1. Calculate "fac\_type\_pen" movement attribute.
    1. (This only needs to happen once per project) Project -> Filters,  Domain: Links.  Click the button `Create...`.  Define `LocalOrCollector` as having the Expression `(facility==6)||(facility==7)||(facility==10)`.
    1. (This only needs to happen once per project) Project -> User Attributes, Domain: Links.  Click the button `Create...`.  Name the value `fac_type_pen` and make it an integer Data Type.
    1. Network -> Calculator..., Domain: Links.  Use the Local or Collector filter to isolate local and collector links and then calculate `fac_type_pen=1`. Press Enter in the text field to make it take effect; you should get a confirmation dialog.
  1. Create new DTA with the following specifications.


### DTA Specifications ###

#### Assignment ####

  * Start of demand:	        14:30 (5:30 for AM run)
  * End of demand:		19:30 (10:30 for AM run)
  * End of simulation period:	00:30 (+1 day) (15:30 for AM run)
  * Transit lines simulation:	Yes
  * Re-optimization:		No
  * Re-optimization iteration(s):	0

#### Demand ####

  * Cars
    * class:		Car\_NoToll
    * matrix:		car\_notoll
    * paths:		20
    * intervals:		20
    * types (%):		Car=100,
    * generalized cost:	Expression\_4
    * movement expression:	ptime+(left\_turn\_pc`*`left\_turn)+ (right\_turn\_pc`*`right\_turn)
    * link expression:  fac\_type\_pen`*`(1800`*`length/fspeed)

  * Trucks
    * class:		Truck\_NoToll
    * matrix:		truck\_notoll
    * paths:		20
    * intervals:		20
    * types (%):		Truck=100,
    * generalized cost:	Expression\_4
    * movement expression:	ptime+(left\_turn\_pc`*`left\_turn)+(right\_turn\_pc`*`right\_turn)
    * link expression:		fac\_type\_pen`*`(1800`*`length/fspeed)

#### Control Plans ####

  * excelSignalsToDynameq:	14:30 - 21:30 (5:30 - 12:30 for AM run)

#### Results ####
(see note below about getting it to run faster)
> PM run:
  * Simulation results:	14:30:00 - 00:30:00 (+1 day) -- 00:05:00
  * Lane queue animation:  14:30:00 - 00:30:00 (+1 day) -- 00:05:00
  * Transit results:  14:30:00 - 00:30:00 (+1 day) -- 00:05:00
> AM run:
  * Simulation results:	05:30:00 - 15:30:00 -- 00:05:00
  * Lane queue animation:  05:30:00 - 15:30:00 -- 00:05:00
  * Transit results:  05:30:00 - 15:30:00 -- 00:05:00

#### Advanced ####

  * Traffic generator:		        Conditional
  * Random seed:			1
  * Travel times averaged over:	450 s
  * Path pruning:			0.001
  * MSA reset:			        3
  * Dynamic path search:		No
  * MSA method:			Flow Balancing
  * Effective length factor:		1.00
  * Response time factor:		1.00

#### Options for Reducing RAM and CPU ####

(tip from INRO)
Run the DTA with a single simulation results interval covering the entire five hours of demand.  When the DTA is done, execute the last iteration (DTA -> Execute Last Iteration) and modify the simulation result intervals to something smaller (i.e. 5 min).  Make sure you keep the start time of the simulation results equal to the start of the demand period when you run the DTA.

## DTA Output Processing ##

  1. Export the Network as Dynameq Network Files (Network -> Export -> To Dynameq Network Files). The outputs would be `{%scenario_prefix%}_{scen,base,advn,ctrl,ptrn}.dqt`.
  1. Export the results (Results -> Export -> Link/Movement/Node/Centroid) and select Outflow, Inflow, and Travel Time for both Link and Movement.
  1. Set the environment variable **`%DTA_CODE_DIR%`** to the file path where the DTA Anyway repository is checked out.
  1. Set the environment variable **`%DYNAMEQ_NET_PREFIX%`** to the prefix of the exported Dynameq network files.
  1. Run the code `%DTA_CODE_DIR%\scripts\attachCounts.bat` (use the one with `_AM` at the end for AM run) from the directory with the exported results. This script attach counts from `CountDracula` and should be run on the C drive of Tehama, where `CountDracula` is stored. The outputs would be:
    * Count files: `counts_{links,movements}_{15,60}min_{%time period%}_{recent_midweek,recent,all_midweek,all}.DAT`
    * node/link/movement shape files
  1. Copy a LOS Monitoring file (e.g. `2011_LOS_Monitoring.csv`) into the run directory, and run the code `%DTA_CODE_DIR%\scripts\visualizeDTAResults_corridorPlots.bat` (use the one with `_AM` at the end for AM run) from there. The outputs would be:
    * `AllLink.csv`
    * `Link{15,60}min.csv`
    * `Movement{15,60}.csv`
    * `ObsVsSimulatedRouteTravelTime.csv`
    * A corridor plot for each route (.png file)
  1. Do comparison for volumes and travel time/speed using prepared spreadsheets or come up with your own spreadsheets.