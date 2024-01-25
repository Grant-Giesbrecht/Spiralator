import gdstk
import numpy as np

lib = gdstk.Library()

cell = lib.new_cell("BASE")

# Make path (spiral)
theta = np.linspace(0, 2*3.14159*4, 1000)
R = theta*0.5

X = R*np.cos(theta)
Y = R*np.sin(theta)

# change path format
# path_list = []
# for th, r in zip(theta, R):
# 	path_list.append((th, r))
	
path_list = [(x_, y_) for x_, y_ in zip(X, Y)]

path = gdstk.FlexPath(path_list, 0.2, tolerance=1e-2)

cell.add(path)

lib.write_gds("path_test.gds")