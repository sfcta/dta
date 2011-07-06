__copyright__   = "Copyright 2011 SFCTA"
__license__     = """
    This file is part of DTA.

    DTA is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    DTA is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with DTA.  If not, see <http://www.gnu.org/licenses/>.
"""
import dta

USAGE = """

 python createSFNetworkFromCubeNetwork.py
 
 """
 
if __name__ == '__main__':
    
    dta.setupLogging("dtaInfo.log", "dtaDebug.log", logToConsole=True)

    
    # The Geary network was created in an earlier Phase of work, so it already exists as
    # a Dynameq DTA network.  Initialize it from the Dynameq text files.
    gearynet_dta = dta.DynameqNetwork(dir=".", file_prefix="Base_Final")
    gearynet_dta.write(dir="test", file_prefix="geary_")
    
    gearyscenario = dta.DynameqScenario(dir=".", file_prefix="Base_Final")
    gearyscenario.write(dir="test", file_prefix="geary_")
    exit(0)
    
    # The rest of San Francisco currently exists as a Cube network.  Initialize it from
    # the Cube network files (which have been exported to dbfs.)
    sanfrancisco_cube = dta.CubeNetwork(dir="sfnet")
    
    # Merge them together
    sanfrancisco_dta = gearynet_dta
    sanfrancisco_dta.merge(sanfrancisco_cube)
    
    # Write the result.  sanfrancisco_dta is a DynameqNetwork
    sanfrancisco_dta.write(dir = ".", file_prefix="SanFrancisco_")
    