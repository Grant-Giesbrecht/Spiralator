	

######################################################################
#                                                                    #
#  Copyright 2009 Lucas Heitzmann Gabrielli.                         #
#  This file is part of gdstk, distributed under the terms of the    #
#  Boost Software License - Version 1.0.  See the accompanying       #
#  LICENSE file or <http://www.boost.org/LICENSE_1_0.txt>            #
#                                                                    #
######################################################################

import pathlib
from matplotlib.font_manager import FontProperties
from matplotlib.textpath import TextPath
from matplotlib import get_data_path
import gdstk


def render_text(text, size=None, position=(0, 0), font_path=None, tolerance=0.1):
	
	# Matplotlib requries pathlib.Path. Convert strings here.
	if font_path is not None:
		font_prop = pathlib.Path(font_path)
	else:
		font_prop = None
	
	path = TextPath(position, text, size=size, prop=font_prop)
	polys = []
	xmax = position[0]
	for points, code in path.iter_segments():
		
		# print("Loop")
		
		if len(points) > 2:
			
			new_points = []
			idx = 1
			while idx < len(points):
				new_points.append([points[idx-1], points[idx]])
				idx += 2
			points = new_points
		
		
		# print("-->")
		
		if code == path.MOVETO:
			c = gdstk.Curve(points, tolerance=tolerance)
		elif code == path.LINETO:
			c.segment(points)
		elif code == path.CURVE3:
			c.quadratic(points)
		elif code == path.CURVE4:
			c.cubic(points)
		elif code == path.CLOSEPOLY:
			poly = c.points()
			
			if poly.size > 0:
				if poly[:, 0].min() < xmax:
					i = len(polys) - 1
					while i >= 0:
						
						if isinstance(poly[0], gdstk.Polygon):
							print("DEPOLY")
							poly = poly[0].points
						
						if gdstk.inside(poly[:1], [polys[i]])[0]: # Ommited: , precision=0.1 * tolerance
							p = polys.pop(i)
							poly = gdstk.boolean([p],[poly],"xor",precision=0.1 * tolerance)
							break
						elif gdstk.inside(polys[i][:1], [poly])[0]:  # Ommited: , precision=0.1 * tolerance
							p = polys.pop(i)
							poly = gdstk.boolean([p],[poly],"xor",precision=0.1 * tolerance)
						i -= 1

				
				if isinstance(poly[0], gdstk.Polygon):
					poly = poly[0].points
					
				# print("\n\n\n", flush=True)
				# print(poly, flush=True)
				xes = [ x_[0] for x_ in poly]
				xmax = max(xmax, max(xes))
				polys.append(poly)
				
				print(xmax)
	
	# Convert list of ndarrays to Polygons
	PolyObjs = []
	for p in polys:
		PolyObjs.append(gdstk.Polygon(p))
	
	return PolyObjs


if __name__ == "__main__":
	futura = pathlib.Path("..", "assets", "futura", "futura medium bt.ttf")
	chicago = pathlib.Path("Chicago.ttf")
	
	fp = FontProperties(family="serif", style="italic")
	polys = render_text("Text rendering", 10, font_prop=futura)
	
	lib = gdstk.Library()
	cell = lib.new_cell("TXT")
	
	for t in polys:
		cell.add(t)
	
	lib.write_gds("fonts.gds")
