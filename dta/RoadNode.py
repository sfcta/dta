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

class RoadNode(Node):
    """
    A Node subclass that represents a road node in a network.
    
    """
    #: Control types - how is this used?
    CONTROL_TYPE_UNSIGNALIZED       = 0
    CONTROL_TYPE_SIGNALIZED         = 1
    CONTROL_TYPES                   = [CONTROL_TYPE_UNSIGNALIZED,
                                       CONTROL_TYPE_SIGNALIZED]
    

    #: No template: either a signalized or unsignalized junction, where there is no yielding of any
    #: kind, and the permitted capacity is equal to the protected capacity. 
    PRIORITY_TEMPLATE_NONE          = 0
    
    #: All Way Stop Control - an intersection with a stop sign on every approach
    PRIORITY_TEMPLATE_AWSC          = 1
    
    #: Two Way Stop Control - an intersection at which a minor street crosses a major street and
    #: only the minor street is stop-controlled
    PRIORITY_TEMPLATE_TWSC          = 2
    
    #: A junction on a roundabout at which vehicles enter the roundabout. Vehicles entering the
    #: roundabout must yield to those already on the roundabout (by convention in most countries).
    PRIORITY_TEMPLATE_ROUNDABOUT    = 3
    
    #: An uncontrolled (unsignalized) junction at which a minor street must yield to the major street,
    #: which may or may not be explicitly marked with a Yield sign. 
    PRIORITY_TEMPLATE_MERGE         = 4
    
    #: Any signalized intersection (three-leg, four-leg, etc.). For right-side driving, left-turn
    #: movements yield to opposing through traffic and right turns, and right turns yield to the
    #: conflicting through traffic (if applicable). For left-side driving, the rules are the same but reversed.
    PRIORITY_TEMPLATE_SIGNALIZED    = 11
    
    #: For each control type, a list of available Capacity/Priority templates is provided.
    #: Choosing a template from the list will automatically provide follow-up time values with
    #: corresponding permitted capacity values in the movements table below, and define all movement
    #: priority relationships at the node with corresponding gap acceptance values.     
    PRIORITY_TEMPLATES              = [PRIORITY_TEMPLATE_NONE,
                                       PRIORITY_TEMPLATE_AWSC,
                                       PRIORITY_TEMPLATE_TWSC,
                                       PRIORITY_TEMPLATE_ROUNDABOUT,
                                       PRIORITY_TEMPLATE_MERGE,
                                       PRIORITY_TEMPLATE_SIGNALIZED]
        
    def __init__(self, id, x, y, control, priority, label=None, level=None):
        """
        Constructor.
        
         * id is a unique identifier (unique within the containing network), an integer
         * x and y are coordinates (what units?)
         * control is one of Node.CONTROL_TYPE_UNSIGNALIZED or Node.CONTROL_TYPE_SIGNALIZED
         * label is a string, for readability.  If None passed, will default to "label [id]"
         * level is for vertical alignment.  More details TBD.  If None passed, will use default.  
        """
        super(Node, self).__init__(id, x, y,label,level)

        self.control = control
        self.priority = priority