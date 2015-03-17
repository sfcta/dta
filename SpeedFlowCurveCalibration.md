# Introduction #

The speed-flow properties of the DTA model are calibrated to match local traffic flow conditions in San Francisco.  The calibration of DTA Anyway speed-flow properties involved analysis of existing data sources as well as targeted observations.  Observed speed-flow parameters were then incorporated into the DTA model's calibration and validation process.  When the citywide DTA model was run with the full set of observed speed-flow parameters, these parameters resulted in excessive congestion and a gridlocked assignment.  In order to produce a working DTA model some the speed-flow parameters - effective vehicle length and response time in particular - were later relaxed.  This page describes available data resources, data collection efforts, and current speed-flow parameter settings applied in the DTA Anyway model.

In addition to calibrating DTA model parameters to match local traffic flow conditions, the project team sought to better understand how street grade affects traffic flow dynamics.  San Francisco is a famously hilly city and many important streets have percent rises in excess of 10%.  Preliminary calibration and validation showed that the DTA model overestimated traffic on some of the steeper streets in San Francisco. The project team believed that speed-flow properties may differ on such streets and that the model should reflect any differences in traffic behavior due to slope.  The data collection efforts described in subsequent sections of this page explain how data was collected to investigate the impact of slope on traffic flow patterns and how observed differences have been incorporated into model parameter settings.


# Model Parameters #

## Dynameq Representation of Traffic Flow Properties ##

In Dynameq, the fundamental flow-density diagram is approximated in a simplified triangular (piece-wise linear) form. Representing flow as a function of density in each link, the positive slope in the first (increasing) segment is equal to FreeFlow Speed (FFS), where the absolute value of the negative slope in the second (decreasing) segment is equal to the Backwards Wave Speed (BWS).

Three independent variables are required to draw the triangular diagram of flow. This page provides the information on the independent parameters that are chosen, the estimated values for each one of them, the data that is used in order to estimate the parameter, and finally the method by which this estimation is performed.

## Parameter Definitions ##

There are two sets of parameters that can be used for DTA traffic modeling.  The first set of parameters assigns traffic flow properties to streets according to the facility type (FT) and area type (AT) of the road link.  In the second set of parameters traffic flow dynamics also differ by street grade. The street grade parameters are under development.

  * **FreeFlow Speed (FFS):** Free-flow speed is the average speed (mph) that vehicles would travel in the absence of congestion or other adverse conditions, e.g., poor weather, rough street surfaces, etc.
  * **Saturation Flow:** The maximum flow (pcu per hour) that can traverse a segment of street in ideal conditions (no signalization or other obstructions).
  * **Effective Length (EL):** Is the average space (space) that the vehicles occupy on the street when stopped in a queue. The effective length includes the vehicle length and spacing between vehicles.
  * **Jam Density (kj):** The maximum number of vehicles that can queue in a given length of roadway (pcu per mile per lane). Jam density reflects the stationary state of traffic with zero flow.  Jam density is the bottom right corner of the triangular representation of the fundamental traffic flow diagram. Note: kj=1/EL)
  * **Response time (RT):** The average time (seconds) that it takes for vehicles to change speed after a change occurs in the traffic flow state ahead.
  * **Backwards Wave Speed (BWS):** The rate at which downstream changes in traffic flow propagate upstream (mph). Note: BWS=EL/RT

## Traffic Flow Parameters ##

In Dynameq there are default values for EL (=20.40 Ft.) and RT (=1.25 Sec.). These values are not used if user-designated vehicle properties are specified.  In the SF DTA model, vehicle-specific effective length, maximum speed, and response time values are specified for cars, trucks, and various transit vehicles. In addition to vehicle class attributes, unique effective length factors (ELF) and response time factors (RTF) can be chosen for specific links or for an entire project scenario. The effective length factor and response time factor values are multiplied by the values specified for each vehicle using the specified road link.

The parameters that are currently used in the San Francisco DTA model are listed below:

_Vehicle-Specific Length, Speed, and Response Time_
| Effective Length (ft) | 21.0 | 31.5 |
|:----------------------|:-----|:-----|
| Effective Length Factor | 1.0 | 1.0 |
| Maximum Speed (mph) | 100 | 70 |
| Vehicle Type Response Time (s) | 1.0 | 1.25 |
Note: Effective length factor is 1.0 throughout most of San Francisco, but it is currently set to 0.95 in and around the San Francisco CBD (defined as area types zero and one (AT0 & AT1).

_Terrain-Specific Response Time Factors_
| Terrain Type | Response Time Factor |
|:-------------|:---------------------|
| Flat | 1.0 |
| Uphill Street | 1.1 |
| Downhill Street | 0.9 |

_Freeflow Speed_
| FT \ AT |	Regional Core	|	CBD	|	Urban Biz	|	Urban	|
|:--------|:--------------|:----|:----------|:------|
| Alley	|	10	|	10	|	10	|	10	|
| Local	|	18	|	18	|	18	|	15	|
| Collector	|	23	|	23	|	20	|	20	|
| Minor Arterial	|	26	|	26	|	28	|	30	|
| Major Arterial	|	28	|	28	|	30	|	32	|
| Super Arterial	|	30	|	30	|	33	|	36	|
| Fwy-Fwy Connector	|	35	|	40	|	45	|	45	|
| Expressway	|	60	|	65	|	65	|	65	|
| Freeway	|	60	|	65	|	65	|	65	|

_Saturation Flow Rate_
| FT \ AT |	Regional Core	|	CBD	|	Urban Biz	|	Urban	|
|:--------|:--------------|:----|:----------|:------|
| Alley	|	1,342	|	1,342	|	1,342	|	1,342	|
| Local	|	1,760	|	1,760	|	1,760	|	1,633	|
| Collector	|	1,923	|	1,923	|	1,831	|	1,831	|
| Minor Arterial	|	1,999	|	1,999	|	2,044	|	2,084	|
| Major Arterial	|	2,044	|	2,044	|	2,084	|	2,121	|
| Super Arterial	|	2,084	|	2,084	|	2,138	|	1,185	|
| Freeway Ramp	|	2,084	|	2,084	|	2,170	|	1,170	|
| Fwy-Fwy Connector	|	2,170	|	2,239	|	2,296	|	2,296	|
| Expressway	|	2,418	|	2,449	|	2,449	|	2,449	|
| Freeway	|	2,418	|	2,449	|	2,449	|	2,449	|


# Data Resources #

In order to determine appropriate traffic flow parameters for the San Francisco DTA model several data sources were consulted. This section introduces these data sources.

## PeMS ##

Caltrans (PeMS: http://pems.dot.ca.gov/) provides real-time and time-series traffic flow data (count, speed, occupancy, etc.) for a number of freeways and expressways in California. Currently, the real time and time series data from 15 sensors located on 4 freeways in San Francisco subarea are available and have been used in DTA traffic flow parameter estimation for freeways. The extracted data consists of 5-minute resolution, lane-by-lane count and speed records, from May 1st to May 31st, 2012. This data is used to extract the flow-density fundamental diagram parameters for freeways.

## SFMTA Speed Surveys ##

The SFMTA has collected speed data on local, collector and arterial streets over the course of time from 2004 to 2012. The data is collected in the off-peak hours and in normal weather conditions. The observation methodology requires a minimum of 4-second headways between one observed vehicle and the following observed vehicle. This requirement is intended to exclude the effect of leading vehicle speed on the observed vehicle although it is uncertain if four seconds is an adequate spacing to ensure true speed independence. 85th-percentile and 50th-percentile speeds are consulted to estimate the free flow speeds in the San Francisco DTA model for non-freeway facilities.

## SFCTA Flow-Length-Response Surveys ##

The SFCTA conducted surveys of traffic flow behavior to inform the DTA calibration process.  The surveys were designed to record the effective length of vehicles when stopped at red lights (effective length at jam density), the flow rate of vehicles when released from a queue (saturation flow rate), and the response time of drivers to accelerate from a stopped position after the car in front begins to accelerate.  The surveyors also measured the approximate slope of the street, the lane configuration of the intersection, and lane width.  SFCTA staff conducted surveys at nine San Francisco locations in AM and PM peak periods in June 2012.  The observations took place primarily on multiple lane one-way streets where traffic flow behavior would have minimal interference from conflicting turning movements.  The surveys were distributed evenly between flat streets, steep uphill streets and steep downhill streets.  Additional details about the SFCTA Flow-Length-Response Surveys are provided in the Appendix below.

## SFCTA Speed Survey ##

The project team conducted speed surveys on lower order facility type streets to supplement available PeMS and SFMTA speed data which focus primarily on freeways and arterials.  Speed observations were conducted at three locations on one day in June 2012.  More observations were initially planned, but have yet to be carried out.  The survey recorded the speed of every vehicle that passed a mid-block observation point that was a sufficient spacing behind another vehicle to be considered traveling at a free-flow speed.  The minimum spacing was four seconds (in order to match the methodology of the SFMTA speed surveys), but typical spacing was much greater.  Additional details about the SFCTA Speed Survey are provided in the Appendix below.

## Pedestrian Counts ##

The SFMTA's June 2011 "City of San Francisco Pedestrian Count Report" provides 2009 and 2010 pedestrian count data for 50 locations throughout San Francisco.


# Parameter Sources #

This section matches the parameters used for modeling traffic flow on a particular facility type to the data that informed the parameter’s value.  In this section the “assumed” value of a parameter is defined as the value that is applied to the DTA model and the “benchmark” value of a parameter is the observed value in which the modelers have the highest confidence.  The assumed and benchmark values may differ due to rounding or professional judgment.

## Free Flow Speed ##

The assumed free-flow speed parameters for freeways in San Francisco are based on benchmarks from PeMS data.  Free-flow speed benchmarks for arterials are based on the MTA speed surveys.  Free-flow speeds for local and collector streets are based on SFMTA speed surveys, the SFCTA speed survey, and modeler intuition.

## Saturation Flow Rates ##

The assumed saturation flow rates for San Francisco freeways are based on PeMS records.  For surface streets of all facility types the saturation flow rates assumed in the DTA model are based on the SFCTA Flow-Length-Response Surveys.  For facility types that were not directly observed in the SFCTA Flow-Length-Response Surveys, modeler judgment was used to assign intuitive values.

## Jam Density / Effective Vehicle Length ##

The assumed jam density for all facility types is based on observed data from the SFCTA Flow-Length-Response Surveys.  It is assumed that arterial queuing spacing in and around the San Francisco CBD is similar to jam density spacing elsewhere in San Francisco and on other facility types.  It is understood that this assumption may be problematic, but no other empirical data is available for effective car length on other facility types in San Francisco.  The observed effective length values are similar to those used by some consultants and are similar to the default settings in some traffic simulation software packages.

## Response Time / Backwards Wave Speed ##

On freeways the benchmark value for the speed of the backwards wave is derived from PeMS data.  For arterial streets the benchmark is computed using observed response times.  Response times on local and collector streets are assumed to be essentially equivalent to response rates on arterials.  Response time is also the only traffic flow parameter where a significant and meaningful difference across grade categories was observed.



# Appendices #

## PeMS Data Analysis ##

Five-minute-resolution data from 15 sensors in San Francisco area, for 31 days in May 2012, are downloaded for our traffic flow model calibration. There are 59 lanes in our data set. Best fit piece-wise linear (triangular) curves are extracted for each lane; and the three parameters, maximum flow, freeflow speed, and backward wave speed are proposed for each curve (the jam density is assumed from SFCTA survey data to be 220 pcu per mile per lane, which corresponds to an effective vehicle length of 24').

Of 59 reviewed lane records, 26 do not show a triangular pattern. This could be because the observed data may always remain in free flow traffic conditions, or because the observed trends are parabolic, trapezoidal, etc. All of the non-triangular patterns are excluded from further processing. Three lanes have unrealistically large maximum flows (4,344 vphpl or so), therefore these lanes are assumed to have faulty sensors and they are excluded from further data processing. The remaining 30 lanes are used for calibration analysis.

The resulting averages for maximum flow, freeflow speed, and backward wave speed are 2,182 vphpl, 65.22 mph and 10.61 mph respectively. Statistical T-tests indicate that the sample means are representative of the freeways at a 95% confidence level and maximum expected error of +/-102 vphpl for maximum flow, +/-1.98 mph for freeflow speed, and +/-0.71 mph for backward wave speed.

_Parameters from Data Analysis for 30 Caltrans Sensors_
|	Sensor Location	|	Lane	|	Sat. Flow	|	FFS	|	BWS	|
|:----------------|:-----|:----------|:----|:----|
|	Mainline VDS 400043 25th st ped o-c	|	1	|	2436	|	72.94	|	10.87	|
|	Mainline VDS 400043 25th st ped o-c	|	2	|	2148	|	69.57	|	9.79	|
|	Mainline VDS 400255 Bacon St. near San brun	|	1	|	2268	|	75.98	|	8.63	|
|	Mainline VDS 400255 Bacon St. near San brun	|	2	|	2064	|	69.67	|	8.32	|
|	Mainline VDS 400255 Bacon St. near San brun	|	3	|	1920	|	62.67	|	7.94	|
|	Mainline VDS 400255 Bacon St. near San brun	|	4	|	2580	|	64.31	|	11.22	|
|	Mainline VDS 400255 Bacon St. near San brun	|	5	|	2136	|	58.88	|	9.71	|
|	Mainline VDS 400552 S of St. Mary's Ped Xin	|	1	|	2292	|	71.07	|	11.76	|
|	Mainline VDS 400552 S of St. Mary's Ped Xin	|	2	|	2052	|	64.73	|	8.68	|
|	Mainline VDS 400552 S of St. Mary's Ped Xin	|	3	|	2004	|	67.7	|	9.36	|
|	Mainline VDS 400552 S of St. Mary's Ped Xin	|	4	|	1788	|	59.81	|	8.34	|
|	Mainline VDS 400868 25th st ped o-c	|	3	|	2100	|	63.73	|	9.94	|
|	Mainline VDS 400868 25th st ped o-c	|	4	|	1665	|	59.45	|	8.26	|
|	Mainline VDS 401018 Alemany Blvd	|	1	|	1968	|	67.15	|	11.03	|
|	Mainline VDS 401018 Alemany Blvd	|	3	|	2136	|	67.6	|	10.1	|
|	Mainline VDS 401018 Alemany Blvd	|	4	|	2112	|	61.68	|	9.83	|
|	Mainline VDS 401162 harrison st	|	1	|	1728	|	71.3	|	9.99	|
|	Mainline VDS 401162 harrison st	|	2	|	2496	|	70.88	|	15.59	|
|	Mainline VDS 401162 harrison st	|	3	|	2208	|	67.27	|	13.88	|
|	Mainline VDS 401162 harrison st	|	4	|	1812	|	62.32	|	11.15	|
|	Mainline VDS 401371 - west 80 to north 101	|	1	|	2244	|	73.27	|	12.89	|
|	Mainline VDS 401371 - west 80 to north 103	|	3	|	2556	|	63.51	|	15.94	|
|	Mainline VDS 401408 20th Street - Hospital	|	1	|	2280	|	57.27	|	10.71	|
|	Mainline VDS 401408 20th Street - Hospital	|	2	|	2100	|	55.6	|	10.45	|
|	Mainline VDS 401408 20th Street - Hospital	|	3	|	1740	|	59.39	|	8.77	|
|	Mainline VDS 401409 Vermont st-between 23rd	|	1	|	2640	|	67.86	|	10.52	|
|	Mainline VDS 401409 Vermont st-between 23rd	|	2	|	2604	|	59.87	|	11.2	|
|	Mainline VDS 401470 Mission St OC	|	4	|	2424	|	55.23	|	12.13	|
|	Mainline VDS 401516 20th Street - Hospital	|	1	|	2700	|	70.07	|	10.84	|
|	Mainline VDS 401516 20th Street - Hospital	|	4	|	2256	|	65.86	|	10.34	|

Based on these results the freeflow speed for freeways and expressways in the model are set at 65 for the urban (non-CBD) area types. Since the jam density is assumed to 220 pcupmpl in the model, the backward wave is derived to be 11.9 mph so as to maintain a maximum flow rate of 2,200 pcuphpl. The response time factor corresponding to an 11.9 mph backward wave is calculated to be 1.1.  This value is assumed in the model.

## SFMTA Data Analysis ##

Speed surveys provided by the SFMTA for 507 locations in SF were analyzed. For each location the 50th percentile and 85th percentile speeds were recorded.  This information was matched to network locations and associated with the relevant network properties for each location, e.g., FT, AT, slope, etc.  The averages of the 50th percentile speeds for different facility types and area types are presented in the table below.

| Average of 50% Speed (mph)	|	Regional Core	|	CBD	|	Urban Biz	|	Urban	|
|:---------------------------|:--------------|:----|:----------|:------|
| Super Arterial | 29.0 | 27.9 | 33.1 | 36.3 |
| Major Arterial | 25.2 | 25.9 | 29.7 | 30.7 |
| Minor Arterial | 26.7 | 26.3 | 28.4 | 29.5 |
| Collector      |  NA  | 28.5 | 26.1 | 28.2 |
| Local          |  NA  | 22.7 | 27.3 | 25.9 |

| Number of Observations	|	Regional Core	|	CBD	|	Urban Biz	|	Urban	|
|:-----------------------|:--------------|:----|:----------|:------|
| Super Arterial | 2 | 17 | 19 | 31 |
| Major Arterial | 16 | 67 | 46 | 58 |
| Minor Arterial | 6 | 16 | 70 | 42 |
| Collector      | 0 | 2 | 18 | 36 |
| Local          | 0 | 3 | 8 | 44 |

## SFCTA Survey locations, dates, and location profiles ##

SFCTA traffic flow observations were conducted between 6/15 and 6/22/2012 at nine locations in San Francisco.  All nine locations are located in or near San Francisco’s CBD.  Each of these locations are classified to be within area type 0 or 1. The facility types of the observed streets are primarily arterials (FT 7, 12 and 15 indicate different classes of arterial roadways).  At each survey location two measurements of street grade are available.  The measured grade is the approximate grade measured by SFCTA staff in the field.  The network grade is the percent rise field in the SCFTA’s SF-CHAMP network.  This network grade was calculated from topographical shapefiles of San Francisco.  A total of 320 queue dissipations were observed at the nine observation locations.  The tables below provide more detail about the survey activities.

_Observation Locations_
| # | Dir. | Observ. Street | Cross Street | Lanes | FT | AT | Measured Grade | Network Grade |
|:--|:-----|:---------------|:-------------|:------|:---|:---|:---------------|:--------------|
| 1 | NB | Leavenworth | O'Farrell | 3 | 12 | 0 | 11.2% | 11.1% |
| 2 | NB | Leavenworth | Geary | 3 | 12 | 0 | 7.9% | 7.4% |
| 3 | EB | Golden Gate | Franklin | 3 | 7 | 1 | Flat | 0.0% |
| 4 | EB | O'Farrell | Van Ness | 2 | 15 | 1 | -10.0% | -10.3% |
| 5 | NB | Kearny | Bush | 3 | 7 | 0 | Flat | 0.0% |
| 6 | WB | Fell | Buchanan | 4 | 15 | 1 | 5.2% | 9.7% |
| 7 | SB | Hyde | Post | 3 | 12 | 0 | -7.9% | -11.2% |
| 8 | NB | Taylor | Post | 3 | 4 | 0 | 8.5% | 8.3% |
| 9 | NB | Van Ness | Golden Gate | 3 | 7 | 0 | Flat | 0.0% |

_Count of Queue Dissipations Observed_
| # | Dir. | Observ. Street | Cross Street | Queues Observed |
|:--|:-----|:---------------|:-------------|:----------------|
| 1 | NB | Leavenworth | O'Farrell | 28 |
| 2 | NB | Leavenworth | Geary | 20 |
| 3 | EB | Golden Gate | Franklin | 42 |
| 4 | EB | O'Farrell | Van Ness | 42 |
| 5 | NB | Kearny | Bush | 42 |
| 6 | WB | Fell | Buchanan | 42 |
| 7 | SB | Hyde | Post | 42 |
| 8 | NB | Taylor | Post | 20 |
| 9 | NB | Van Ness | Golden Gate | 42 |

_Sample Size, Mean, and Standard Deviation of Effective Length in Different Rise Categories_

|	Slope Category	|	Number of Observations	|	Mean (ft)	|	Standard Deviaion	|
|:---------------|:-----------------------|:----------|:------------------|
|	Down	|	756	|	24.54	|	5.41	|
|	Flat	|	1134	|	24.05	|	5.14	|
|	Up	|	990	|	24.32	|	5.63	|

_Sample Size, Mean, and Standard Deviation of Headway in Different Rise Categories_
|	Slope Category	|	Number of Observations	|	Mean (sec)	|	Standard Deviaion	|
|:---------------|:-----------------------|:-----------|:------------------|
|	Down	|	756	|	2.38	|	0.73	|
|	Flat	|	1125	|	2.57	|	0.91	|
|	Up	|	558	|	2.72	|	0.78	|

_Sample Size, Mean, and Standard Deviation of Response Time in Different Rise Categories_

|	Slope Category	|	Number of Observations	|	Mean (sec)	|	Standard Deviaion	|
|:---------------|:-----------------------|:-----------|:------------------|
| Down |	747	|	1.09	|	0.39	|
| Flat	|	378	|	1.37	|	0.45	|
| Up	|	558	|	1.38	|	0.90	|
