# Short Term #

## Traffic Flow Model ##
  * _Panel_: `The DTA settings currently used appeared to make sense to the panel. It was suggested that futher changes to these settings may be guided by the calibration and sensitivity tests conducted.`
  * Stop-control FFS
  * local-local possibility
    * _Panel_: `For overestimation issue on local streets, imposing twice the free flow time may not be ideal. There might also be an aversion component in addition to the time component. It might be better to try and tweak the traffic flow parameters such as reaction time. This factor could act as a “perception penalty” and could be a function of number of stop signs. Alternatively, a separate facility type for residential low-volume streets could be created. In addition to this, a reaction time factor that includes friction due to pedestrian traffic on such streets could be tested. `
    * _Response_: ` We are creating an "alleyway" Facility Type and fixing stop-controlled link free flow speeds based on new knowledge of how it is used inside the DTA model `
  * Make sure every intersection has control
  * Increase follow-up time for right turn movements
  * Pedestrian RT impedance
    * _Panel_: ` There might be value in developing link/node specific reaction time factors targeted at specific areas in the network which this could be important. They could also be derived in a systematic way by using information on aggregate pedestrian demand within a radius of a node (buffering).  In addition to area type and facility type currently being used to classify the various parameters, there is potential to use a third dimension – “intersection type” that would allow to make targeted improvements.`
  * Slope

## Validation ##
  * Path reasonableness
  * VMT/VHT for whole network (to see if demand is 'missing')

## Generalized Cost ##
  * **Distance Term**
    * _Panel_: `The panel felt that including distance in the generalized cost function might help towards the traffic overestimation issue on local streets. It is probably more applicable for truck traffic than autos.`
    * _Response_: `TODO`

## Demand ##
  * **Smarter demand profile**
    * _Panel_: `The panel thought that the demand carving for a subarea was a non-trivial process and there should be some more focus on that. External geographical information could be preserved and the demand from external stations could be shifted based on the travel time to the model subarea. In addition, a temporal profile at external gateways and in internal zones could be created to avoid a flat or uniform loading profile to the DTA model. Since traffic counts are available, they may be used to create the temporal profile. Alternatively, departure times from the household survey could also be processed to obtain a temporal profile.`
    * _Status_: `The temporal profile has been adjusted based on counts`
  * **Warm start/end**
    * _Panel_: `The panel felt that a longer warm-up period may be needed to improve the accuracy of the simulated traffic in the current modeling period (4:30 – 6:30 PM). This could also incorporate a portion of mid-day demand to create background traffic which would already be present before the model period. Further, there might be some value in simulating the entire 3-hour period (3:30 – 6:30 PM) in the DTA model to facilitate a straightforward comparison to the static model.  `
    * _Status_: `Simulation period has been expanded to incorporate demand from the midday.  Signal timings are continued throughout the simulation.  `
  * make sure we aren't losing demand from discretized trips

## Validation ##
  * Standards
    * _Panel_: `In the collective experience of the panel members, it was felt that there may not be any validation standards that are broadly accepted and also there may be no national benchmark for root mean squared error (RMSE) of flows and speeds. The panel thought the reason for this may be the limited number of studies currently existing in the DTA arena and different limitations being associated with various DTA packages used in these studies.  The panel members recommended that regular Caltrans static validation standards could be used as a starting point and then extended for more refined time periods. It was noted here again that a 3-hour validation period would facilitate a more direct comparison with the static model. The panel members also stressed on the consistency of reporting structure that needs to be maintained for such a comparison.`
  * Stability
    * _Panel_: `The panel noted that specific value of relative gap may not be as important as the stability of the gap.  Maximums and minimums of traffic characteristics such as speeds may be checked to see if those have stabilized over iterations. It might also help to look at variation in VMT and VHT as additional measures of stability.`
  * Conflicting Data
    * _Panel_: `The general response of the panel to this was to obtain more data so that more cross-checking can be done. The panel felt more observed traffic data on local streets would be useful for validation given that there appears to be considerable overestimation of traffic. Expanding the number of observed traffic count locations was also offered as a long term consideration. The panel felt that the current number of 200 locations may be too less for a city the size of San Francisco. The panel noted that there are 400 count locations in the SACOG area for a population of about a million people and that counts should be geographically distributed and not correlated.`

## Network Coding ##
  * Bus lane coding
    * _Panel_: `The modeling team described a method of splitting a bus-lane link and making one-half of the link right-turn only to deal with bus lanes in the model. The panel suggests that targeted reaction time factors adjustments could potentially be used to accommodate more throughput going through the general purpose lanes and better represent the traffic flow on these lanes.`
    * _Response_: `TODO`


## Sensitivity Tests ##
  * _Panel_: `To aid calibration and validation, more sensitivity tests need to be conducted from the perspective of future and alternative policy scenarios. It might help to devise some future scenarios tests and targeted policy tests. Since SFCTA already has an idea about the initial policies that it would like to use this model for, it might be useful to build some tests around them and evaluate the results qualitatively first. Sensitivity tests on both demand and traffic flow parameters would help understand which parameters affect to what extent which in turn could help identify the parameters that need to be focused on.`
  * _Response_: `ongoing work`
  * Traffic flow parameters
    * _Panel_: `In addition, the panel recommended conducting sensitivity tests around traffic flow parameters such as jam density and also flow averaging parameters. Since sensitivity is contextual, the panel suggested analyzing if the ranking of investments might change due to certain changes in these parameters. Based on which parameters affect the ranking of investments to what extent, the modeling team may be able to focus more on those parameters during calibration and validation.`
    * _Response_: `ongoing work`
    * _Question_: `How sensitive should the model be to these settings? `
    * _Panel_: `The panel thought that there are no standards as to how sensitive a model is to the DTA settings since the sensitivity might be dependent on the DTA package being used and modeling assumptions made in them.`
  * Random number seed
  * Network Changes
    * _Panel_: `The panel offered various methods to check the model’s sensitivity to network changes. At first, it was suggested that progression of traffic on major arterials be confirmed. Another basic test would be to visually inspect the relevant paths for reasonableness. Finally, the panel recommended examining areas in the network that are specifically affected by bottlenecks and queues. These are the areas where static model would be significantly inaccurate in predicting the traffic flow patterns.  `

## Demand ##
  * Overlay demand?
  * More geographically consistent representation of external stations
  * Bucket Rounding
    * _Panel_: ` The panel mentioned that rounding of fractional trips may also be a source of issues in traffic prediction. Even if there are no trips lost in total, there may be significant loss of trips in specific zones. The panel recommended that bucket rounding be used over arithmetic rounding. `
    * _Response_: ` Implemented `


# Longer Term #

## Data ##
  * _Panel_: `There does not seem to be enough traffic counts data available. Counts from 200 locations are not sufficient for a city of this size. SACOG area with about a million people uses counts from about 400 locations. Counts should be geographically distributed and not correlated.`
  * _Response_: ` The TA is actively putting more counts in our validation database TODO- put in quantity `
  * _Panel_: `Aerial photos could be used for estimating traffic flow parameters such as effective length. This could be helpful especially for freeways since effective length derived from data collected on local and arterial streets is currently being used for freeways.`
  * _Response_: `TODO: Confirm if this is actually the case...I believe we used PeMS`
  * _Panel_: `More data on local streets would also be useful since there does not seem to be a clear picture of what is going on there. It is possible that all the traffic volumes being simulated on local streets by the DTA model are actually in there but is not being supported by the limited data currently available. `
  * _Response_: ` The TA is actively putting more counts in our validation database - targeting local streets`
  * _Panel_: `GPS information could be used to develop trip tables further down the road.`
  * _Response_: ` Need Clarification `


## Integration ##
  * ABM ==> DTA
    * _Panel_: ` The distinction between parking location and activity location may need to be made in the longer term. This might not be important during the initial phase but will probably be essential during the evaluation of various congestion pricing policies.`
    * _Response_: ` The TA has previous work on this topic and was awaiting appropriate data.  They plan to pursue this as time/budget allows `
    * _Panel_: ` Market segmentation of the demand being passed on to the DTA model could be refined further to include VOT. There will possibly be run time implications of this step. `
    * _Response_: ` Right now this toll/no-toll choice happens in the AB model based on a distributed value of time.  In the long term, the TA will look to DTA to help make this decision `
    * _Panel_: ` The panel recommends that reliability be only considered after model linkage has been well established at a reasonable level of temporal detail.  `
  * DTA ==> ABM
    * _Panel_: ` As a first step, the modeling team could work on developing a hybrid approach that combines static skims regionally and DTA skims locally to be fed back into ABM. `
    * _Panel_: ` The DTA model could eventually be temporally expanded to simulate a full day full day. It may be better to prefer temporal over spatial detail while increasing the scope and sophistication of the model. `
    * _Panel_: ` A fully disaggregate DTA-ABM integration could then be considered which would require significant amount of restructuring to both ABM (SF-CHAMP) and the DTA model. `
    * _Panel_: ` A regional level DTA model might involve a lot of work and may even be unnecessary. `
  * SF-CHAMP
    * _Panel_: ` The temporal resolution of SF-CHAMP could be increased from the current 5 time periods. Again, it may be better to give priority to adding temporal detail to SF-CHAMP before spatial detail. `
    * _Panel_: ` Changes to the resolution of skims would probably require a number of changes to other model components in SF-CHAMP such as tour time of day and trip departure time models. `
  * Transit
    * _Panel_: ` The panel recommends that only after adding temporal and spatial detail to the model should SFCTA consider transit DTA using packages like FAST-TrIPs.`