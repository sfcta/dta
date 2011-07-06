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

import datetime
from .DtaError import DtaError
from .VehicleClassGroup import VehicleClassGroup
from .VehicleType import VehicleType

class Scenario(object):
    """
    Class that represents a DTA Scenario, and all that it entails.
    """
    
    __all__ = ["__init__", "vehicleClassNames"]
    
    def __init__(self, startTime, endTime):
        """
        Constructor.
        
        *startTime* and *endTime* are datetime.time instances.
        """
        self.startTime = startTime
        self.endTime   = endTime
        
        if self.endTime <= self.startTime:
            raise DtaError("Scenario cannot have startTime (%s) >= endTime (%s)" %
                           (str(startTime), str(endTime)))
        
        #: list of Vehicle Class Names
        self.vehicleClassNames  = []
        
        #: Vehicle Type Name (string) -> :py:class:`VehicleType`
        self.vehicleTypes       = {}
        
        #: vehicle class group name (string) -> :py:class:`VehicleClassGroup`
        self.vehicleClassGroups = {}
        
        #: event time (datetime.time) -> description string
        self.events             = {}
        
    def __dir__(self):
        return ["vehicleClassNames", "vehicleTypes"]
    
    def addVehicleClass(self, vehicleClassName):
        """
        *vehicleClassName* is a string
        """
        self.vehicleClassNames.append(vehicleClassName)
        
    def addVehicleType(self, vehicleType):
        """
        *vehicleType* is a :py:class:`VehicleType`
        """
        if not isinstance(vehicleType, VehicleType):
            raise DtaError("Scenario addVehicleTyp() called with a non VehicleType object: %s" % 
                           str(vehicleType))
        
        self.vehicleTypes[vehicleType.name] = vehicleType
        
    def addVehicleClassGroup(self, vehicleClassGroup):
        """
        *vehicleClassGroup* is a :py:class:`VehicleClassGroup` object
        """
        if not isinstance(vehicleClassGroup, VehicleClassGroup):
            raise DtaError("Scenario addVehicleClassGroup() called with a non VehicleClassGroup object: %s" %
                           str(vehicleClassGroup))
            
        self.vehicleClassGroups[vehicleClassGroup.name] = vehicleClassGroup

    def getVehicleClassGroup(self, vehicleClassGroupName):
        """
        Returns the relevant :py:class:`VehicleClassGroup` or throws a :py:class:`DtaError` if not
        found.
        """
        if vehicleClassGroupName in self.vehicleClassGroups:
            return self.vehicleClassGroups[vehicleClassGroupName]
        
        raise DtaError("Scenario VehicleClassGroup named %s not found" % vehicleClassGroupName)
        
    def addEvent(self, eventTime, eventDescription):
        """
        *eventTime* is a datetime.time instance and *description* is a string.
        
        Verifies that *eventTime* is in [startTime, endTime)
        """
        
        if eventTime < self._startTime:
            raise DtaError("Scenario cannot have an event time (%s) < startTime %s" %
                           (str(eventTime), str(self.startTime)))
        
        if eventTime >= self.endTime:
            raise DtaError("Scenario cannot have an event time (%s) >= endTime %s" %
                           (str(eventTime), str(self.endTime)))
        
        self.events[eventTime] = eventDescription