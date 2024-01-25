import gdstk
import numpy as np

# Notice that when you add segments and change the width, it does NOT
# give a constant slope across the new segments, rather it gives a
# constant width delta across each segment. So when I change path_1 from
# 0.2 to 0.6 microns, the width increases 0.2 to 0.4 by x=1.25, and 
# adds the same delta=0.2 to 0.6 microns to x=1.5
#
#

lib = gdstk.Library()

cell = lib.new_cell("BASE")

# Make path (spiral)
theta = np.linspace(0, 2*3.14159*4, 1000)
R = theta*0.5

X = R*np.cos(theta)
Y = R*np.sin(theta)

points1 = [(1.25, 0), (1.5, 0)]
points2 = [(2, 0)]

path_1 = gdstk.FlexPath((0, 0), 0.2)

path_1.segment(points1, 0.6)
path_1.segment(points2, 2)

# path_2 = gdstk.FlexPath((3, 0), [0.1, 0.1], 0.2)

# path_2.segment(points, offset=0.6, relative=True)


cell.add(path_1)

lib.write_gds("taper_test.gds")