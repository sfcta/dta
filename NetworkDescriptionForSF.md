# Vehicle Types #

**Purpose** : determines max speeds, vehicle length, etc.

  * Autos
  * Trucks (smallish ones...this is SF)
  * Transit:
    * LRT1
    * LRT2
    * Trolley Std
    * Trolley Artic
    * Motor Std
    * Motor Artic
    * Cable Car

[See implementation in the code](http://code.google.com/p/dta/source/browse/scripts/createSFNetworkFromCubeNetwork.py?name=release-1.0#377)

# Vehicle Classes #
These correspond to demand. Initially we will use 4 class groups:
  * Autos that don't pay tolls
  * Autos that pay tolls
  * Trucks that don't pay tolls
  * Trucks that pay tolls

# Class Groups #

**Purpose** : determines lane use privilege.  This is also a RAM-blower...so we need to be careful and only do the ones that we need.

Initially we'lll use:
  * All
  * Prohibited
  * Transit-Only
  * Toll

To consider in future:
  * HOV2, HOV3+
  * No-Trucks
  * Electric vehicles
  * Taxis
  * Scooters/Motorcycles

# Facility Types #

We will map the facility type of our static network to a DTA facility type (were a lower number indicates higher priority) as follows:
| Description | Cube (Static) Facility Type No. | DTA Facility Type No. |
|:------------|:--------------------------------|:----------------------|
| Freeway | 2 | 1 |
| Expressway | 3 | 2 |
| Freeway-Freeway Connector | 1 | 3 |
| Major Arterial | 7 | 4 |
| Super Arterial | 15 | 4 |
| Minor Arterial | 12 | 5 |
| Collector | 4 | 6 |
| Local | 11 | 7 |
| Ramp | 5 | 8 |
| Alley | 9 | 10 |