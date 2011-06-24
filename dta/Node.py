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

class Node:
    """
    Base class that represents a node in a network.
    
    """
    
    # Defaults
    DEFAULT_LABEL = "label %d"
    DEFAULT_LEVEL = 0

    # Geometry types - how is this used?  Why is the centroid not in the type list?
    GEOMETRY_TYPE_INTERSECTION      = 1
    GEOMETRY_TYPE_JUNCTION          = 2
    GEOMETRY_TYPE_VIRTUAL           = 99 
    GEOMETRY_TYPE_CENTROID          = 100
    GEOMETRY_TYPES                  = [GEOMETRY_TYPE_INTERSECTION,
                                       GEOMETRY_TYPE_JUNCTION,
                                       GEOMETRY_TYPE_VIRTUAL]
    
    def __init__(self, id, x, y, label=None, level=None):
        """
        Constructor.
        
         * id is a unique identifier (unique within the containing network), an integer
         * x and y are coordinates (what units?)
         * label is a string, for readability.  If None passed, will default to "label [id]"
         * level is for vertical alignment.  More details TBD.  If None passed, will use default.  
        
        """
        self.id     = id
        self.x      = x
        self.y      = y
        
        if label:
            self.label = label
        else:
            self.label = Node.DEFAULT_LABEL % self.id
            
        if level:
            self.level = level
        else:
            self.level = Node.DEFAULT_LEVEL
        
        # Dictionary of Link objects, with key = angle between the link and this (x,y) and (x+1,y).
        self.incoming_links = {}
        self.outgoing_links = {}