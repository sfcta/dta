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
    
    # The Geary network was created in an earlier Phase of work, so it already exists as
    # a Dynameq DTA network.  Initialize it from the Dynameq text files.
    gearynet_dta = DynameqNetwork()
    
    # The rest of San Francisco currently exists as a Cube network.  Initialize it from
    # the Cube network files (which have been exported to dbfs.)
    sanfrancisco_cube = CubeNetwork()
    
    # Merge them together
    sanfrancisco_dta = gearynet_dta
    sanfrancisco_dta.merge(sanfrancisco_cube)
    
    # Write the result.  sanfrancisco_dta is a DynameqNetwork
    sanfrancisco_dta.write(output_dir = ".", file_prefix="SanFrancisco_")
    