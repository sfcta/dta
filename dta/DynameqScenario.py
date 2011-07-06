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
import os
from .DtaError import DtaError
from .Scenario import Scenario
from .VehicleClassGroup import VehicleClassGroup
from .VehicleType import VehicleType

class DynameqScenario(Scenario):
    """
    A Dynameq Scenario.
    """
    
    SCENARIO_FILE   = '%s_scen.dqt'

    def __init__(self, dir, file_prefix):
        """
        Constructor. Reads the scenario in the given *dir* with the given *file_prefix*.
        
        """
        
        # scenario file processing
        scenariofile = os.path.join(dir, DynameqScenario.SCENARIO_FILE % file_prefix)
        if not os.path.exists(scenariofile):
            raise DtaError("Scenario file %s does not exist" % scenariofile)
        
        
        (startTime, endTime) = self._readStudyPeriodFromScenarioFile(scenariofile)
        Scenario.__init__(self, startTime, endTime)
        
        try:
            for (eventTime, eventDescription) in self._readEventsFromScenarioFile(scenariofile):
                self.addEvent(eventTime, eventDescription)
        except StopIteration:
            pass
                
        try:
            for vehicleClassName in self._readVehicleClassesFromScenarioFile(scenariofile):
                self.addVehicleClass(vehicleClassName)
        except StopIteration:
            pass
        
        try:
            for vehicleType in self._readVehicleTypesFromScenarioFile(scenariofile):
                self.addVehicleType(vehicleType)
        except StopIteration:
            pass
            
        for vehicleClassGroup in self._readVehicleClassGroupsFromScenarioFile(scenariofile):
            self.addVehicleClassGroup(vehicleClassGroup)
                 
        # TODO: generalized cost   
        # for generalizedCost in self._readGeneralizedCostFromScenarioFile(scenariofile):
        #    self.addGeneralizedCost(generalizedCost)

    def write(self, dir, file_prefix):
        scenariofile = os.path.join(dir, DynameqScenario.SCENARIO_FILE % file_prefix)
        
        scenariofile_object = open(scenariofile, "w")
        self._writeStudyPeriodToScenarioFile(scenariofile_object)
        self._writeEventsToScenarioFile(scenariofile_object)
        self._writeVehicleClassesToScenarioFile(scenariofile_object)
        self._writeVehicleTypesToScenarioFile(scenariofile_object)
        self._writeVehicleClassGroupsFromScenarioFile(scenariofile_object)
        
    def _readStudyPeriodFromScenarioFile(self, scenariofile):
        """ 
        Reads the study period and returns the start and times as datetime.time objects
        """
        lines = open(scenariofile, "r")
        curLine = lines.next().strip()
        try:
            while curLine !="STUDY_PERIOD":
                curLine = lines.next().strip()
        except StopIteration:
            raise DtaError("Scenario file %s: cannot locate the STUDY_PERIOD section" % scenariofile)

        curLine = lines.next().strip()
        while curLine[0] == "*": # if its a comment, skip
            curLine = lines.next().strip()
            
        fields  = curLine.split()        
        time1 = fields[0].split(":")
        time2 = fields[1].split(":")
        
        lines.close()
        
        return (datetime.time(hour=int(time1[0]), minute=int(time1[1])),
                datetime.time(hour=int(time2[0]), minute=int(time2[1])))
    
    def _writeStudyPeriodToScenarioFile(self, scenariofile_object):
        """
        Write version of _readStudyPeriodFromScenarioFile().  *scenariofile_object* is the file object,
        ready for writing.
        """
        scenariofile_object.write("STUDY_PERIOD\n")
        scenariofile_object.write("*   start      end\n")
        scenariofile_object.write("    %02d:%02d    %02d:%02d\n" % (self.startTime.hour, self.startTime.minute,
                                                                    self.endTime.hour,   self.endTime.minute))
        
    def _readEventsFromScenarioFile(self, scenariofile):
        """
        Generator function, yields (eventTime, eventDescription) to the caller
        """
        lines = open(scenariofile, "r")
        curLine = lines.next().strip()
        try:
            while curLine !="EVENTS":
                curLine = lines.next().strip()
        except StopIteration:
            raise DtaError("Scenario file %s: cannot locate the EVENTS section" % scenariofile)

        curLine = lines.next().strip()
        while curLine[0] == "*": # if its a comment, skip
            curLine = lines.next().strip()
            
        while not curLine == "VEH_CLASSES":
            fields  = curLine.split()
            
            timestrs = fields[0].split(":")            
            yield (datetime.time(hour=int(timestrs[0]), minute=int(timestrs[1])), fields[1])
            
            curLine = lines.next().strip()
        
        lines.close()
        raise StopIteration
    
    def _writeEventsToScenarioFile(self, scenariofile_object):
        """
        Write version of _readEventsFromScenarioFile().  *scenariofile_object* is the file object,
        ready for writing.
        """
        scenariofile_object.write("EVENTS\n")
        scenariofile_object.write("*    time                                                     desc\n")
        for eventTime in sorted(self.events.keys()):
            scenariofile_object.write("    %02d:%02d %56s\n" % (eventTime.hour, eventTime.minute,
                                                                self.events[eventTime]))
                
    def _readVehicleClassesFromScenarioFile(self, scenariofile):
        """
        Generator function, yields vehicleClassName (strings) to the caller
        """
        lines = open(scenariofile, "r")
        curLine = lines.next().strip()
        try:
            while curLine !="VEH_CLASSES":
                curLine = lines.next().strip()
        except StopIteration:
            raise DtaError("Scenario file %s: cannot locate the VEH_CLASSES section" % scenariofile)

        curLine = lines.next().strip()
        while curLine[0] == "*": # if its a comment, skip
            curLine = lines.next().strip()
            
        while not curLine == "VEH_TYPES":
            fields  = curLine.split()
            yield fields[0]
            
            curLine = lines.next().strip()
        
        lines.close()
        raise StopIteration
        
    def _writeVehicleClassesToScenarioFile(self, scenariofile_object):
        """
        Write version of _readVehicleClassesFromScenarioFile().  *scenariofile_object* is the file object,
        ready for writing.
        """
        scenariofile_object.write("VEH_CLASSES\n")
        scenariofile_object.write("*      class_name\n")
        for vehicleClassName in self.vehicleClassNames:
            scenariofile_object.write("%17s" % vehicleClassName)
        
    def _readVehicleTypesFromScenarioFile(self, scenariofile):
        """
        Generator function, yields VehicleType objects to the caller        
        """
        lines = open(scenariofile, "r")
        curLine = lines.next().strip()
        try:
            while curLine !="VEH_TYPES":
                curLine = lines.next().strip()
        except StopIteration:
            raise DtaError("Scenario file %s: cannot locate the VEH_TYPES section" % scenariofile)

        curLine = lines.next().strip()
        while curLine[0] == "*": # if its a comment, skip
            curLine = lines.next().strip()
            
        while not curLine == "VEH_CLASS_GROUPS":
            fields  = curLine.split()
            vehicleClassName    = fields[0]
            vehicleTypeName     = fields[1]
            length              = float(fields[2])
            responseTime        = float(fields[3])
            yield VehicleType(vehicleTypeName, vehicleClassName, length, responseTime)
            
            curLine = lines.next().strip()
        
        lines.close()
        raise StopIteration
    
    def _writeVehicleTypesToScenarioFile(self, scenariofile_object):
        """
        Write version of _readVehicleTypesFromScenarioFile().  *scenariofile_object* is the file object,
        ready for writing.
        """
        scenariofile_object.write("VEH_TYPES\n")
        scenariofile_object.write("*class_name type_name   length res_time\n")
        for vehicleTypeName in sorted(self.vehicleTypes.keys()):
            scenariofile_object.write("%11s %9s %8f %8f\n" % (self.vehicleTypes[vehicleTypeName].className,
                                                              vehicleTypeName,
                                                              self.vehicleTypes[vehicleTypeName].length,
                                                              self.vehicleTypes[vehicleTypeName].responseTime))
        
    def _readVehicleClassGroupsFromScenarioFile(self, scenariofile):
        """
        Generator function, yields VehicleClassGroup objects to the caller        
        """
        lines = open(scenariofile, "r")
        curLine = lines.next().strip()
        try:
            while curLine !="VEH_CLASS_GROUPS":
                curLine = lines.next().strip()
        except StopIteration:
            raise DtaError("Scenario file %s: cannot locate the VEH_TYPES section" % scenariofile)

        curLine = lines.next().strip()
        while curLine[0] == "*": # if its a comment, skip
            curLine = lines.next().strip()
            
        while not curLine == "GENERALIZED_COSTS":
            fields  = curLine.split()
            groupName     = fields[0]
            classDef      = fields[1]
            colorCode     = fields[2]
            yield VehicleClassGroup(groupName, classDef, colorCode)
            
            curLine = lines.next().strip()
        
        lines.close()
        raise StopIteration
    
    def _writeVehicleClassGroupsFromScenarioFile(self, scenariofile_object):
        """
        Write version of _readVehicleClassGroupsFromScenarioFile().  *scenariofile_object* is the file object,
        ready for writing.
        """
        scenariofile_object.write("VEH_CLASS_GROUPS\n")
        scenariofile_object.write("*      name   class      color\n")
        for groupname in sorted(self.vehicleClassGroups.keys()):
            scenariofile_object.write("%11s %7s %10s\n" % (groupname,
                                                           self.vehicleClassGroups[groupname].classDefinitionString,
                                                           self.vehicleClassGroups[groupname].colorCode))
        