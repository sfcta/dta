The base of this code is designed to be fairly software agnostic.  However, at the end of the day in order to be useful it needs to be able to interface with some of the specific formatting and nuances of actual dta software.  For now, the team at SFCTA has chosen the Dynameq DTA package made by INRO, so most of the plug-ins are related to Dynameq.  However, other extensions are possible and welcome.

> ## Dynameq ##

SFCTA has a Dynameq license large enough to cover our entire city.  The following table summarizes various Dynameq Versions so we can keep track of them.

|**Version**|**CPU**|**Features**|**Projects**|**Format Change?**|
|:----------|:------|:-----------|:-----------|:-----------------|
|2.0.2|32bit| - |Geary|Has Events|
|2.1.0|32bit| - | - | yes |
|2.5.0 Beta|64bit| NOT compatible with 2.1 | - | - |
|2.5.0.2 Beta|64bit and 32bit|compatible with 2.1 release, 32-bit version has arcGIS runtime service pack 2| - | network format plays perfectly with 2.1.0 :-) |
|test-2.6.0.1b|64bit and 32bit|features a next-gen, less-gridlock-prone traffic flow model that will be adopted in future Dynameq releases| Final DTA Anyway Validation | network format is fine |