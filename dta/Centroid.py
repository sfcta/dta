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
from .Node import Node

class Centroid(Node):
    """
    A Node subclass that represents a centroid node in a network.
    
    """        
    def __init__(self, id, x, y, label=None, level=None):
        """
        Constructor.
        
         * id is a unique identifier (unique within the containing network), an integer
         * x and y are coordinates (what units?)
         * label is a string, for readability.  If None passed, will default to "label [id]"
         * level is for vertical alignment.  More details TBD.  If None passed, will use default.  
        """        
        Node.__init__(self, id, x, y, geometryType=Node.GEOMETRY_TYPE_CENTROID, label=label, level=level)
