

# Introduction #

Please enter any new runs in the format below.

## Runs ##

### sf\_jun7\_530p ###
  * Calibration run 1!
  * Convergence: Min = 0.01451, Max = 0.01809, Mean = 0.01687
  * No waiting vehicles at the end of simulation

### sf\_jun8\_420p ###
  * Changes from last run: fixes to a handful of signals that were probably causing issues; upped the freeflow speed on freeways
  * No waiting vehicles at the end of simulation

### sf\_jun18\_630p ###
  * Changes from last run: Transit Lanes ([Issue 83](https://code.google.com/p/dta/issues/detail?id=83)), many stop signs added (See Comment 23 on [Issue 35](https://code.google.com/p/dta/issues/detail?id=35))
  * Convergence: Min = 0.02675, Max = 0.01313, Mean = 0.02821
  * Runtime: 20 hours for 50 iterations
  * No waiting vehicles at the end of simulation

### pb\_jun27\_530p ###
  * Changes from last run:
    * Wrap in changes from codes and network
    * Decrease response time factors from 1.15 to 1.05
    * Run on PB machine
  * Convergence: Min = 0.02915, Max = 0.1139, Mean = 0.0708
  * Runtime: Approx. 15 hours to do 45 iterations
  * RMSE:
  * GEH:
  * Overall Vol/Count Ratio:
  * Observed Gridlock: A few NW of Market street and at SE entry point to the network, similar to previous run.
  * Link to Validation Spreadsheet:
  * Observations: Looks like gridlock is still being caused by capacities that are too low in these areas.  Reducing the response time factor helped, but not enough.  The next thing to test will be undoing some of the larger speed decreases.

### pb\_jul2\_400p ###
  * Changes from last run:
    * Wrap in changes from codes and network
    * Make sure the turn penalties are calculated correctly
    * Set trips to Cars and Trucks (not Generic)
  * Convergence: Min = 0.0124001, Max = 0.0741798, Mean = 0.0377371
  * Runtime: Approx. 12.28 hours to do 50 iterations
  * RMSE: Links = 131 (57%), Movements = 64 (80%)
  * GEH: Links = 7.12, Movements = 4.55
  * Overall Vol/Count Ratio: Links = 0.6604, Movements = 0.7174
  * Observed Gridlock: Entry point in SW corner of the region, Monterey Blvd near I-280, a couple of areas along Hwy 101 have a small amount of gridlock.
  * Link to Validation Spreadsheet:
  * Observations: We definitely need to update the code so that boundary connectors don't connect to ramps and so that the number of lanes on boundary connectors is the sum of the incoming or outgoing lanes.  Still should maybe be seeing more traffic at entry points to I-80.

### pb\_july3\_500p ###
  * Changes from last run:
    * Centoid connectors at boundaries now can't connect to freeways or ramps, and the number of lanes is equal to the sum of the incoming or outgoing lanes.
  * Convergence: Min = 0.0131095, Max = 0.0448661, Mean = 0.0303312
  * Runtime: Approx. 12.46 hours to do 50 iterations
  * RMSE: Links = 130 (56%), Movements = 63 (79%)
  * GEH: Links = 7.05, Movements = 4.56
  * Overall Vol/Count Ratio: Links = 0.6729, Movements = 0.7238
  * Observed Gridlock: Some gridlock on streets intersecting with I-80.
  * Link to Validation Spreadsheet:
  * Observations: Left and right turns seem to be lower than other movements.  We should see if lowering the turn penalties a little bit helps us match the movement counts better.

### pb\_july4\_330p ###
  * Changes from last run:
    * Turn penalties changed: lt\_pc = 20, rt\_pc=5.
  * Convergence: Min = 0.0145885, Max = 0.0416506, Mean = 0.0291377
  * Runtime: Approx. 16.33 hours to do 60 iterations
  * RMSE: Links = 135 (59%), Movements = 67 (84%)
  * GEH: Links = 7.45, Movements = 4.72
  * Overall Vol/Count Ratio: Links = 0.6459, Movements = 0.6811
  * Observed Gridlock: None. Some congestion along Hwy 101 NB and I-80 WB.
  * Link to Validation Spreadsheet:
  * Observations: This definitely made our matching of both link and movement counts worse.  Next run we'll go back to 30 and 10 for the penalties. Matching is worst on FT 4, 5, and 6 for links and FT 7 for movements.  Maybe check and see if those speeds should be lowered slightly or response time should be changed.

### pb\_july5\_500p\_I ###
  * Changes from last run:
    * Added intrazonal trips back in (only about 1,000 total)
  * Convergence: Min = 0.0107243, Max = 0.0459835, Mean = 0.0298107
  * Runtime: Approx. 13.81 hours to do 55 iterations
  * RMSE: Links = 130 (57%), Movements = 63 (79%)
  * GEH: Links = 7.04, Movements = 4.56
  * Overall Vol/Count Ratio: Links = 0.6686, Movements = 0.7230
  * Observed Gridlock: None.  There is congestion but no observed gridlock.
  * Link to Validation Spreadsheet: [July 5 Intrazonal Model vs. Counts (60 min)](http://dta.googlecode.com/files/ModelVsCount_pb_july5_500p_I_60min_v1.xlsx/), [July 5 Intrazonal Model vs. Counts (15 min)](http://dta.googlecode.com/files/ModelVsCount_pb_july5_500p_I_15min_v1.xlsx/), [July 5 Intrazonal Static vs. DTA](http://dta.googlecode.com/files/11RoadwayValidation_pb_july5_I_v1.xls/)
  * Observations: This change only slightly improves the count matching.  This is because there aren't a lot of intrazonal trips in the Cube trip tables, and the trips that are there are often fractional.  These fractional trips are, in many cases, small enough that their effect doesn't show up when the trip tables are truncated as they're imported into Dynameq.
!! Important: This run included a problem with the code.  It was replacing the existing trips between the zones with the intrazonal trips.  I've fixed this problem, and I'll run a new assignment today.  It still shouldn't make a big difference (only about 3,000 trips), but we'll see.

### pb\_july5\_500p\_S ###
  * Changes from last run:
    * Made two-way stops with FT conflicts All-way
    * This does not include the intrazonal trips
  * Convergence: Min = 0.012036, Max = 0.0496103, Mean = 0.0314793
  * Runtime: Approx. 13.96 hours to do 55 iterations
  * RMSE: Links = 130 (56%), Movements = 63 (79%)
  * GEH: Links = 7.04, Movements = 4.58
  * Overall Vol/Count Ratio: Links = 0.6729, Movements = 0.7238
  * Observed Gridlock: None.  There is congestion but no observed gridlock.
  * Link to Validation Spreadsheet: [July 5 All Stops Model vs. Counts (60 min)](http://dta.googlecode.com/files/ModelVsCount_pb_july5_500p_S_60min_v1.xlsx/), [July 5 All Stops Model vs. Counts (15 min)](http://dta.googlecode.com/files/ModelVsCount_pb_july5_500p_S_15min_v1.xlsx/), [July 5 All Stops Static vs. DTA](http://dta.googlecode.com/files/11RoadwayValidation_pb_july5_S_v1.xls/)
  * Observations: This makes some difference, but we may see larger differences in the SF results based on how Lisa implemented the change.  This run also does not include the updates to the connector codes that Lisa made or the changes to the counts.  Those changes will all be wrapped in to the tests run over the weekend.  Several detailed issues were observed:
    1. Some of the worst offenders in the network are volumes that are much too low on Sunset, Great Highway, and Embarcadero.  It looks like there is not enough congestion in the rest of the network to push people out of their way to use these facilities.
    1. Counts that are intended for the Geary Tunnel are instead showing up on the adjacent surface street, where the volumes are in reality much lower.  We should clean this up by moving the count, and our model will do better at this particular location.
    1. At 4th & Harrison and 4th & Folsom, the all-red time is 24s.  This can be traced back to the signal card where there are long pedestrian phases.  Is that really right?  Maybe it could be because of the convention center, but it seems excessive.
    1. There is hourly count of 102 vehicles on Folsom St (links 16160).  This looks like we're missing a zero.
    1. The volumes on Turk are too high, whereas we tend to be low on Geary and Oak/Fell.  Turk is coded as a major arterial.  Seems like we may want to classify it as a minor arterial instead to get somewhat less flow.
    1. The volume is too high on Claremont St.  It looks like people may be too willing to drive over the hill.
    1. The volume is too high on Taraval St.  Not sure why this is.
    1. At Octavia and Mission, there is a U-Turn permitted.  There is also only one through lane on Octavia, whereas there should be two (perhaps because the U-turn is blocking it).  Add to the U-Turn prohibitions list.
    1. There are permitted movements (U-Turns and left turns) on Octavia that should not be permitted.  Clean these up.
    1. There are some signals that don't import cleanly on Octavia due to the complexity of the intersections with the side right turn/parking lanes.  As a result, one is showing up as a TWSC and one is showing up as uncontrolled.

### pb\_july6\_1200p ###
  * Changes from last run:
    * Fixed the issue with the intrazonal trips code.
  * Convergence: Min = 0.0110936, Max = 0.0365741, Mean = 0.02541
  * Runtime: Approx. 13.84 hours to do 55 iterations
  * RMSE: Links = 133 (58%), Movements = 64 (80%)
  * GEH: Links = 7.17, Movements = 4.59
  * Overall Vol/Count Ratio: Links = 0.6527, Movements = 0.7145
  * Observed Gridlock:
    * The Embarcadero between Howard & Folsom
  * Link to Validation Spreadsheet: [July 6 Intrazonal Reports](http://dta.googlecode.com/files/July6_1200p_Intrazonal.zip/)
  * Observations:
    1. It may look like our count-matching is worse, but this is because of the new counts added in, not because of the model.
    1. The intrazonal trips and all-way stops don't make a lot of difference.  We will have to see if some of the capacity changes that Neema and Dan have been working on will give more improvement.
    1. There's something wrong with how Embarcadero & Folsom's signal card is being read in.  The 38s phase should have both NB and SB Embarcadero, but it only has NB.  I'll look into how we might be able to fix this.

### pb\_july6\_430p ###
  * Changes from last run:
    * Neema's updates to the response time factors
  * Convergence: Min = 0.0116106, Max = 0.0673996, Mean = 0.0331219
  * Runtime: Approx. 17.61 hours to do 75 iterations (trying to get better convergence)
  * RMSE: Links = 132 (57%), Movements = 64 (80%)
  * GEH: Links = 7.04, Movements = 4.56
  * Overall Vol/Count Ratio: Links = 0.6467, Movements = 0.7051
  * Observed Gridlock:
    * Stockton Tunnel/Stockton (same congestion as seen before in this area where the tunnel comes out and one lane becomes transit only.
    * Market St. near Stockton
    * I-280 NB @ Brannan
    * Portola @ Sloat
    * Harrison between 3rd & 4th St
    * The Embarcadero between Howard & Folsom
  * Link to Validation Spreadsheet: [July 6 New Capacity Model vs. Counts (60 min)](http://dta.googlecode.com/files/ModelVsCount_pb_july6_430p_60min_v1.xlsx/), [July 6 New Capacity Model vs. Counts (15 min)](http://dta.googlecode.com/files/ModelVsCount_pb_july6_430p_15min_v1.xlsx/), [July 6 New Capacity Static vs. DTA](http://dta.googlecode.com/files/11RoadwayValidation_pb_july6_I_v1.xls/)
  * Observations:
    1. Still ~ 1050 cars waiting at the end of the simulation.  Centroids with waiting vehicles at the end are all in NE area.  These capacities may be lowered too much by the most recent change.
    1. Seeing a lot of new gridlock in the NE region.  I assume this is because of the capacity changes.  We may need to decrease the response time factor a bit (possibly down to 1.20).

### pb\_july9\_400p\_BL ###
  * Changes from last run:
    * Removed bus lanes and updated signal timings with code fix
  * Convergence: Min = 0.0100908, Max = 0.0361953, Mean = 0.0252914
  * Runtime: Approx. 15.66 hours to do 60 iterations
  * RMSE: Links = 135 (59%), Movements = 64 (80%)
  * GEH: Links = 7.32, Movements = 4.59
  * Overall Vol/Count Ratio: Links = 0.6459, Movements = 0.7085
  * Observed Gridlock: None
  * Link to Validation Spreadsheet: [July 9 No Bus Lanes Reports](http://dta.googlecode.com/files/pb_july9_400p_BL_Reports.zip/),[July 9 No Bus Lanes Travel Times](http://dta.googlecode.com/files/ObsVsSimulatedRouteTravelTimes_pb_july9_400p_BL.xlsx/)
  * Observations:
    1. Congestion on 6th St between Bryant & Harrison - both signals are correct, so there must be some other issue here.
    1. Without the bus lanes, the max. delay in Stockton Tunnel is about 1.5 minutes, much less than before.
    1. There is still some congestion on the arterials around Market St., and I-80 in the NE region, but not nearly as much as before.
    1. Flow in the western region is still concentrated mostly on 19th Ave.  We need to figure out why we're not getting much flow on Great Hwy or Sunset Blvd.

### pb\_july9\_500p\_CBD ###
  * Changes from last run:
    * Bus lanes in, but speeds in CBD increased to match AT1 and response time factor decreased from 1.25 to 1.2 for non-freeway links
  * Convergence: Min = 0.00985006, Max = 0.0374433, Mean = 0.0231557
  * Runtime: Approx. 13.06 hours to do 60 iterations
  * RMSE: Links = 137 (59%), Movements = 65 (81%)
  * GEH: Links = 7.40, Movements = 4.62
  * Overall Vol/Count Ratio: Links = 0.6345, Movements = 0.713
  * Observed Gridlock:
    * Market St starting around 4th St.
    * Stockton Tunnel
    * California around Kearny
    * Battery St. & Clay St. around where they intersect (checked signal, and timing is correct)
    * Mason & Columbus around where they intersect (checked signal, and timing is correct)
    * Laguna & Market where they intersect (signal timing is correct)
  * Link to Validation Spreadsheet: [July 9 Change to CBD speeds Reports](http://dta.googlecode.com/files/pb_july9_500p_CBD_Reports.zip/),
  * Observations:
    1. We still get huge amounts of congestion in the CBD. Since changing the speeds and response time factor didn't help much, it looks like fixing the transit-only lane issues is more important.
    1. At the end of the simulation (at 21:30) there were still 1850 vehicles waiting.  This much gridlock is definitely causing our flows to be too low.
    1. At least half of these gridlocked areas are around bus-only lanes that could be causing congestion.  Others are areas that are fed by congestion from other bus-only problems (like Market & 4th having residual problems from the Stockton St. congestion after the tunnel).
    1. Next step will be to figure out how to deal with the bus-only lane issues, decide if we want to keep these speed and response time factor changes, and increase the demand by 25% - 30% to see if that helps us match the counts.

### pb\_july10\_500p\_30D ###
  * Changes from last run:
    * No Bus lanes, includes the changes in the CBD speeds and response time factors
    * Main change is that internal demand was increased by 30%
  * Convergence: Min = 0.0112683, Max = 0.0645339, Mean = 0.0325649
  * Runtime: Approx. 13.51 hours to do 60 iterations
  * RMSE: Links = 155 (68%), Movements = 72 (90%)
  * GEH: Links = 8.18, Movements = 4.86
  * Overall Vol/Count Ratio: Links = 0.6316, Movements = 0.7526
  * Observed Gridlock: Pretty much everywhere.  There are way too many places to list
  * Link to Validation Spreadsheet: [July 10 Increasing demand by 30% Reports](http://dta.googlecode.com/files/pb_july10_500p_30Demand_Reports.zip/),
  * Observations:
    1. We seem to be doing a better job of matching counts here until about 5:30, at which point the gridlock starts and our modeled flows have a huge drop.
    1. This definitely overloads the network, but even with gridlock, we are doing a better job of matching the movement counts than before.  The next step might be to try an increase of just 10%.
    1. We've never seen gridlock on the freeways before, but here we get significant amounts of gridlock on most of them, driving the modeled flow way down.

### pb\_july11\_1000a\_10D ###
  * Changes from last run:
    * Internal demand was increased by 10%
  * Convergence: Min = 0.0105004, Max = 0.0479881, Mean = 0.0276245
  * Runtime: Approx. 14.85 hours to do 60 iterations
  * RMSE: Links = 131 (57%), Movements = 64 (80%)
  * GEH: Links = 7.00, Movements = 4.52
  * Overall Vol/Count Ratio: Links = 0.6948, Movements = 0.7668
  * Observed Gridlock: None.  There is congestion in some areas but no gridlock.
  * Link to Validation Spreadsheet: [July 11 Increasing demand by 10% Reports](http://dta.googlecode.com/files/pb_july11_1000a_10Demand_Reports.zip/), [July 11 Increasing demand by 10% Travel Times](http://dta.googlecode.com/files/ObsVsSimulatedRouteTravelTimes_pb_july11_1000a_10D.xlsx/)
  * Observations:
    1. Increasing demand by 10% instead of 30% allows us to get closer to the counts without overloading the network.  It does lead to more congestion in the CBD, but not gridlock.
    1. We'll see how penalizing the locals and collectors affects the results in the next test.  It's possible that a combination of the two would get us closer to the flows that we're looking for.
    1. We're still seeing a lot of congestion on 6th St. around I-80.  Is this congestion there in real life, or is there something going on in the network that we need to look at?

### pb\_july11\_300p\_FT ###
  * Changes from last run:
    * Locals and collectors were penalized by 1\*FFTime
  * Convergence: Min = 0.00730297, Max = 0.0535901, Mean = 0.0324052
  * Runtime: Approx. 14.19 hours to do 60 iterations
  * RMSE: Links = 122 (53%), Movements = 61 (76%)
  * GEH: Links = 6.85, Movements = 4.47
  * Overall Vol/Count Ratio: Links = 0.8074, Movements = 0.855
  * Observed Gridlock: None.  There is congestion in some areas but no gridlock.
  * Link to Validation Spreadsheets:  [July 11 Penalizing collectors and locals Reports](http://dta.googlecode.com/files/pb_july11_300p_FT_Reports.zip/), [Speed Comparison](http://dta.googlecode.com/files/ObsVsSimulatedRouteTravelTimes_pb_july11_300p_FT.xlsx/)
  * Observations:
    1. These results look much better than what we've seen before.  We're matching counts even better than we did by increasing demand by 10%.
    1. Arterial Plus is still the one facility type where we are really low.  We might want to consider changing the properties of those ones somehow to increase flow.  I'm not sure if we need to decrease speed to slow them down or add capacity to attract more vehicles.  We can look into that next week.
    1. This test still has no bus-only lanes.  Things may change a lot when we add them back in with the right-turns.  I think that will be the next test that we need to do.

### pb\_july19\_830p ###
  * Changes from last run:
    * Network changes (mostly Octavia)
    * Signal changes (yellow time)
    * Bigger transit vehicles
  * Convergence: Min = 0.00776709, Max = 0.05473, Mean = 0.0345985
  * Runtime: Approx. 14.16 hours to do 60 iterations
  * RMSE: Links = 52% (1,748 counts), Movements = 72% (7,643 counts)
  * GEH: Links = 6.63, Movements = 4.34
  * VMT = 1,523,412 miles, VHT (4-6pm) = 66,768 hours
  * Overall Vol/Count Ratio: Links = 0.8019, Movements = 0.8569
  * Observed Gridlock: None.  There is congestion in some areas but no gridlock.
  * Link to Validation Spreadsheets:  [July 19 Network and Signal Changes Reports](http://dta.googlecode.com/files/pb_july19_830p_Reports.zip/)
  * Observations:
    1. These results, on most measures, are better than what we had in the last test with the local and collector penalties.
    1. There is more congestion than we've seen before on the Market St. crossings, especially those that feed into and off of I-80.
    1. Octavia definitely has more traffic than before, probably because the all-way stops were preventing vehicles from using Octavia in previous tests.
    1. Speed matching is better in terms of slope and percent difference, but the RMSE is slightly higher.

### pb\_july31\_900a ###
  * Changes from last run:
    * Input trip tables were in 30-min slices, not the whole 3 hours.
  * Convergence: Min = 0.00754429, Max = 0.0869174, Mean = 0.0507424
  * Runtime: Approx. 14.53 hours to do 60 iterations
  * RMSE: Links = 54% (1,748 counts), Movements = 74% (7,643 counts)
  * GEH: Links = 6.75, Movements = 4.34
  * VMT = 1,524,309 miles, VHT (4-6pm) = 71,785 hours
  * Overall Vol/Count Ratio: Links = 0.7777, Movements = 0.8441
  * Observed Gridlock: None.  There is congestion in some areas but no gridlock.
  * Link to Validation Spreadsheets:  [July 31 Trip Table Slicing Reports](http://dta.googlecode.com/files/pb_july31_Reports.zip/)
  * Observations:
    1. Unfortunately, the slices do seem to have a significant effect on the flows.  This is because having the trip tables input in 30-minute slices seems to cause a shift (about 600 trips total) from 5-6pm to 4-5pm.
    1. We should be able to control the effects of these changes somewhat by applying our own demand profile in the future, but we do want to see less variation between time periods from the bucket rounding if possible.
    1. One of the biggest changes we see is in travel times.  When you look at just 4-5 vs. 5-6, the VHT changes a lot from the previous test.  The demand profile obviously has significant effects on the flows, but we need to make sure that we can set it to what we want instead of allowing the changes that happen as a result of the Dynameq bucket rounding.

### pb\_aug1\_230p ###
  * Changes from last run:
    * 25% of PM demand added to start and end of demand period (14:30-15:30 and 18:30-19:30)
    * Signals updated so that overlapping yellow/green has yellow time
  * Convergence: Min = 0.00619515, Max = 0.0936764, Mean = 0.0483475
  * Runtime: Approx. 21.51 hours to do 65 iterations (needed more iterations to reach stable convergence)
  * RMSE: Links = 56% (1,748 counts), Movements = 78% (7,643 counts)
  * GEH: Links = 7.34, Movements = 4.57
  * VMT = 1,332,327 miles, VHT (3:30-6:30pm) = 53,093 hours
  * Overall Vol/Count Ratio: Links = 0.7112, Movements = 0.773
  * Observed Gridlock: Gridlock in many places in the CBD.  Most of the gridlock develops after the simulation period during the 6:30-7:30 hour, but it doesn't clear as the simulation ends.
  * Link to Validation Spreadsheets:  [Aug 1 Extended Demand Time Reports](http://dta.googlecode.com/files/pb_aug1_Reports.zip/)
  * Observations:
    1. This actually seems to make things worse.  One of the issues is that we're not sure how much demand to add to the start and end hours.  We also need to look at how much the bucket rounding is re-distributing these trips.
    1. We're not clearing out the demand from the network, but one of the reasons that this may be happening is the addition of starting all-red time to signal phases where it exists.  Before the signals timing just started wherever the green time started.
    1. Next two runs will be testing the new speeds that Neema uploaded both with and without the additional hours of demand.
    1. The pems data that I'm using to estimate the demand profile can also give a better idea of how much demand we should be adding to the start and end hours (in terms of the % of the PM demand).
    1. This test did take more iterations to converge to a stable point than other tests have.  That may be another consideration in terms of running time.  To reach stable convergence, this simulation took 21 hours, but we also may be able to shorten that when we go back to the simpler generalized cost expression.

### pb\_aug3\_330p\_NS ###
  * Changes from last run:
    * Neema's speed updates
    * Demand back to 15:30-18:30 (extended demand used in next test)
  * Convergence: Min = 0.00850662, Max = 0.0477658, Mean = 0.0302559
  * Runtime: Approx. 14.62 hours to do 60 iterations
  * RMSE: Links = 52% (1,748 counts), Movements = 73% (7,643 counts)
  * GEH: Links = 6.31, Movements = 4.22
  * VMT = 1,436,086 miles, VHT (3:30-6:30pm) = 64,728 hours
  * Overall Vol/Count Ratio: Links = 0.7312, Movements = 0.7915
  * Observed Gridlock: None.  Congestion in the CBD, but no gridlock.
  * Link to Validation Spreadsheets:  [Aug 3 New Speeds Reports](http://dta.googlecode.com/files/pb_aug3_NwSpd_Reports.zip/)
  * Observations:
    1. We don't get the same boost in count-matching that we did from penalizing the collectors, and locals.  However, we do get closer than we were before the speed changes.
    1. We see congestion where it is expected: the major roadways crossing Market to get to the freeway and clustered around freeway on and off-ramps.
    1. We may want to introduce the local-local facility type or the distance measure in the generalized cost to further penalize the use of very small local streets - especially those South of the park in the Western region pulling traffic from Sunset and 19th.

### pb\_aug3\_430p\_DE ###
  * Changes from last run:
    * Demand extended to 14:30-19:30 with 15% of PM demand added as start and end hours
  * Convergence: Min = 0.00648877, Max = 0.0696583, Mean = 0.0339798 (Converged to gridlock)
  * Runtime: Approx. 19.14 hours to do 60 iterations
  * RMSE: Links = 53% (1,748 counts), Movements = 74% (7,643 counts)
  * GEH: Links = 6.39, Movements = 4.27
  * VMT = 1,431,466 miles, VHT (3:30-6:30pm) = 66,695 hours
  * Overall Vol/Count Ratio: Links = 0.7203, Movements = 0.7241
  * Observed Gridlock: All over the CBD after about 6:00.  Starts mostly E of Stockton and N of market then branches West along Broadway and California.  After 6:30 it seems to reach a critical point and everything becomes gridlocked.
  * Link to Validation Spreadsheets:  [Aug 3 New Speeds with Extended Demand Reports](http://dta.googlecode.com/files/pb_aug3_DE_Reports.zip/)
  * Observations:
    1. Even adding only 15% of the PM demand seems to really overload the network.  This isn't something that will be fixed with the demand profile.  The bucket rounding here results in a pretty even distribution of demand within the 15:30-16:30 period.
    1. We need to figure out why this gridlocks the network to such a huge extent.  Without the extra time there was congestion in this area of hte CBD but no gridlock, so it's not a network/signal timing issue.
    1. I may try changing the demand profile of the start and end hours to make it more like incremental loading instead of having an even distribution.  We would have more demand in the second half of the 14:30-15:30 hour and in the first half of the 18:30-19:30 hour.
    1. If we can get rid of the gridlock we may start matching counts better since these results are pretty close to what we see in the test without the extended demand even though we have gridlock toward the end here.

### pb\_aug7\_1000a\_1S10E ###
  * Changes from last run:
    * Demand extended to 14:30-19:30 with 1% of PM demand added as start hour and 10% added as end hour
  * Convergence: Stopped after 40 iterations as it was clearly converging to gridlock.
  * Runtime:
  * Overall Vol/Count Ratio:
  * Observed Gridlock: All over the CBD.  This test converged to gridlock pretty early on and never recovered.
  * Link to Validation Spreadsheets:  None
  * Observations:
    1. Clearly the end hour demand is causing a lot of problems.  This adds extra demand to a very congested network, and it seems to be the tipping point in terms of our traffic exceeding the capacity in the CBD.

### pb\_aug7\_1000a\_10S1E ###
  * Changes from last run:
    * Demand extended to 14:30-19:30 with 10% of PM demand added as start hour and 1% added as end hour
  * Convergence: Min = 0.00740795, Max = 0.08556, Mean = 0.0346489
  * Runtime: Approx. 34.27 hours to do 60 iterations (other programs were running at the same time and slowing this down)
  * Overall Vol/Count Ratio:
  * Observed Gridlock: Not nearly as bad as when demand is added to both start and end hours.  Only about 400 vehicles waiting at the end of the simulation.  Primarily gridlocked in CBD.
  * Link to Validation Spreadsheets:  None
  * Observations:
    1. Adding the demand only to the start doesn't seem to be nearly as bad as adding it at the end.  The end hour gets gridlocked since we already have a very congested network at that time even without the additional demand.  The gridlock then propagates backward to the 5:30-6:30 time period.
    1. While this is useful to know (that the gridlock is more because of the end hour than the start hour), we still shouldn't have this many problems.
    1. Next test will be to see if using only 5% of the demand in the additional hours and only 90% of the demand in the PM peak still has gridlock.  This shouldn't because it will be the same total amount of demand just loaded over a longer time period.

### pb\_aug13\_1000a\_MDPMEV ###
  * Changes from last run:
    * Actual MD and EV trip tables used.  % of each demand set used was based on taking a 1-hour portion of the total demand period.
  * Convergence: Project this was in has become corrupted, so I can't access the test anymore to get the convergence info.
  * Runtime:
  * RMSE: Links = 68% (1,748 counts), Movements = 90% (7,643 counts)
  * GEH: Links = 8.40, Movements = 4.89
  * VMT = 1,225,908, VHT (3:30-6:30pm) = 64,484 hours
  * Overall Vol/Count Ratio: Links = 0.5869, Movements = 0.6967
  * Observed Gridlock: All over the CBD starting around 5:30/6:00
  * Link to Validation Spreadsheets:  [Aug 13 Actual MD and EV Demand Reports](http://dta.googlecode.com/files/pb_aug13_MDPMEV_Results.zip/)
  * Observations:
    1. Clearly switching to MD/EV trip tables hasn't helped us.  We still have huge amounts of gridlock that make the counts look really low.  We are measuring outflow and comparing to counts in the output processing, so when there is gridlock, the gridlocked vehicles don't get counted at all.
    1. Is there a different measure that we should be using?  Are the counts really outflow or some combination of outflow and occupancy?

### pb\_aug13\_400p\_90PM ###
  * Changes from last run:
    * Demand extended to 14:30-19:30 with 15% of MD demand added as start hour and 12% of EV demand added as end hour and only 90% of PM demand used in PM peak hours; Demand profile also used for PM hours based on counts at boundary locations
  * Convergence: Min = 0.00973505, Max = 0.0929695, Mean = 0.0361602 (Stopped at 50 iterations because of obvious gridlock issues)
  * Runtime: Approx. 21.86 hours for 50 iterations
  * Overall Vol/Count Ratio:
  * Observed Gridlock: All over the CBD
  * Link to Validation Spreadsheets:  None
  * Observations:
    1. This still doesn't seem to make sense.  By decreasing the PM demand we should be freeing up enough capacity to get the vehicles through the network.
    1. One observation from this test is that there are a lot of truck trips in the MD and EV trip tables, and the trucks may be overloading the network in the added demand.

### pb\_aug15\_400p\_RT ###
  * Changes from last run:
    * Response Times changed to 1.1 where 1.2 and 1.2 where 1.32 in AT 0 and 1 to increase capacity. (MD and EV extended demand still used.)
  * Convergence: Min = 0.0123642, Max = 0.0991522, Mean = 0.0373117(Stopped at 51 iterations because of obvious gridlock issues)
  * Runtime: Approx. 22.30 hours for 51 iterations
  * Overall Vol/Count Ratio:
  * Observed Gridlock: All over the CBD
  * Link to Validation Spreadsheets:  None
  * Observations:
    1. Even this significant increase in capacity wasn't enough to clear the gridlock.  We may need to look at other problems.

### pb\_aug16\_1030a\_Cap ###
  * Changes from last run:
    * Response Times changed to 1.1 where 1.2 and 1.2 where 1.32 in AT 0 and 1 to increase capacity. (MD and EV extended demand still used.)
    * Speeds in the CBD increased by 10 mph (except freeways)
  * Convergence: Min = 0.00904175, Max = 0.0627537, Mean = 0.0310921
  * Runtime: Approx. 29.31 hours for 60 iterations
  * Overall Vol/Count Ratio:
  * Observed Gridlock: All over the CBD
  * Link to Validation Spreadsheets:  None
  * Observations:
    1. We still had about 21,000 vehicles waiting at the end of the simulation.  There's clearly something overloading the network here.
    1. The next step will be to see how much the additional truck trips are affecting this gridlock.

### pb\_aug20\_530p\_NoT ###
  * Changes from last run:
    * RT and speeds back to normal.
    * Truck demand for start and end hours set to zero.
  * Convergence: Min = 0.00634479, Max = 0.128235, Mean = 0.0569804 (This wasn't a stable convergence since the relative gap was still shifting some, but after 60 iterations we had enough information to decide what to do for the next test.)
  * Runtime: Approx. 20.18 hours for 60 iterations
  * RMSE: Links = 50% (1,748 counts), Movements = 71% (7,643 counts)
  * GEH: Links = 6.10, Movements = 4.19
  * VMT = 1,418,136, VHT (3:30-6:30pm) = 70,735 hours
  * Overall Vol/Count Ratio: Links = 0.7433, Movements = 0.8034
  * Observed Gridlock: Ocean & Alemany, parts of Silver Ave,Columbus, Broadway, Laguna, Tayor (CBD in general)
  * Link to Validation Spreadsheets: [Aug 20 No Trucks in MD and EV Demand Reports](http://dta.googlecode.com/files/pb_aug20_NoT_Results.zip/)
  * Observations:
    1. We only have about 750 vehicles waiting at the end of the simulation here.  Clearly the trucks are a major factor in the gridlock developing after we add the start and end hours.
    1. Also, it's a good sign that we're getting back up closer to counts again.  If we can load the network with the start and end demand and get it to clear (or mostly clear), we may get much closer to counts.

### pb\_aug21\_530p ###
  * Changes from last run:
    * Only 1% of truck demand used for start and end hours
    * Stop signs added at centroid connectors (preliminary implementation without custom priorities file)
    * Response time for trucks changed from 1.6 to 1.25
  * Convergence: Min = 0.00697173, Max = 0.0682133, Mean = 0.0297328
  * Runtime: Approx. 22.59 hours to do 60 iterations
  * RMSE: Links = 50% (1,748 counts), Movements = 72% (7,643 counts)
  * GEH: Links = 6.01, Movements = 4.19
  * VMT = 1,464,957, VHT (3:30-6:30pm) = 66,708 hours
  * Overall Vol/Count Ratio: Links = 0.7505, Movements = 0.8082
  * Observed Gridlock: None.  We have heavy congestion in some parts of the CBD, but one of the changes we made here really cleared things out.
  * Link to Validation Spreadsheets:  [Aug 21 Stop Signs on Centroids and Updated Truck Response Time](http://dta.googlecode.com/files/pb_aug21_CentStops_Reports.zip/)
  * Observations:
    1. Amazingly, we have no gridlock at the end of the simulation and are able to completely clear the network.  There is congestion in the CBD, as there should be, but it's not as much as we've seen in past simulations.
    1. I can't be sure yet if it is the trucks or the stop signs on centroid connectors, but something has had a big effect on letting traffic get through the network here.
    1. It might be worthwhile to test just the stop signs and/or just the changes to truck response times to isolate which change is having the biggest effect on getting rid of the gridlock that we've seen in previous tests.
    1. We can start adding back in more of the MD and EV trucks to get a more accurate warm up/cool down time now.

### pb\_aug22\_530p\_50T ###
  * Changes from last run:
    * Only half of an hour's worth of truck demand used for start and end hours
  * Convergence: Min = 0.00759221, Max = 0.0858625, Mean = 0.0354923
  * Runtime: Approx. 22.22 hours to do 60 iterations
  * RMSE: Links = 50% (1,748 counts), Movements = 72% (7,643 counts)
  * GEH: Links = 6.09, Movements = 4.21
  * VMT = 1,445,020, VHT (3:30-6:30pm) = 66,455 hours
  * Overall Vol/Count Ratio: Links = 0.7453, Movements = 0.8036
  * Observed Gridlock: Stockton, Columbus, Broadway, Bay, Union, Mason and then spreading to the rest of the CBD starting about 6:15.
  * Link to Validation Spreadsheets:  [Aug 22 Half of MD and EV truck traffic added back](http://dta.googlecode.com/files/pb_aug22_50T_Reports.zip/)
  * Observations:
    1. This many trucks at the start and end overwhelm the network even with the updated truck response time.
    1. Next test will be to run the same test with 1/4 of an hour's worth of MD and EV trucks.
    1. Stop signs on centroid connectors are only working at external centroids.  We'll need to test these changes again when the stop sign priorities are corrected on the connectors.

### pb\_aug23\_500p\_25T ###
  * Changes from last run:
    * Only 1/4 of an hour's worth of truck demand used for start and end hours
  * Convergence: Min = 0.00698851, Max = 0.0618205, Mean = 0.0277422
  * Runtime: Approx. 24.44 hours to do 65 iterations (needed the extra 5 iterations to reach convergence)
  * RMSE: Links = 49% (1,748 counts), Movements = 72% (7,643 counts)
  * GEH: Links = 5.97, Movements = 4.19
  * VMT = 1,462,665, VHT (3:30-6:30pm) = 65,152 hours
  * Overall Vol/Count Ratio: Links = 0.7504, Movements = 0.8084
  * Observed Gridlock: None.  There is heavy congestion in the CBD but no gridlock.
  * Link to Validation Spreadsheets:  [Aug 23 1/4 of MD and EV truck traffic added back](http://dta.googlecode.com/files/pb_aug23_25T_Reports.zip/)
  * Observations:
    1. Adding back the MD and EV trucks doesn't seem to make a lot of difference in the results.  As long as it doesn't cause gridlock.
    1. We need to test Lisa's changes to allow for stop signs at connectors.
    1. We may want to play with the truck response times a bit to find out what gets us to the right level of congestion to match our counts without causing total gridlock.

### pb\_aug27\_1130a\_SCent ###
  * Changes from last run:
    * Only 1% of the MD and EV truck trip tables were used.
    * Lisa's fix for the stop sign priorities on centroids was incorporated
  * Convergence: Min = 0.0069094, Max = 0.0606801, Mean = 0.026982
  * Runtime: Approx. 24.49 hours to do 65 iterations (needed the extra 5 iterations to reach convergence)
  * RMSE: Links = 49% (1,748 counts), Movements = 72% (7,643 counts)
  * GEH: Links = 6.00, Movements = 4.18
  * VMT = 1,465,257, VHT (3:30-6:30pm) = 66,293 hours
  * Overall Vol/Count Ratio: Links = 0.7524, Movements = 0.8077
  * Observed Gridlock: None.
  * Link to Validation Spreadsheets:  [Aug 27 Stop Signs on Centroid Connectors](http://dta.googlecode.com/files/pb_aug27_Stops_Reports.zip/)
  * Observations:
    1. The correct implementation of the stop signs on centroid connectors not only improved count matching, but it also creates much less congestion in the CBD.
    1. The next step will be to add more of the trucks back into the start and end hours.
    1. It will be good to test this when Dan has added the pedestrian friction for turning movements.  The combination of the two effects should allow us to increase congestion somewhat with the turning friction without causing gridlock.

### pb\_aug28\_530p ###
  * Changes from last run:
    * Only 1/3 of an hour of the MD and EV truck trip tables were used.
  * Convergence: Min = 0.00750854, Max = 0.0754229, Mean = 0.0323439
  * Runtime: Approx. 22.90 hours to do 60 iterations
  * RMSE: Links = 50% (1,748 counts), Movements = 72% (7,643 counts)
  * GEH: Links = 6.04, Movements = 4.20
  * VMT = 1,459,743, VHT (3:30-6:30pm) = 66,543 hours
  * Overall Vol/Count Ratio: Links = 0.7408, Movements = 0.8027
  * Observed Gridlock: None.
  * Link to Validation Spreadsheets:  [Aug 28 1/3 of an hour's truck demand for MD and EV Results](http://dta.googlecode.com/files/pb_aug28_33T_Reports.zip/)
  * Observations:
    1. We still don't have heavy congestion in the CBD, even with 1/3 of an hour's worth of trucks added to the start and end hours.
    1. I think this is a good place to stop with adding trucks and go on with other testing.  1/3 of an average hour's worth of MD and EV trucks seems like a realistic level of trucks for the start and end hours.

### pb\_sept4\_430p\_RS\_T1 ###
  * Changes from last run:
    * Set the Random Seed value to 5 (changed from 1).
  * Convergence: Min = 0.00681721, Max = 0.0667021, Mean = 0.0326394
  * Runtime: Approx. 27.05 hours to do 60 iterations (It's slower because I moved the project to a newer, slightly slower computer.  This computer has a slower processor but tons of hard drive space, which is more important right now given how big the files for each scenario run are.)
  * RMSE: Links = 50% (1,748 counts), Movements = 72% (7,643 counts)
  * GEH: Links = 6.04, Movements = 4.17
  * VMT = 1,468,712, VHT (3:30-6:30pm) = 66,837 hours
  * Overall Vol/Count Ratio: Links = 0.7543, Movements = 0.8064
  * Observed Gridlock: None.
  * Link to Validation Spreadsheets:  [Random Seed Test 1 Results](http://dta.googlecode.com/files/pb_sept4_RS_T1_Reports.zip/)
  * Observations:
    1. The pattern of convergence is different that we see with a random seed of 1. The peak in the relative gap is much higher and sharper, and it happens much sooner.
    1. The largest changes weren't very large.  The largest difference in total link flow (over all 3 hours of the PM peak) was 2,551 vehicles.  For the most part, the changes were on a few major arterials.  The flow generally increased in one direction and dropped off in the other direction, increasing the flow on multiple nearby arterials.
    1. We do a slightly better job of matching counts with this setting because it re-balances flows a bit between the major arterials and the smaller arterials around them.
    1. Given the change in convergence and a noticeable change in some of the volumes, I'm going to run another test with the random seed set to 2 instead to see how sensitive these values are to a smaller change.

### pb\_sept5\_500p\_RS\_T2 ###
  * Changes from last run:
    * Set the Random Seed value to 2 (changed from base of 1).
  * Convergence: Min = 0.00683357, Max = 0.0768023, Mean = 0.0354672
  * Runtime: Approx. 31.84 hours to do 60 iterations
  * RMSE: Links = 50% (1,748 counts), Movements = 73% (7,643 counts)
  * GEH: Links = 6.08, Movements = 4.18
  * VMT = 1,468,480, VHT (3:30-6:30pm) = 66,193 hours
  * Overall Vol/Count Ratio: Links = 0.7518, Movements = 0.8075
  * Observed Gridlock: None.
  * Link to Validation Spreadsheets:  [Random Seed Test 2 Results](http://dta.googlecode.com/files/pb_sept5_RS_T2_Reports.zip/)
  * Observations:
    1. After looking at the batch file again, I realized that some of the signal plans might be slightly different than the Aug. 28 test.  That one had 4:30 as the signal plan time to look for, and both of these have 3:30.  I'll run a new test that has everything the same except the Random Seed so we have a definite base.
    1. Between the two different random seed tests there were some differences, but those were smaller than the difference between each test and the Aug 28 test, which leads me to believe that the signal timing may be to blame for some of that difference.
    1. The convergence looked different than it did for a random seed of 1 or 5.  Changing this value does seem to have a significant impact on the speed and pattern of convergence, but the impact on flows is somewhat smaller.

### pb\_sept10\_830a\_Base ###
  * Changes from last run:
    * Random Seed = 1. The signals this time are the same as with the Sept 4 and 5 tests.
  * Convergence: Min = 0.00750274, Max = 0.0882354, Mean = 0.0346544
  * Runtime: Approx. 23.76 hours to do 60 iterations (this was run as an additional DTA in the Sept. 4 scenario, so some of the bucket rounding, etc. may not have been required, which would shorten the run time)
  * RMSE: Links = 50% (1,748 counts), Movements = 72% (7,643 counts)
  * GEH: Links = 6.03, Movements = 4.16
  * VMT = 1,458,712 miles; VHT (3:30-6:30pm) = 66,837 hours
  * Overall Vol/Count Ratio: Links = 0.7533, Movements = 0.8057
  * Observed Gridlock: None.
  * Link to Validation Spreadsheets:  [Random Seed Test Base Reports](http://dta.googlecode.com/files/pb_sept10_RSBase_Reports.zip/)
  * Link to PPT with Flow Comparison: [Random Seed Test Flow and Travel Time Comparisons](http://dta.googlecode.com/files/Random%20Seed%20Test%20Results.pptx/)
  * Observations:
    1. Interestingly, the flow coparison seems to show a larger difference in the test where the Random Seed =2.
    1. Neither test showed large shifts of more than 1,600 vehicles over the 3-hour PM peak.

### sf\_sept7\_1200p\_ResetSpeedFlow\_v1 ###
  * Changes from last run:
    * Discovered that speed, flow, and density parameters had been misunderstood.  Reset vehicle effective length and response time to match intended parameters.
  * Convergence: Min = 0.00773108, Max = 0.15868, Mean = 0.0483952
  * Runtime: Approx. 23.87 hours to do 50 iterations
  * RMSE: Links = xx% (xxxx counts), Movements = x% (xxxx counts)
  * GEH: Links = x.xx, Movements = x.xx
  * VMT = xxxxxx, VHT (3:30-6:30pm) = xxxxxx hours
  * Overall Vol/Count Ratio: Links = xxxx, Movements = xxxx
  * Observed Gridlock: Gridlock occurs around 5:30 PM. Approximately 50k waiting vehicles accumulate and do not dissipate.
  * Link to Validation Spreadsheets:  xxx
  * Observations:
    1. This run resulted in severe congestion leading to gridlock.  This was anticipated due to the significant increase in PCU effective length relative to previous runs.  Subsequent runs will relax response time and jam density to observe the sensitivity of gridlock to these parameters.

### sf\_sept10\_430p\_ResetSpeedFlow\_v2 ###
  * Changes from last run:
    * Reduced car and truck response time from 1.25 sec to 1.0 sec to test sensitivity of gridlock in previous run to response time.
  * Convergence: Min = 0.00682784, Max = 0.131843, Mean = 0.050911
  * Runtime: Approx. 44.78 hours to do 60 iterations
  * RMSE: Links = 53% (1,748 counts), Movements = 74% (7,643 counts)
  * GEH: Links = 6.48, Movements = 4.28
  * VMT = 1,357,472, VHT (3:30-6:30pm) = 67,550 hours
  * Overall Vol/Count Ratio: Links = 0.7296, Movements = 0.8009
  * Observed Gridlock: Starts around 18:00 at 25th St & Harrison (in the South); 3rd/Geary/Market; Freemont/Pine/Market; On-Ramp to I-80 at Freemont & Harrison; Stockton & Columbus, Mason & Columbus, Gough near California;  after 18:10 the gridlock quickly spreads over the whole CBD and most of the rest of the Northern region.
  * Link to Validation Spreadsheets:  [Speed Flow Changes V2 Reports](http://dta.googlecode.com/files/sf_sept10_SpeedFlow_V2_Reports.zip/)
  * Observations:
    1. The gridlock is really bad here.  In some areas it develops where we saw it when we had issues with trucks, but the locations along Market are clearly because of the changes to the car properties.
    1. The count-matching is clearly worse, but that may be more because there are so many vehicles that never even get to enter the network because of the gridlock.

### sf\_sept10\_500p\_ResetSpeedFlow\_v3 ###
  * Changes from last run:
    * Car and truck response time still 1.0 sec. PCU effective length reduced to 20ft from 24ft and Truck effective length reduced from 36ft to 30ft.
  * Convergence: Min = 0.00675461, Max = 0.0593676, Mean = 0.0264851
  * Runtime: Approx. 50.29 hours to do 60 iterations
  * RMSE: Links = 52% (1,748 counts), Movements = 74% (7,643 counts)
  * GEH: Links = 6.29, Movements = 4.32
  * VMT = 1,469,785, VHT (3:30-6:30pm) = 62,884 hours
  * Overall Vol/Count Ratio: Links = 0.7604, Movements = 0.8191
  * Observed Gridlock: None.
  * Link to Validation Spreadsheets:  [Speed Flow Changes V3 Reports](http://dta.googlecode.com/files/sf_sept10_SpeedFlow_V3_Reports.zip/)
  * Observations:
    1. This test has no gridlock and very little congestion in the CBD.  We really need to find a halfway point between the extreme gridlock caused by the V2 settings and the lack of congestion we see with these settings.
    1. This set of speed-flow parameters is going to be used in the first PB test for prohibiting left turns from connectors.

### pb\_sept11\_LTCent ###
  * Changes from last run:
    * Settings from V3 with left turns from centroids prohibited
  * Convergence: Min = 0.00693941, Max = 0.0689223, Mean = 0.0304047
  * Runtime: Approx. 34.94 hours to do 60 iterations (Running another instance of Dynameq and two other programs at the same time)
  * RMSE: Links = 52% (1,748 counts), Movements = 75% (7,643 counts)
  * GEH: Links = 6.39, Movements = 4.32
  * VMT = 1,471,900, VHT (3:30-6:30pm) = 64,420 hours
  * Overall Vol/Count Ratio: Links = 0.7518, Movements = 0.8151
  * Observed Gridlock: Fleeting in some areas of the CBD.  Rarely lasts more than 5-15 minutes.
  * Link to Validation Spreadsheets:  [Prohibited Left Turns from Centroids with Speed Flow Changes V3 Reports](http://dta.googlecode.com/files/pb_sept11_LTCent_Reports.zip/)
  * Observations:
    1. This test creates gridlock where there wasn't even congestion with the V3 settings.  Clearly, prohibiting the left turns over-crowds the other movements.  It might be a better idea to just add a high penalty to those left turns instead of prohibiting them.

### pb\_sept12\_LT2 ###
  * Changes from last run:
    * Still prhibiting left turns with car length set to 24ft and truck response time to 1.25sec
  * Convergence: Min = 0.00685579, Max = 0.1337749, Mean = 0.0507178
  * Runtime: Approx. 32.23 hours to do 60 iterations (Running another instance of Dynameq and two other programs at the same time)
  * RMSE: Links = 52% (1,748 counts), Movements = 74% (7,643 counts)
  * GEH: Links = 6.31, Movements = 4.27
  * VMT = 1,399,539, VHT (3:30-6:30pm) = 67,483 hours
  * Overall Vol/Count Ratio: Links = 0.7417, Movements = 0.8065
  * Observed Gridlock: 3rd & Market, Freemont & Market, Columbus; Spreads out to the rest of the CBD around 18:00.
  * Link to Validation Spreadsheets:  [Prohibited Left Turns from Centroids with Some Speed Flow Changes Reports](http://dta.googlecode.com/files/pb_sept12_LT2_Reports.zip/)
  * Observations:
    1. This test has lots of gridlock.
    1. I think we need to try an in-between test that is halfway between V2 and V3 settings.
    1. I think we need to try penalizing the left turns from centroids instead of prohibiting them.

### sf\_sept13\_ResetSpeedFlow\_v4 ###
  * Changes from last run:
    * Test of effective length midpoint between v2 and v3 because v2 is gridlocked and v3 is not congested.  Effective length for PCUs set to 22ft. Effective length of trucks set to 33ft.
  * Convergence: Min = 0.00734649, Max = 0.127082, Mean = 0.0544831
  * Runtime: Approx. 29.82 hours to do 60 iterations
  * RMSE: Links = 51% (1,748 counts), Movements = 73% (7,643 counts)
  * GEH: Links = 6.27, Movements = 4.24
  * VMT = 1,439,454, VHT (3:30-6:30pm) = 65,007 hours
  * Overall Vol/Count Ratio: Links = 0.761, Movements = 0.8169
  * Observed Gridlock: Fleeting in some locations in the CBD, but never lasts more than 5-10 mins.
  * Link to Validation Spreadsheets:  [Speed Flow Changes V4 Reports](http://dta.googlecode.com/files/sf_sept13_SpeedFlow_V4_Reports.zip/)
  * Observations:
    1. This one clearly didn't reach a very steady convergence, but it looked like it was good enough at 60 iterations to process the results and decide what to do next.
    1. Some combination of these settings and a penalty on left turns out of centroids might be the best option to test next.
    1. There was some occasional gridlock here, but not much.  There was some serious congestion in pars of the CBD, so we want to avoid increasing the parameters beyond this until we test some othe settings in Dynameq (like gap acceptance) that could help with the congestion.

### sf\_sept18\_ResetSpeedFlow\_v4\_extendedRuns ###
  * Changes from last run:
    * Previous model run did not seem to be fully converged at 60 iterations.  The DTA was continued to 85, 100, 125, and 130 iterations.  At both 85 and 100 iterations results did not seem fully converged, so more iterations were added. Gridlock was present in 125th iteration, but absent in 130th iteration.
  * Convergence: Min = 0.00678499, Max = 0.0405788, Mean = 0.02269
  * Runtime: Approx. 80.41 hours to do 130 iterations (0.619 hr / iter.)
  * RMSE: Links = 52% (1,748 counts), Movements = 74% (7,659 counts)
  * GEH: Links = 6.35, Movements = 4.30
  * VMT = 1,657,896, VHT (3:30-6:30pm) = 78,756 hours
  * Average Speed (VMT/VHT) = 21.2 mph
  * Overall Vol/Count Ratio: Links = 0.7522, Movements = 0.8143
  * Max waiting vhcls:  351, Max traveling vhcls: 33,609
  * Observed Gridlock: After some iterations gridlock was present, but no tin the final iteration
  * Observations:
    1. Heavy congestion on EB Market approaching central freeway, and on WB Harrison at 4th.
    1. Severe congestion upstream from WB Harrison occurs after 6:30 PM.
    1. Clayton and Market needs to be corrected. Signalization is missing and cars are allowed to perform movements that only MUNI is allowed to make.

### sf\_sept18\_ResetSpeedFlow\_v5 ###
  * Changes from last run:
    * Uses same speed/flow/density parameters as V4, but adjusts critical gap settings.  Critical gap values reduced by 50% from the default settings for all movement and control categories.  Critical wait times were not adjusted.
  * Convergence: Min = 0.00611203, Max = 0.18799, Mean = 0.0503522
  * Runtime: Approx. 70.79 hours to do 130 iterations (0.545 hr / iter.)
  * RMSE: Links = 51% (1,748 counts), Movements = 73% (7,659 counts)
  * GEH: Links = 6.26, Movements = 6.34
  * VMT = 1,643,236, VHT (3:30-6:30pm) = 78,510 hours
  * Average Speed (VMT/VHT) = 20.9 mph
  * Overall Vol/Count Ratio: Links = 0.7545, Movements = 0.8179
  * Max waiting vhcls:  1,352, Max traveling vhcls: 36,589
  * Observed Gridlock: None, all vehicles clear
  * Observations:
    1. ...

### sf\_sept25\_ResetSpeedFlow\_v6 ###
  * Changes from last run:
    * PCU effective length remains at 22' (33' for trucks)
    * Critical gap returned to default settings
    * All follow-up times reduced by 20% (AWSC, TWSC, merge and signalized permitted mvmts)
  * Convergence: Min = 0.00654758, Max = 0.0503777, Mean = 0.028217
  * Runtime: Approx. 71.44 hours to do 90 iterations (0.79 hr / iter.)
  * RMSE: Links = 51% (1,748 counts), Movements = 74% (7,659 counts)
  * GEH: Links = 6.34, Movements = 4.33
  * VMT = 1,658,414, VHT (3:30-6:30pm) = 77,295 hours
  * Average Speed (VMT/VHT) = 21.5 mph
  * Overall Vol/Count Ratio: Links = 0.7503, Movements = 0.8094
  * Max waiting vhcls:  577, Max traveling vhcls: 33,270
  * Observed Gridlock: None, all vehicles clear
  * Observations:
    1. ...

### sf\_sept25\_ResetSpeedFlow\_v7 ###
  * Run v7 was not completed.  The model crashed midway through and was not restarted.  By the time the crash occurred other model runs rendered v7 unnecessary.

### sf\_sept25\_ResetSpeedFlow\_v8 ###
  * Changes from last run:
    * PCU eff. length reduced to 21' (31.5' for trucks)
    * Critical gaps reduced by 20% for crossing, merging, TWSC, Merge, and Signalized movements
  * Convergence: Min = 0.00677008, Max = 0.0833202, Mean = 0.0370174
  * Runtime: Approx. 46.31 hours to do 60 iterations (0.77 hr / iter.)
  * RMSE: Links = 51% (1,748 counts), Movements = 74% (7,659 counts)
  * GEH: Links = 6.24, Movements = 4.25
  * VMT = 1,673,241, VHT (3:30-6:30pm) = 77,680 hours
  * Average Speed (VMT/VHT) = 21.5 mph
  * Overall Vol/Count Ratio: Links = 0.7619, Movements = 0.8176
  * Max waiting vhcls:  222, Max traveling vhcls: 30,709
  * Observed Gridlock: None, all vehicles clear
  * Observations:
    1. ...

### pb\_sept26\_530p\_V9 ###
  * Changes from last run:
    * Vehicle lengths changed to 21ft and 31.5 ft for cars and trucks
    * Critical gaps reduced by 20% for crossing, merging, TWSC, Merge, and Signalized movements
    * Distance term added to generalized cost expression
  * Convergence: Min = 0.00512647, Max = 0.0506207, Mean = 0.0214311
  * Runtime: Approx. 38.13 hours to do 70 iterations (two other models running at the same time)
  * RMSE: Links = 52% (1,748 counts), Movements = 75% (7,643 counts)
  * GEH: Links = 6.30, Movements = 4.29
  * VMT = 1,627,728, VHT (3:30-6:30pm) = 77,972 hours
  * Average Speed (VMT/VHT) = 20.9 mph
  * Overall Vol/Count Ratio: Links = 0.7496, Movements = 0.8083
  * Observed Gridlock: Columbus Ave., Bay St. around Columbus, Stockton, Geary/Market/3rd St; quickly spreads from these areas to whole CBD after 18:20
  * Link to Validation Spreadsheets:  [Speed Flow Changes V9 Reports](http://dta.googlecode.com/files/pb_sept26_V9_Reports.zip/)
  * Observations:
    1. This one is very clearly converged, but there is still significant gridlock.
    1. Once we have the results of V8, we can see how much of the gridlock is caused by the distance term in the Generalized Cost and how much by the changes to the critical gap.

### pb\_sept27\_900a\_V10 ###
  * Changes from last run:
    * Vehicle lengths set to 21ft and 31.5 ft for cars and trucks
    * Critical gaps and follow-up time all set to defaults except TWSC RT and Thru follow-up and Merge follow-up all decreased by 20%.
  * Convergence: Min = 0.00658655, Max = 0.0646256, Mean = 0.0278028
  * Runtime: Approx. 67.35 hours to do 80 iterations (two other models running at the same time)
  * RMSE: Links = 51% (1,748 counts), Movements = 74% (7,643 counts)
  * GEH: Links = 6.30, Movements = 4.29
  * VMT = 1,654,206, VHT (3:30-6:30pm) = 78,366 hours
  * Average Speed (VMT/VHT) = 21.1 mph
  * Overall Vol/Count Ratio: Links = 0.7485, Movements = 0.8105
  * Observed Gridlock: For the most part, there seems to be not a lot of congestion.  The only problem area is at Market & Freemont where it actually backs up the I-80W off-ramp and creates congestion back onto I-80W, but only after 19:15 (which is really odd).
  * Link to Validation Spreadsheets:  [Speed Flow Changes V10 Reports](http://dta.googlecode.com/files/pb_sept27_V10_Reports.zip/)
  * Observations:
    1. With these settings we get very little congestion.  This makes some sense since we decreased the vehicle lengths.

### pb\_sept27\_930a\_V11 ###
  * Changes from last run:
    * Vehicle lengths set to 21ft and 31.5 ft for cars and trucks
    * Critical gaps and follow-up time all set to defaults except TWSC RT and Thru follow-up and Merge follow-up all decreased by 20%.
    * Distance term added to generalized cost expression
  * Convergence: Min = 0.00526515, Max = 0.0388225, Mean = 0.0205391
  * Runtime: Approx. 64.46 hours to do 80 iterations (two other models running at the same time)
  * RMSE: Links = 51% (1,748 counts), Movements = 74% (7,643 counts)
  * GEH: Links = 6.19, Movements = 4.28
  * VMT = 1,634,490, VHT (3:30-6:30pm) = 77,110 hours
  * Average Speed (VMT/VHT) = 21.2 mph
  * Overall Vol/Count Ratio: Links = 0.7544, Movements = 0.8094
  * Observed Gridlock: Starts and Columbus Ave. and intersecting streets such as Bay St., Taylor, Stockton, Mason, etc.; Spreads out to the rest of the CBD after 18:20
  * Link to Validation Spreadsheets:  [Speed Flow Changes V11 Reports](http://dta.googlecode.com/files/pb_sept27_V11_Reports.zip/)
  * Observations:
    1. Like V9, the convergence is clearly stable after 80 iterations, but there is significant gridlock.
    1. Comparing this to the results of V10, we can see that the generalized cost term creates a lot of congestion that is not there otherwise.
    1. Our next test should be to try the same settings with a smaller coefficient on the generalized cost (half of the current coefficient).

### pb\_oct1\_500p\_V12 ###
  * Changes from last run:
    * Vehicle lengths set to 21ft and 31.5 ft for cars and trucks
    * Critical gaps and follow-up time all set to defaults except TWSC RT and Thru follow-up and Merge follow-up all decreased by 20%.
    * Coefficient of distance term halved (now 14.4)
  * Convergence: Min = 0.00573276, Max = 0.0441135, Mean = 0.021717
  * Runtime: Approx. 25.85 hours to do 70 iterations
  * RMSE: Links = 51% (1,748 counts), Movements = 74% (7,643 counts)
  * GEH: Links = 6.30, Movements = 4.27
  * VMT = 1,656,335, VHT (3:30-6:30pm) = 76,288 hours
  * Average Speed (VMT/VHT) = 21.7 mph
  * Overall Vol/Count Ratio: Links = 0.7475, Movements = 0.8079
  * Observed Gridlock: None.
  * Link to Validation Spreadsheets:  [Speed Flow Changes V12 Reports](http://dta.googlecode.com/files/pb_oct1_V12_Reports.zip/)
  * Observations:
    1. Convergence looked steady after 70 iterations with no gridlock.
    1. By halving the coefficient on the generalized cost term, we can still get results without gridlock.
    1. Test V13 will keep these same settings with the vehicle lengths increased back up to 22 and 33 ft respectively.
    1. For other test going forward we should process the V6 and V8 results and compare them to V10 to see which critical gap/follow-up time settings give the best results.  We can then apply the different vehicle lengths and generalized cost terms to the best one.

### pb\_oct3\_900a\_V13 ###
  * Changes from last run:
    * Vehicle lengths set to 22ft and 33 ft for cars and trucks
    * Critical gaps and follow-up time all set to defaults except TWSC RT and Thru follow-up and Merge follow-up all decreased by 20%.
    * Coefficient of distance term halved (now 14.4)
  * Convergence: Min = 0.00557595, Max = 0.0783259, Mean = 0.0360715
  * Runtime: Approx. 34.32 hours to do 100 iterations (messy convergence)
  * RMSE: Links = 51% (1,748 counts), Movements = 73% (7,643 counts)
  * GEH: Links = 6.19, Movements = 4.24
  * VMT = 1,631,560, VHT (3:30-6:30pm) = 78,726 hours
  * Average Speed (VMT/VHT) = 20.7 mph
  * Overall Vol/Count Ratio: Links = 0.7547, Movements = 0.8144
  * Observed Gridlock: None.
  * Link to Validation Spreadsheets:  [Speed Flow Changes V13 Reports](http://dta.googlecode.com/files/pb_oct3_V13_Reports.zip/)
  * Observations:
    1. Convergence was really unsteady, but there was no gridlock at the end of the simulation.
    1. The count-matching seems to be better here with more congestion due to the increase in car length (vs. V12).
    1. There is some very heavy congestion in the CBD here, but it clears out by the end of the simulation time.
    1. Given the amount of congestion, with these settings we would definitely get gridlock in a test with future demand.

### pb\_oct8\_1230p\_V14 ###
  * Changes from last run:
    * Same settings as V8 test for critical gap and follow-up time
    * Vehicle lengths set to 22ft and 33ft
    * Distance term of 14.4\*length added to generalized cost function
  * Convergence: Min = 0.00559359, Max = 0.0419954, Mean = 0.0232241
  * Runtime: Approx. 40.40 hours to do 100 iterations (could have probably stopped around 80, but I was in meetings all day yesterday so let it run to 100)
  * RMSE: Links = 51% (1,748 counts), Movements = 74% (7,643 counts)
  * GEH: Links = 6.29, Movements = 4.27
  * VMT = 1,636,903, VHT (3:30-6:30pm) = 77,819 hours
  * Average Speed (VMT/VHT) = 21.0 mph
  * Overall Vol/Count Ratio: Links = 0.7475, Movements = 0.8083
  * Observed Gridlock: None.
  * Link to Validation Spreadsheets:  [Speed Flow Changes V14 Reports](http://dta.googlecode.com/files/pb_oct8_v14_Reports.zip/)
  * Observations:
    1. Very converged by the time it stopped.
    1. There is some heavy congestion in the CBD and on 25th St, Gough, and Laguna between 19:00 and 19:30, but it's not as bas as in V13.
    1. This test actually does a worse job of matching counts than the V8 test without the distance term in the generalized cost.
    1. We may need to have some compromise here.  The next test that would be good to do might be V8 critical gaps and follow-up time with the generalized cost term but with the vehicle lengths decreased to 21 and 31.5.

### pb\_oct10\_400p\_V15 ###
  * Changes from last run:
    * Same settings as V8 test for critical gap, follow-up time and vehicle length
    * Distance term of 14.4\*length added to generalized cost function
  * Convergence: Min = 0.0056292, Max = 0.0400427, Mean = 0.0203637
  * Runtime: Approx. 60.33 hours to do 80 iterations (takes more time when running at the same time as a test with facility type penalty)
  * RMSE: Links = 51% (1,748 counts), Movements = 74% (7,643 counts)
  * GEH: Links = 6.25, Movements = 4.27
  * VMT = 1,661,988, VHT (3:30-6:30pm) = 77,527 hours
  * Average Speed (VMT/VHT) = 21.4 mph
  * Overall Vol/Count Ratio: Links = 0.7478, Movements = 0.8092
  * Observed Gridlock: None.
  * Link to Validation Spreadsheets:  [Speed Flow Changes V15 Reports](http://dta.googlecode.com/files/pb_oct10_V15_Reports.zip/)
  * Observations:
    1. There is some congestion but no gridlock.
    1. These results are not too different (in terms of count-matching).  Hopefully the test with the facility type penalty will show better results.

### pb\_oct10\_500p\_V16 ###
  * Changes from last run:
    * Same settings as V8 test for critical gap, follow-up time and vehicle length
    * Distance term of 14.4\*length added to generalized cost function
    * Facility type penalty of 1/2 FF Time added to generalized cost function
  * Convergence: Min = 0.00414533, Max = 0.0526134, Mean = 0.0247232
  * Runtime: Approx. 60.66 hours to do 80 iterations (takes more time when running at the same time as a test with facility type penalty)
  * RMSE: Links = 48% (1,748 counts), Movements = 72% (7,643 counts)
  * GEH: Links = 6.05, Movements = 4.17
  * VMT = 1,677,175, VHT (3:30-6:30pm) = 80,639 hours
  * Average Speed (VMT/VHT) = 20.8 mph
  * Overall Vol/Count Ratio: Links = 0.8321, Movements = 0.8679
  * Observed Gridlock: None.
  * Link to Validation Spreadsheets:  [Speed Flow Changes V16 Reports](http://dta.googlecode.com/files/pb_oct10_V16_Reports.zip/)
  * Observations:
    1. There is not much congestion.
    1. These results are really good compared to what we've been seeing in other tests.

### pb\_oct15\_430p\_V17 ###
  * Changes from last run:
    * Same settings as V16 with the transit lanes allowing right-turns added
  * Convergence: Min = 0.00398136, Max = 0.0725547, Mean = 0.0371406
  * Runtime: Approx. 31.93 hours to do 100 iterations (needed 100 and still didn't have a very steady/stable convergence)
  * RMSE: Links = 50% (1,748 counts), Movements = 72% (7,659 counts)
  * GEH: Links = 6.24, Movements = 4.22
  * VMT = 1,630,582, VHT (3:30-6:30pm) = 82,980 hours
  * Average Speed (VMT/VHT) = 19.7 mph
  * Overall Vol/Count Ratio: Links = 0.7968, Movements = 0.8496
  * Observed Gridlock: Many areas of the CBD, but not severe enought that it didn't clear by the end of the simulation.
  * Link to Validation Spreadsheets:  [Speed Flow Changes V17 with Transit + Right Turns Reports](http://dta.googlecode.com/files/pb_oct15_V17_Reports.zip/)
  * Observations:
    1. There is way too much congestion to use these settings for testing anything like future demand.
    1. It's possible that also splitting the approaches to centroid connectors would help some of this congestion, but it may be that in some areas of the CBD we just don't have enough capacity on some of these links to accomodate all of the traffic.
    1. We might want to consider slightly increasing capacities in the CBD to account for the fact that in real life, drivers to use those bus-only lanes at times to get around congestion even if they're not turning right.

### sf\_octxx\_V18 ###
  * Changes from last run:
    * Same as V17 run, but different implementation of transit lanes.  In the previous run transit lane links are split in half to allow right turning vehicle to use transit lanes at intersections.  In this run links are also split to allow right turning vehicles to use the transit lanes for access to centroid connectors.
  * Convergence: Min = ..., Max = ..., Mean = ...
  * Runtime: Approx. ... hours to do ... iterations (extended to 100 iterations seeking a solution where waiting vehicles clear, but this does nto happen at 100 iterations)
  * RMSE: Links = xx% (xxxx counts), Movements = xx% (xxxx counts)
  * GEH: Links = xxx, Movements = xxx
  * VMT = xxx, VHT (3:30-6:30pm) = xxx hours
  * Average Speed (VMT/VHT) = xxx mph
  * Overall Vol/Count Ratio: Links = xxx, Movements = xxx
  * Observed Gridlock: The model run is heavily congested.  Girdlock appears and does not dissipate.  Waiting vehicles never enter the network and traveling vehicles never clear.
  * Link to Validation Spreadsheets:  xxx
  * Observations:
    1. Heavy congestion on SB US-101 from downtown to San Mateo border. Approaches at Octavia, 10th, S. Van Ness, and Cesar Chavez all experience lengthy approach queues.
    1. US-101 congestion highlighted a couple of network coding errors on the Central Freeway that either reduce approach throughput or alter intersection configuration.

### sf\_oct22\_V19 ###
  * Changes from last run:
    * Same as V17, but with minor updates to transit lane link splitting logic.  Very short links are no longer split.  Also removes the distance term from the generalized cost expression for cars (but maintains it for trucks).  JHC 2012 land use is not used, but it will be implemented for the next run.
  * Convergence: Min = xxx, Max = xxx, Mean = xxx
  * Runtime: Approx. xxx hours to do xxx iterations
  * RMSE: Links = xxx% (xxxx counts), Movements = xx% (xxxx counts)
  * GEH: Links = xxx, Movements = xxx
  * VMT = xxx, VHT (3:30-6:30pm) = xxx hours
  * Average Speed (VMT/VHT) = xxx mph
  * Overall Vol/Count Ratio: Links = xxx, Movements = xxx
  * Observed Gridlock: Yes.
  * Link to Validation Spreadsheets:  xxx
  * Observations:
    1. xxx.
    1. xxx.
    1. xxx.

### sf\_oct29\_V20 (finalCalibration1) ###
  * Changes from last run:
    * JHC 2012 land use
    * Effective length factor of 0.95 in AT0 and AT1 (1.0 elsewhere)
    * All turning movements are permitted, unless they have a dedicated signal phase (in which case turn is protected movement)
    * 21' effective PCU length (trucks x1.5)
    * Turning movement follow-up times are 2.0 sec (AT2+), 2.22 sec (AT1) and 2.67 (AT0)
    * Response time factor of 0.8 for weaving link of NB US-101
    * Same bus lane implementation as previous run
    * 21' effective PCU length (trucks x1.5)
  * Convergence: Min = 0.453391%, Max = 10.4815%, Mean = 4.45782%
  * Runtime: Approx. 44.6 hours to do 65 iterations
  * RMSE: Links = 52% (1,740 counts), Movements = 75% (7,643 counts)
  * GEH: Links = 6.33, Movements = 4.29
  * VMT = 1,702,774, VHT (3:30-6:30pm) = 80,226 hours
  * Average Speed (VMT/VHT) = 21.2 mph
  * Overall Vol/Count Ratio: Links = 0.8483, Movements = 0.8818
  * Observed Gridlock: Gridlock present at 50 iterations.  No gridlock at 65 iterations.
  * Link to Validation Spreadsheets: [Reset Speed Flow v20 - Final Calibration 1 - restrictive](http://dta.googlecode.com/files/sf_oct29_V20_Reports.zip)
  * Observations:
    1. Heavy congestion and long multi-block queues throughout the CBD.
    1. Vehicles can clear, but it takes a long time.

### sf\_oct29\_V21 (finalCalibration2) ###
  * Changes from last run:
    * All turning movements are permitted, unless they have a dedicated signal phase (in which case turn is protected movement)
    * 20.5' effective PCU length (trucks x1.5)
    * Turning movement follow-up times are 2.0 sec (AT2+), 2.11 sec (AT1) and 2.22 (AT0)
  * Convergence: Min = 0.461168%, Max = 7.03288%, Mean = 3.19193%
  * Runtime: Approx. 65 hours to do 47.95 iterations
  * RMSE: Links = 52% (1,740 counts), Movements = 77% (7,643 counts)
  * GEH: Links = 6.37, Movements = 4.30
  * VMT = 1,720,317, VHT (3:30-6:30pm) = 78,768 hours
  * Average Speed (VMT/VHT) = 21.8 mph
  * Overall Vol/Count Ratio: Links = 0.8464, Movements = 0.8716
  * Observed Gridlock: None
  * Link to Validation Spreadsheets:  [Reset Speed Flow v21 - Final Calibration 2 - relaxed](http://dta.googlecode.com/files/sf_oct29_V21_Reports.zip)
  * Observations:
    1. Very little congestion on freeways or local roads.
    1. No congestion on EB I-80 over Bay Bridge

### pb\_oct29\_V22 (finalCalibration3) ###
  * Changes from last run:
    * All turning movements are permitted, even when there is a dedicated turning movement phase
    * 21' effective PCU length (trucks x1.5)
    * Turning movement follow-up times are 2.0 sec (AT2+), 2.11 sec (AT1) and 2.22 (AT0)
  * Convergence: Min = 0.467392%, Max = 10.602%, Mean = 5.00126%
  * Runtime: Approx. 62.80 hours to do 77 iterations
  * RMSE: Links = 51% (1,740 counts), Movements = 73% (7,643 counts)
  * GEH: Links = 6.17, Movements = 4.20
  * VMT = 1,709,866, VHT (3:30-6:30pm) = 79,365 hours
  * Average Speed (VMT/VHT) = 21.5 mph
  * Overall Vol/Count Ratio: Links = 0.8462, Movements = 0.8714
  * Observed Gridlock: No gridlock at 77 iterations
  * Link to Validation Spreadsheets:  [Reset Speed Flow v21 - Final Calibration 3 - longer vhcl length / higher turn capacity](http://dta.googlecode.com/files/pb_oct29_V22_Reports.zip)
  * Observations:
    1. Fairly heavy congestion.
    1. V24 tests the same parameters, but with protected turn phases for protected turning movements

### pb\_oct29\_V23 (finalCalibration4) ###
  * Changes from last run:
    * All turning movements are permitted, even when there is a dedicated turning movement phase
    * 20.5' effective PCU length (trucks x1.5)
    * Turning movement follow-up times are 2.0 sec (AT2+), 2.22 sec (AT1) and 2.67 (AT0)
  * Convergence: Min = xxx, Max = xxx, Mean = xxx
  * Runtime: Approx. xxx hours to do xxx iterations
  * RMSE: Links = xxx% (xxxx counts), Movements = xx% (xxxx counts)
  * GEH: Links = xxx, Movements = xxx
  * VMT = xxx, VHT (3:30-6:30pm) = xxx hours
  * Average Speed (VMT/VHT) = xxx mph
  * Overall Vol/Count Ratio: Links = xxx, Movements = xxx
  * Observed Gridlock: xxx
  * Link to Validation Spreadsheets:  xxx
  * Observations:
    1. Model run completed on PB computers

### sf\_oct31\_V24 (finalCalibration5) ###
  * Changes from last run:
    * All turning movements are permitted, unless they have a dedicated signal phase (in which case turn is protected movement)
    * 21' effective PCU length (trucks x1.5)
    * Turning movement follow-up times are 2.0 sec (AT2+), 2.11 sec (AT1) and 2.22 (AT0)
  * Convergence: Min = 0.464949%, Max = 10.5833%, Mean = 4.44329%
  * Runtime: Approx. 32.33 hours to do 70 iterations
  * RMSE: Links = 51% (1740 counts), Movements = 76% (7643 counts)
  * GEH: Links = 6.32, Movements = 4.28
  * VMT = 1,720,317, VHT (3:30-6:30pm) = 78,768 hours
  * Average Speed (VMT/VHT) = 21.8 mph
  * Overall Vol/Count Ratio: Links = 0.8512, Movements = 0.8741
  * Observed Gridlock: No gridlock at 70 iterations, but heavy congestion accumulates and clears in later periods.
  * Link to Validation Spreadsheets:  [Reset Speed Flow v24 - Final Calibration 5 - Final Calibration Run](http://dta.googlecode.com/files/sf_nov01_V24_Reports.zip)
  * Observations:
    1. Long queues develop for many blocks along key arteries.
    1. Lots of congestion around Battery and Market.  For future runs will need to shift 8 seconds from market St green time to Battery/1st.
    1. Lane configurations for Bay Bridge entrances at 1st and Essex need to be adjusted.  Need to adjust response time factor to account for merging as well.

### pb\_nov1\_NetChg (Network Change Sensitivity Test) ###
  * Changes from last run:
    * Some slight changes to signals and bus dwell times vs. V24
    * 5-block section of Sunset Blvd has one lane removed in each direction
    * Dynamic Path Search was used in the DTA
  * Convergence: Min = 0.471757%, Max = 9.73225%, Mean = 4.74552%
  * Runtime: Approx. 51.13 hours to do 80 iterations (moved to a faster computer at iteration 64)
  * RMSE: Links = 51% (1740 counts), Movements = 73% (7643 counts)
  * GEH: Links = 6.23, Movements = 4.22
  * VMT = 1,712,952, VHT (3:30-6:30pm) = 82,294 hours
  * Average Speed (VMT/VHT) = 20.8 mph
  * Overall Vol/Count Ratio: Links = 0.8283, Movements = 0.8614
  * Observed Gridlock: None.  Heavy congestion in some areas, but no total gridlock.
  * Link to Validation Spreadsheets:  [Sensitivity Test for Small Network Change with Dynamic Path Search](http://dta.googlecode.com/files/pb_nov1_NetChg_Reports.zip)
  * Observations:
    1. Convergence looks very different than without dynamic path search.  There is a second peak in the relative gaps around 60 iterations where the later time periods begin to break up the congestion and choose better paths.
    1. Some heavy congestion at Broadway and Battery.  Maybe worth checking to see if a signal is causing this since there's not as much congestion anywhere else in the CBD.
    1. Still seem to have issues at I80W off-ramp to Freemont.  This area gets very heavily congested toward the end of the simulation time.

### pb\_nov8\_V25 ###
  * Changes from last run:
    * Same as SF's V25 run but with 0.8 RTF on freeways in AT0 and AT1
  * Convergence: Min = 0.473007%, Max = 6.56926%, Mean = 3.19799%
  * Runtime: Approx. 53.16 hours to do 85 iterations
  * RMSE: Links = 51% (1740 counts), Movements = 74% (7643 counts)
  * GEH: Links = 6.17, Movements = 4.22
  * VMT = 1,721,058, VHT (3:30-6:30pm) = 79,246 hours
  * Average Speed (VMT/VHT) = 21.7 mph
  * Overall Vol/Count Ratio: Links = 0.8376, Movements = 0.8643
  * Observed Gridlock: None.
  * Link to Validation Spreadsheets:  [PB Test with Lower RTF on Freeways Downtown](http://dta.googlecode.com/files/pb_nov8_V25_Reports.zip)
  * Observations:
    1. Not as much congestion in this test.  Lowering the response time on freeways in/near the CBD really clears up some areas where we were seeing congestion in previous tests.
    1. The convergence was still a bit messy with this one.  There were three separate peaks in the relative gap: one at around 20 iterations, another at about 42 iterations, and one at about 63 iterations.  Hopefully the newer version of Dynameq will help get rid of some of this odd behavior so that we reach convergence sooner.  Having to run this out past 80 iterations means a long time to do each test.

### resetspeedflow\_v24\_Dyn26 ###
  * Changes from last run:
    * Same as V25 w/Dwell but running in Dynameq 2.6.0
  * Convergence: Min = 0.274272%, Max = 6.19217%, Mean = 2.66666%
  * Runtime: Approx. 108.8 hours (4.53 days) to do 100 iterations
  * RMSE: Links = 53% (1740 counts), Movements = 76% (7643 counts)
  * GEH: Links = 6.30, Movements = 4.23
  * VMT = 1,701,490, VHT (3:30-6:30pm) = 83,919 hours
  * Average Speed (VMT/VHT) = 20.27 mph
  * Overall Vol/Count Ratio: Links = 0.8332, Movements = 0.8901
  * Observed Gridlock: None.
  * Link to Validation Spreadsheets:  [SF Final Calibration Test (V24 w/ Dwell on Dynameq 2.6.0)](http://dta.googlecode.com/files/sf_nov13_V24wDwell_Dyn26_Reports.zip)
  * Observations:
    1. Some congestion in the CBD around Columbus, but anything bad enough to cause gridlock.
    1. There were some odd jumps in the relative gaps in later iterations, but it looks converged at 100 iterations.

### pb\_nov15\_300p\_netchg3 ###
  * Changes from last run:
    * Same as SF Reset Speed Flow V24 w/ Dwell but Sunset has 1 fewer lane in each direction from Ortega to Taraval
  * Convergence: Min = 0.272598%, Max = 6.98232%, Mean = 2.9929%
  * Runtime: Approx. 56.95 hours (2.37 days) to do 80 iterations
  * RMSE: Links = 54% (1740 counts), Movements = 78% (7643 counts)
  * GEH: Links = 6.38, Movements = 4.29
  * VMT = 1,701,676, VHT (3:30-6:30pm) = 85,021 hours
  * Average Speed (VMT/VHT) = 20.01 mph
  * Overall Vol/Count Ratio: Links = 0.8265, Movements = 0.8815
  * Observed Gridlock: None.
  * Link to Validation Spreadsheets:  [PB Small Network Change Test w/ SF Final (V24 w/ Dwell in Dynameq 2.6.0) as the Base](http://dta.googlecode.com/files/pb_nov15_NetChg13_Reports.zip)
  * Observations:
    1. Some congestion in the CBD around Columbus, but anything bad enough to cause gridlock.
    1. There were some odd jumps in the relative gaps in later iterations, but it looks converged at 80 iterations.
    1. More detailed analysis of changes in flow and travel times on each link will be used for the sensitivity analysis.

### sf\_brt\_scenario ###
  * Changes from last run:
    * BRT center lane on Mission from 14th St to Cesar Chavez, lanes on Mission and South Van Ness adjusted
  * Convergence: Min = xx%, Max = xx%, Mean = xx%
  * Runtime: Approx. xx hours (xx days) to do xx iterations
  * RMSE: Links = 52% (1740 counts), Movements = 76% (7643 counts)
  * GEH: Links = 6.23, Movements = 4.26
  * VMT = 1,703,312, VHT (3:30-6:30pm) = 84,000 hours
  * Average Speed (VMT/VHT) = 20.28 mph
  * Overall Vol/Count Ratio: Links = 0.8496, Movements = 0.8932
  * Observed Gridlock: None.
  * Link to Validation Spreadsheets:  [SF BRT Scenario Test](http://dta.googlecode.com/files/sf_BRTScenario_Reports.zip)
  * Observations:
    1. 

### pb\_nov15\_futdem ###
  * Changes from last run:
    * 2012 network with 2040 demand
  * Convergence: Min = 0.357%, Max = 21.7%, Mean = 8.87%
  * Runtime: Approx. 101.8 hours (4.24 days) to do 130 iterations
  * RMSE: Links = 52% (1740 counts), Movements = 79% (7643 counts)
  * GEH: Links = 6.13, Movements = 4.14
  * VMT = 1,909,226, VHT (3:30-6:30pm) = 113,254 hours
  * Average Speed (VMT/VHT) = 16.86 mph
  * Overall Vol/Count Ratio: Links = 0.8871, Movements = 0.9584
  * Observed Gridlock: Some around Columbus, Turk, and links feeding onto I-80, but it clears by the end of the simulation time
  * Link to Validation Spreadsheets:  [PB Future Demand Scenario Test](http://dta.googlecode.com/files/pb_nov15_FutDem_Reports.zip)
  * Observations:
    1. Heavy congestion, but it does clear by the end of the simulation.
    1. Even after 130 iterations, it wasn't very converged because of the high levels of congestion.

### pb\_nov19\_RS ###
  * Changes from last run:
    * Random Seed Test (Random Seed =2)
  * Convergence: Min = 0.307%, Max = 7.90%, Mean = 3.37%
  * Runtime: Approx. 46.70 hours (1.94 days) to do 80 iterations
  * RMSE: Links = 53% (1740 counts), Movements = 77% (7643 counts)
  * GEH: Links =  6.30, Movements = 4.27
  * VMT = 1,710,198, VHT (3:30-6:30pm) = 85,906 hours
  * Average Speed (VMT/VHT) = 19.9 mph
  * Overall Vol/Count Ratio: Links = 0.8467, Movements = 0.8988
  * Observed Gridlock: None.
  * Link to Validation Spreadsheets:  [PB Random Seed Test Reports](http://dta.googlecode.com/files/pb_nov19_RandomSeed_Reports.zip)
  * Observations:
    1. Flow values vary more than we would expect in some areas.

### sf\_nov21\_pricing ###
  * Changes from last run:
    * Congestion Pricing Application Test
  * Convergence: Min = 0.0501%, Max = 5.51%, Mean = 2.03%
  * Runtime: Approx. 50.6 hours (2.11 days) to do 70 iterations
  * RMSE: Links = 68% (1740 counts), Movements = 98% (7643 counts)
  * GEH: Links =  8.45, Movements = 5.22
  * VMT = 1,443,680, VHT (3:30-6:30pm) = 67,866 hours
  * Average Speed (VMT/VHT) = 21.3 mph
  * Overall Vol/Count Ratio: Links = 0.5565, Movements = 0.6454
  * Observed Gridlock: None.
  * Link to Validation Spreadsheets:  [SF Congestion Pricing Application Test Reports](http://dta.googlecode.com/files/sf_Pricing_Reports.zip)
  * Observations:
    1. Demand is much lower, so there is little to no congestion.
    1. Even the CBD is pretty clear with heavy congestion in only a few places and dissipating quickly.
    1. Flow moves away from the CBD to take paths that avoid going through that area.