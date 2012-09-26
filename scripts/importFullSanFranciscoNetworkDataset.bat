:: This file should run in an empty directory, all the way through.

:: DTA Anyway code location is required
IF NOT DEFINED DTA_CODE_DIR (
  echo Please set the DTA_CODE_DIR environment variable to the directory where DTA Anyway is installed.
  echo e.g. set DTA_CODE_DIR=Y:\Users\neema\dta
  goto done
)

:: Default to Cube transit networks if not defined
IF NOT DEFINED TRANSIT_IMPORT (
  set TRANSIT_IMPORT=CUBE
)

:: let PYTHON know where to find it
set PYTHONPATH=%DTA_CODE_DIR%

::
:: 1) create the network from the Cube network
::
:convertStaticNetwork
python %DTA_CODE_DIR%\scripts\createSFNetworkFromCubeNetwork.py -n sf_nodes.shp -l sf_links.shp Y:\dta\SanFrancisco\2010\SanFranciscoSubArea_2010.net Y:\dta\SanFrancisco\2010\network\turnspm.pen Q:\GIS\Road\SFCLINES\AttachToCube\stclines.shp
:: primary output: Dynameq files sf_{scen,base,advn,ctrl}.dqt
:: log     output: createSFNetworkFromCubeNetwork.{DEBUG,INFO}.log
:: debug   output: sf_{links,nodes}.shp
IF ERRORLEVEL 1 goto done

::
:: 2) attach the transit lines to the DTA network
:: 
:importTransit
if %TRANSIT_IMPORT% == CUBE (
  python %DTA_CODE_DIR%\scripts\importTPPlusTransitRoutes.py . sf Y:\dta\SanFrancisco\2010\transit\sfmuni.lin Y:\dta\SanFrancisco\2010\transit\bus.lin
  :: primary output: Dynameq files sf_trn_{scen,base,advn,ptrn}.dqt
  :: log     output: importTPPlusTransitRoutes.{DEBUG,INFO}.log
  IF ERRORLEVEL 1 goto done
)
if %TRANSIT_IMPORT% == GTFS (
  set PYTHONPATH=%DTA_CODE_DIR%;Y:\lmz\googletransitdatafeed-read-only\python
  python %DTA_CODE_DIR%\scripts\importGTFS.py -s sf_gtfs_stops.shp -l sf_gtfs_links.shp . sf Y:\dta\SanFrancisco\2010\transit\google_transit_sfmta_20120609_20120914.zip
  :: primary output: Dynameq files sf_trn_{scen,base,adv,ptrn}.dqt
  :: log     output: importGTFS.{DEBUG,INFO}.log
  IF ERRORLEVEL 1 goto done
)


::
:: 3) attach the signal data to the DTA network
:: 
:: This step needs to go after the transit step because the transit step enables all movements for transit (so if there is a transit line
:: turning left at an intersection and the left was prohibited, it will become transit-only.)  That way, the signal validation will make
:: sure that transit gets green time.
::
:importSignals
python %DTA_CODE_DIR%\scripts\importExcelSignals.py . sf_trn Y:\dta\SanFrancisco\2010\network\excelSignalCards 15:30 18:30 Y:\dta\SanFrancisco\2010\network\movement_override.csv Y:\dta\SanFrancisco\2010\network\uturnPros.csv
:: primary output: Dynameq files sf_signals_{scen,base,advn,ctrl}.dqt
:: log     output: importExcelSignals.{DEBUG,INFO}.log
IF ERRORLEVEL 1 goto done

::
:: 4) attach the stop sign data to the DTA network
::
:: This step needs to go after import signals because signals win over stop signs; if a node has a signal, we'll leave it alone.
::
:importStopSigns
python %DTA_CODE_DIR%\scripts\importUnsignalizedIntersections.py . sf_signals Q:\GIS\CityGIS\TrafficControl\StopSigns\stops_signs.shp 
IF ERRORLEVEL 1 goto done
:: primary output: Dynameq files sf_stops_{scen,base,advn,??}.dqt
:: log     output: importUnsignalizedIntersections.{DEBUG,INFO}.log

::
:: 4) create the car demand
::
:createDemand
python %DTA_CODE_DIR%\scripts\importCubeDemand.py -f Y:\dta\SanFrancisco\2010\demand\DemandProfile.csv . sf_stops Car_NoToll demand_Car_NoToll.dat 14:30 19:30 Y:\dta\SanFrancisco\2010\demand\SanFranciscoSubArea_2010_MD.csv 14:30 15:30 01:00 0.13364 Y:\dta\SanFrancisco\2010\demand\SanFranciscoSubArea_2010_PM.csv 15:30 18:30 03:00 1.00 Y:\dta\SanFrancisco\2010\demand\SanFranciscoSubArea_2010_EV.csv 18:30 19:30 01:00 0.22594
IF ERRORLEVEL 1 goto done
:: primary output: demand_Car_NoToll.dat
:: log     output: importCubeDemand.{DEBUG,INFO}.log

:: 5) create the truck demand
::
:createDemand
python %DTA_CODE_DIR%\scripts\importCubeDemand.py -f Y:\dta\SanFrancisco\2010\demand\DemandProfile.csv . sf_stops Truck_NoToll demand_Truck_NoToll.dat 14:30 19:30 Y:\dta\SanFrancisco\2010\demand\SanFranciscoSubArea_2010_MD.csv 14:30 15:30 01:00 0.051282 Y:\dta\SanFrancisco\2010\demand\SanFranciscoSubArea_2010_PM.csv 15:30 18:30 03:00 1.00 Y:\dta\SanFrancisco\2010\demand\SanFranciscoSubArea_2010_EV.csv 18:30 19:30 01:00 0.039216
IF ERRORLEVEL 1 goto done
:: primary output: demand_Truck_NoToll.dat
:: log     output: importCubeDemand.{DEBUG,INFO}.log

:copyFinal
:: THESE are the files to import into dynameq
copy sf_stops_scen.dqt sf_final_scen.dqt
copy sf_stops_base.dqt sf_final_base.dqt
copy sf_stops_advn.dqt sf_final_advn.dqt
copy sf_stops_ctrl.dqt sf_final_ctrl.dqt
copy sf_stops_prio.dqt sf_final_prio.dqt
copy sf_trn_ptrn.dqt   sf_final_ptrn.dqt

:: This is here because countdracula is not typically setup.  Unless you're Lisa. ;)
IF %USERNAME% NEQ Lisa (
  goto done
)
::
:: 5) import the counts into userdata files for Dynameq to read
::
:importCounts
set PYTHONPATH=%DTA_CODE_DIR%;Y:\lmz\CountDracula
python %DTA_CODE_DIR%\scripts\attachCountsFromCountDracula.py -l sf_final_links.shp -m sf_final_movements.shp -n sf_final_nodes.shp . sf_final
IF ERRORLEVEL 1 goto done

:done