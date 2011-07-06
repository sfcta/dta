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

from .Centroid import Centroid
from .Connector import Connector
from .DtaError import DtaError
from .Link import Link
from .VirtualNode import VirtualNode

class VirtualLink(Link):
    """
    A VirtualLink is a Link that connects a :py:class:`Centroid` with
    a :py:class:`Connector`.
    
    """
    
    # Dummy values to use if you must
    REVERSE         = -1
    FACILITY_TYPE   = 100
    LENGTH          = 0
    FFSPEED         = 30
    RESPONSE_FACTOR = 0
    LENGTH_FACTOR   = 0
    LANES           = 1
    RABOUT          = 0
    LEVEL           = 0
        
    def __init__(self, id, nodeA, nodeB, label, connector):
        """
        Constructor. Verifies one node is a :py:class:`Centroid` and the
        other node is a :py:class:`VirtualNode`.
        
         * *id* is a unique identifier (unique within the containing network), an integer
         * *nodeA*, *nodeB* are :py:class:`Node` instances
         * *label* is a string, or None 
         * *connector* is a :py:class:`Connector` instance
        """
        
        if not isinstance(nodeA, Centroid) and not isinstance(nodeB, Centroid):
            raise DtaError("Attempting to initialize a VirtualLink without a Centroid: %s - %s" % 
                           (str(nodeA), str(nodeB)))

        if not isinstance(nodeA, VirtualNode) and not isinstance(nodeB, VirtualNode):
            raise DtaError("Attempting to initialize a VirtualLink without a VirtualNode: %s - %s" % 
                           (str(nodeA), str(nodeB)))
       
        Link.__init__(self, id, nodeA, nodeB, label)

        if not isinstance(connector, Connector):
            raise DtaError("Attempting to initialize a VirtualLink without a Connector: %s" % 
                           str(connector))
        self._connector = connector
       