# Task 3: Analysis Tools Development #
**Task lead: Lisa Zorn**



## 3.1: Observed Data Management ##
## 3.2: Model component integration scripts ##

This section is more of the 'doing' section of scripts that take data from x and move it to z...and all the required translation and massaging that goes along with that.

### Demand Model to DTA ###
**Background**: The second level of analysis will seek to calibrate the demand models such that trip tables can be fed directly from SF-CHAMP to the DTA without matrix estimation. This one-way flow of information will allow the model to consider changes in destination, mode, time-ofday,
etc, and allow the model to be run for future year and alternative scenarios. This level of analysis represents a significant advance over the current state of practice, although requires further calibration of the demand models to produce reasonable flows without gridlock.


### Translation to Demand Model ###
**Background**: The most sophisticated level of analysis will seek to feed both roadway and transit travel times from the dynamic model back into the demand models. Because the DTA model is for a subarea of the regional model for which demand is determined, it will be necessary to
fuse DTA travel times with those determined from static traffic assignment for the whole region. This raises several difficult issues to be identified and evaluated, among them, the impact of travel times that vary by departure time intervals on the demand models that were
calibrated on “period level” travel times. This is the riskiest approach, but allows for the full benefit of the DTA to be unleashed and the identification of a variety of future research topics.

## 3.3: Output summary, Reporting and Visualization ##
  * Validation Reports
  * Corridor Volume Plots
  * Travel Times between Points