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

def lineSegmentsCross(p1, p2, p3, p4):
    """
    Helper function that determines if line segments, 
    defined as a sequence of pairs 
    of points, (p1,p2) and (p3,p4) intersect. 
    If so it returns True, otherwise False. If the two 
    line segments touch each other the method will 
    return False.  
    """
    
    def crossProduct(pl, pm):
        """Return the cross product of two points pl and pm 
        each of them defined as a tuple (x, y)
        """ 
        return pl[0]*pm[1] - pm[0]*pl[1]


    def direction(pi, pj, pk):
        
        return crossProduct((pk[0] - pi[0], pk[1] - pi[1]),
                            (pj[0] - pi[0], pj[1] - pi[1])) 

    d1 = direction(p3, p4, p1)
    d2 = direction(p3, p4, p2)
    d3 = direction(p1, p2, p3)
    d4 = direction(p1, p2, p4) 

    if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and \
            ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
        return True
    else:
        return False
    
def getMidPoint(p1, p2):
    """
    Return the the point in the middle of p1 and p2 as a (x,y) tuple.
    """
    #TODO:consider associating this function to an object
    return ((p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0)