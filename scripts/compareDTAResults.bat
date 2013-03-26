:: Prior to running this script, the user must:
::  1. Run the DTA model in Dynameq
::  2. Export the loaded Dynameq network files: {scenario_prefix}_{scen,base,advn,ctrl,ptrn}.dqt
::  3. Export the link flow files: link_aflowi.dqt, link_aflowo.dqt, link_atime.dqt
::
::  This file should be run in a directory containing these exported results. 

SET DTA_CODE_DIR=C:\work\dta\dta

SET DYNAMEQ_NET_DIR_1=Q:\Model Projects\MarketStreet\BMS\DTA\MarketStreet_2012\ASCII\Results_Base_Scen
SET NET_PREFIX_1=sf_base
SET DYNAMEQ_NET_DIR_2=Q:\Model Projects\MarketStreet\BMS\DTA\MarketStreet_2012\ASCII\Results_BMS_Scen
SET NET_PREFIX_2=sf_base
SET RPT_TIME_STEP=30
SET RPT_START=990
SET RPT_END=1110
SET OUT_FILE=diffs_BMS_430_630pm.csv

:: let PYTHON know where to find DTA code
set PYTHONPATH=%DTA_CODE_DIR%

python %DTA_CODE_DIR%\scripts\compareDTAResults.py %DYNAMEQ_NET_DIR_1% %NET_PREFIX_1% %DYNAMEQ_NET_DIR_2% %NET_PREFIX_2% %RPT_TIME_STEP% %RPT_START% %RPT_END% %OUT_FILE%
IF ERRORLEVEL 1 goto done

