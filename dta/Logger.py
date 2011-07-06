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

import logging

__all__ = ['DtaLogger', 'setupLogging']


# for all dta logging needs!
DtaLogger = logging.getLogger("DTALogger")


def setupLogging(infoLogFilename, debugLogFilename, logToConsole=True):
    """ 
    Sets up the logger.  The infoLog is terse, just gives the bare minimum of details
    so the network composition will be clear later.
    The debuglog is very noisy, for debugging.
        
    Pass none to either.
    Spews it all out to console too, if logToConsole is true.
    """
    # create a logger
    DtaLogger.setLevel(logging.DEBUG)

    if infoLogFilename:
        infologhandler = logging.StreamHandler(open(infoLogFilename, 'w'))
        infologhandler.setLevel(logging.INFO)
        infologhandler.setFormatter(logging.Formatter('%(message)s'))
        DtaLogger.addHandler(infologhandler)
    
    if debugLogFilename:
        debugloghandler = logging.StreamHandler(open(debugLogFilename,'w'))
        debugloghandler.setLevel(logging.DEBUG)
        debugloghandler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s', '%Y-%m-%d %H:%M'))
        DtaLogger.addHandler(debugloghandler)
    
    if logToConsole:
        consolehandler = logging.StreamHandler()
        consolehandler.setLevel(logging.DEBUG)
        consolehandler.setFormatter(logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s'))
        DtaLogger.addHandler(consolehandler)
        
        
