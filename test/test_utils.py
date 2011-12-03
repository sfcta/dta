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


from dta.Utils import *

class TestUtils:

    def test_lineSegmentsCross(self):
        
        p1, p2 = [[0,0], [1,0]]

        p3, p4 = [[0, 1], [1,1]]

        assert not lineSegmentsCross(p1, p2, p3, p4)

        p5, p6 = [[0,0], [0, 1]]

        assert not lineSegmentsCross(p1, p2, p5, p6)
        assert lineSegmentsCross(p1, p2, p5, p6, checkBoundryConditions=True)

    def test_polylinesCross(self):
        
        line1 = [[[0,0], [1,0]], [[1,0], [1,1]]]
        line2 = [[[0,0], [1,0]], [[1,0], [1, -1]]]

        assert not polylinesCross(line1, line2)

        line3 = [[[0, 0.5], [1, 0.5]], [[1, 0.5], [2, 0.5]]]

        assert not polylinesCross(line1, line3)

        line4 = [[[0, 0.5], [2, 0.5]]]

        assert polylinesCross(line1, line4)

        
