import gdstk

lib = gdstk.Library()

cell = lib.new_cell("BASE")

try:
	lib_in = gdstk.read_gds("buffalo_v1.gds", filter={(1,0)})
	# lib_in = gdstk.read_gds("tests/buffalo_v1.gds")
except:
	lib_in = gdstk.read_gds("buffalo_v1.gds")
	
cell_in = lib_in.top_level()

poly_in = cell_in[0].polygons[0]

bb = poly_in.bounding_box()
width = bb[1][0]-bb[0][0]
print(f"Original width: {width} um")

target_w = 15
target_bl = [2, 3]

poly_in.scale(target_w/width)
poly_in.translate(target_bl[0]-bb[0][0], target_bl[1]-bb[0][1])

cell.add(poly_in)
# cell.add(cell_in[0].paths[0])



lib.write_gds("read_test.gds")


