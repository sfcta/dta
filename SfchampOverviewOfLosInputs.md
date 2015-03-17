

# Tour Mode Choice #

SF-CHAMP’s tour mode choice model incorporates the following Level of Service variables.  Coefficient estimation is segmented by purpose, and work and other purpose coefficients are shown; Grade School, High School, College, and Work-based coefficients are not shown.  Tour mode choice variables incorporate level of service variables for both trips to and from the primary tour destination.

Variables are in <font color='green'>green if they relate to transit modes</font>, they are in <font color='blue'>blue if they relate to auto modes</font>, and they are black if they relate to both.  Variables related to non-motorized modes are not shown here because non-motorized mode LOS currently does not relate to roadway speeds.

<table cellpadding='3' border='1' cellspacing='0'>
<thead>
<blockquote><tr>
<blockquote><th width='200'>Variable Group</th>
<th width='300'>Coefficient</th>
<th>Work Tours</th>
<th>Other Tours</th>
</blockquote></tr>
<tr>
<blockquote><th>Estimate</th>
<th>Ratio to IVT</th>
<th>Estimate</th>
<th>Ratio to IVT</th>
</blockquote></tr>
</thead>
<tbody align='right'>
<tr>
<td align='left'>Travel Time & Cost</td>
<td align='left'>In Vehicle Time</td>
<td>-0.0105<b></td></b><td>--</td>
<td>-0.0087<b></td></b><td>--</td>
</tr>
<tr>
<td align='left'>Travel Cost (including operating cost, tolls for toll modes, and fares for transit and taxi</td>
<td align='center'><i>Determined by Traveler's Value of Time</i></td>
</tr>
<tr>
<td align='left'><font color='green'>Wait (Initial and Transfer) Time</font></td>
<td>-0.0234<b></td></b><td>2.2</td>
<td>-0.0230<b></td></b><td>2.6</td>
</tr>
<tr>
<td align='left'><font color='green'>Origin (OTAZ-station) Walk Time</font></td>
<td>-0.0192<b></td></b><td>1.8</td>
<td>-0.0156<b></td></b><td>1.8</td>
</tr>
<tr>
<td align='left'><font color='green'>Dest Walk (station-primary DTAZ) Time</font></td>
<td>-0.0566<b></td></b><td>5.4</td>
<td>-0.0461<b></td></b><td>5.3</td>
</tr>
<tr>
<td align='left'><font color='green'>Transfer Walk Time</font></td>
<td>-0.0782<b></td></b><td>7.4</td>
<td>-0.0800</td>
<td>9.2</td>
</tr>
<tr>
<td align='left'>Convenience & Reliability</td>
<td align='left'><font color='green'>Number of Transfers</font></td>
<td>-0.0815<b></td></b><td>7.8</td>
<td>-0.0524</td>
<td>6.0</td>
</tr>
<tr>
<td align='left'><font color='green'>Drive to Transit Access Ratio</font></td>
<td>-0.8380<b></td></b><td>79.8</td>
<td>-1.0900<b></td></b><td>124.9</td>
</tr>
<tr>
<td align='left'><font color='blue'>Drive Distance with VC>0.8</font></td>
<td>-0.0224<b></td></b><td>2.1</td>
<td>-0.0352<b></td></b><td>4.0</td>
</tr>
<tr>
<td align='left'><font color='blue'>Drive Park Availability Index</font></td>
<td>-0.2400<b></td></b><td>22.9</td>
<td>-0.2440<b></td></b><td>27.9</td>
</tr>
<tr>
<td align='left'>Transit/Taxi Environment Factors</td>
<td align='left'><font color='green'>Trn Dest End Walk AbsRise (00 ft)</font></td>
<td>-0.1710</td>
<td>16.3</td>
<td>--</td>
<td>--</td>
</tr>
<tr>
<td align='left'><font color='green'>Trn Origin End Walk Ln(PopDen)</font></td>
<td>0.0778<b></td></b><td>-7.4</td>
<td>--</td>
<td>--</td>
</tr>
<tr>
<td align='left'><font color='green'>Trn Origin End Walk Indirectness</font></td>
<td>--</td>
<td>--</td>
<td>-0.0873</td>
<td>10.0</td>
</tr>
<tr>
<td align='left'><font color='green'>Trn Dest End Walk Ln(EmpDen)</font></td>
<td>0.1390<b></td></b><td>-13.2</td>
<td>0.1310<b></td></b><td>-15.0</td>
</tr>
<tr>
<td align='left'><font color='blue'>Taxi Origin Ln(EmpDen)</font></td>
<td>0.0814</td>
<td>-7.8</td>
<td>0.3240</td>
<td>-37.1</td>
</tr>
</tbody>
</table></blockquote>

The cost coefficients are related directly to the in vehicle time coefficients through a simulated Value of Time variable that is sampled for each individual traveler.  The sampling is performed using a log normal distribution informed by (what dataset), and non-work Value of Time is assessed at two thirds that of the Value of Time for work tours.

# Trip Mode Choice #

SF-CHAMP’s trip mode choice model functions similarly.  The following variables represent LOS in the trip mode choice models.  As with the Tour Mode Choice model, coefficient estimation is segmented by purpose, and work and other purpose coefficients are shown; Grade School, High School, College, and Work-based coefficients are not shown.  Some variables have no coefficient listed for either the work or other purpose; this is because the variable is significant in one of the other purpose models.

<table cellpadding='3' border='1' cellspacing='0'>
<thead>
<blockquote><tr>
<blockquote><th width='200'>Variable Group</th>
<th width='300'>Coefficient</th>
<th>Work Tours</th>
<th>Other Tours</th>
</blockquote></tr>
<tr>
<blockquote><th>Estimate</th>
<th>Ratio to IVT</th>
<th>Estimate</th>
<th>Ratio to IVT</th>
</blockquote></tr>
</thead>
<tbody align='right'>
<tr>
<td align='left'>Travel Time & Cost</td>
<td align='left'>In Vehicle Time</td>
<td>-0.0157</td>
<td>--</td>
<td>-0.0185</td>
<td>--</td>
</tr>
<tr>
<td align='left'>Travel Cost (including operating cost, tolls for toll modes, and fares for transit and taxi</td>
<td align='center'><i>Determined by Traveler's Value of Time</i></td>
</tr>
<tr>
<td align='left'><font color='green'>Wait (Initial and Transfer) Time</font></td>
<td>-0.0345</td>
<td>2.2</td>
<td>-0.0499</td>
<td>2.7</td>
</tr>
<tr>
<td align='left'><font color='green'>Origin (OTAZ-station) Walk Time</font></td>
<td>-0.0283</td>
<td>1.8</td>
<td>-0.0314</td>
<td>1.7</td>
</tr>
<tr>
<td align='left'><font color='green'>Dest Walk (station-primary DTAZ) Time</font></td>
<td>-0.0848</td>
<td>5.4</td>
<td>-0.0999</td>
<td>5.4</td>
</tr>
<tr>
<td align='left'><font color='green'>Transfer Walk Time</font></td>
<td>-0.1162</td>
<td>7.4</td>
<td>-0.1702</td>
<td>9.2</td>
</tr>
<tr>
<td align='left'>Convenience & Reliability</td>
<td align='left'><font color='green'>Number of Transfers</font></td>
<td>-0.1225</td>
<td>7.8</td>
<td>-0.1202</td>
<td>6.5</td>
</tr>
<tr>
<td align='left'><font color='green'>Drive to Transit Access Ratio</font></td>
<td>-0.4350</td>
<td>27.7</td>
<td>-1.950</td>
<td>105.4</td>
</tr>
<tr>
<td align='left'>Transit/Taxi Environment Factors</td>
<td align='left'><font color='green'>Trn Origin End Walk AbsRise (00 ft)</font></td>
<td>--</td>
<td>--</td>
<td>-0.0462</td>
<td>2.5</td>
</tr>
<tr>
<td align='left'><font color='green'>Trn Destination End Walk AbsRise (00 ft)</font></td>
<td>--</td>
<td>--</td>
<td>--</td>
<td>--</td>
</tr>
<tr>
<td align='left'><font color='green'>Trn Origin End Walk Ln(EmpDen)</font></td>
<td>0.1410</td>
<td>-9.0</td>
<td>0.1080</td>
<td>-5.8</td>
</tr>
<tr>
<td align='left'><font color='green'>Trn Destination End Walk Ln(EmpDen)</font></td>
<td>0.1910</td>
<td>-12.2</td>
<td>0.0367</td>
<td>-2.0</td>
</tr>
<tr>
<td align='left'><font color='green'>Trn Origin End Walk Indirectness</font></td>
<td>--</td>
<td>--</td>
<td>-0.7810</td>
<td>42.2</td>
</tr>
<tr>
<td align='left'><font color='green'>Trn Destination End Walk Indirectness</font></td>
<td>--</td>
<td>--</td>
<td>--</td>
<td>--</td>
</tr>
<tr>
<td align='left'><font color='green'>Trn Non-Work Land Use Entropy at Dest</font></td>
<td>0.0018</td>
<td>-0.1</td>
<td>--</td>
<td>--</td>
</tr>
<tr>
<td align='left'><font color='blue'>Taxi Origin Ln(EmpDen)</font></td>
<td>0.0789</td>
<td>-5.0</td>
<td>0.0789</td>
<td>-4.3</td>
</tr>
</tbody>
</table></blockquote>

# Level of Service in Other SF-CHAMP Submodels #
Since Level of Service variables are directly fed into the SF-CHAMP mode choice models, they feed into other submodels as well via logsums, or general measures of accessibility:
  * The workplace choice submodel incorporates the tour mode choice logsum.  This submodel is segmented by income categories, but all categories use the same coefficients on the mode choice logsum.
  * The destination choice submodel also incorporates the tour mode choice logsum for College, Other and Work-Based purposes, but not for Grade School or High School purposes.
  * The tour generation submodel (or day pattern submodel) incorporates the tour mode choice logsum to the chosen work location into the utility of work tours, as well as the destination choice logsum at work into the utility of work-based subtours.  Additionally, destination choice logsums are incorporated into the utility of any additional tours and into the utility of making intermediate stops on any tours.
  * The tour time of day submodel takes the day pattern structure into account in modeling the time of days that tours are taken.
  * The intermediate stop submodel directly includes Level of Service variables, incorporating the additional travel time incurred by including the intermediate stop.