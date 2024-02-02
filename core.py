import gdstk
import os
import json
import numpy as np
import logging
import getopt
import sys
from colorama import Fore, Back, Style
import re
import math

import pathlib
from matplotlib.font_manager import FontProperties
from matplotlib.textpath import TextPath
from matplotlib import get_data_path

PI = 3.1415926535

#
# TODO: For designs which are NOT inverted microstrip, you're going to
#       want to add GSG pads (currently just signal b/c cannot route gnd
#       to signal plane).
#
#-----------------------------------------------------------
# Parse arguments and initialize logger

DUMMY_MODE = False

LOG_LEVEL = logging.INFO

argv = sys.argv[1:]

try:
	opts, args = getopt.getopt(sys.argv[1:], "h", ["help", "debug", "info", "warning", "error", "critical", "dummy"])
except getopt.GetoptError as err:
	print("--help for help")
	sys.exit(2)
for opt, aarg in opts:
	if opt in ("-h", "--help"):
		print(f"{Fore.RED}LOL just kidding I haven't made any help text yet. ~~OOPS~~{Style.RESET_ALL}")
		sys.exit()
	elif opt == "--debug":
		LOG_LEVEL = logging.DEBUG
	elif opt == "--info":
		LOG_LEVEL = logging.INFO
	elif opt == "--warning":
		LOG_LEVEL = logging.WARNING
	elif opt == "--error":
		LOG_LEVEL = logging.ERROR
	elif opt == "--critical":
		LOG_LEVEL = logging.CRITICAL
	elif opt == "--dummy":
		DUMMY_MODE = True
	else:
		assert False, "unhandled option"
	# ...

tabchar = "    "
PrC = Fore.YELLOW # Prime color (in formatting)
MPrC = Fore.LIGHTCYAN_EX # Message prime color 
StdC = Fore.LIGHTBLUE_EX # Main color for messages
quiet_color = Fore.WHITE # Not used as of now

# logging.basicConfig(stream=sys.stdout, format='%(asctime)s - %(message)s', level=logging.INFO)
logging.basicConfig(format=f'::{PrC}%(levelname)s{Style.RESET_ALL}::{StdC} %(message)s{quiet_color} (Received at %(asctime)s){Style.RESET_ALL}', level=LOG_LEVEL)

def rd(x:float, precision:int=2):
	
	return f"{round(x*(10**precision))/(10**precision)}"

def debug(msg:str):
	""" Logs a message. Applys rules:
		> changes color to PRIME
		< retursn color to standard
		\\> Type > without color adjustment
		\\< Type < without color adjustment
	"""
	
	main_color = Fore.LIGHTBLACK_EX
	prime_color = Fore.WHITE
	
	rich_msg = f"{main_color}{msg}{Style.RESET_ALL}"
	
	# Replace > < that are not escaped with color
	rich_msg = re.sub("(?<!\\\\)>", f"{prime_color}", rich_msg)
	rich_msg = re.sub("(?<!\\\\)<", f"{main_color}", rich_msg)
	
	# Remove escape characters
	rich_msg = rich_msg.replace("\\>", f">")
	rich_msg = rich_msg.replace("\\<", f"<")
	
	logging.debug(rich_msg)

def info(msg:str):
	
	main_color = StdC
	prime_color = MPrC
	
	rich_msg = f"{main_color}{msg}{Style.RESET_ALL}"
	
	# Replace > < that are not escaped with color
	rich_msg = re.sub("(?<!\\\\)>", f"{prime_color}", rich_msg)
	rich_msg = re.sub("(?<!\\\\)<", f"{main_color}", rich_msg)
	
	# Remove escape characters
	rich_msg = rich_msg.replace("\\>", f">")
	rich_msg = rich_msg.replace("\\<", f"<")
	
	logging.info(rich_msg)

def warning(msg:str):
	
	main_color = Fore.LIGHTRED_EX
	prime_color = Fore.WHITE
	
	rich_msg = f"{main_color}{msg}{Style.RESET_ALL}"
	
	# Replace > < that are not escaped with color
	rich_msg = re.sub("(?<!\\\\)>", f"{prime_color}", rich_msg)
	rich_msg = re.sub("(?<!\\\\)<", f"{main_color}", rich_msg)
	
	# Remove escape characters
	rich_msg = rich_msg.replace("\\>", f">")
	rich_msg = rich_msg.replace("\\<", f"<")
	
	logging.warning(rich_msg)
	
def error(msg:str):
	
	main_color = Fore.RED
	prime_color = Fore.WHITE
	
	rich_msg = f"{main_color}{msg}{Style.RESET_ALL}"
	
	# Replace > < that are not escaped with color
	rich_msg = re.sub("(?<!\\\\)>", f"{prime_color}", rich_msg)
	rich_msg = re.sub("(?<!\\\\)<", f"{main_color}", rich_msg)
	
	# Remove escape characters
	rich_msg = rich_msg.replace("\\>", f">")
	rich_msg = rich_msg.replace("\\<", f"<")
	
	logging.error(rich_msg)

def critical(msg:str):
	
	main_color = Fore.RED
	prime_color = Fore.WHITE
	
	rich_msg = f"{main_color}{msg}{Style.RESET_ALL}"
	
	# Replace > < that are not escaped with color
	rich_msg = re.sub("(?<!\\\\)>", f"{prime_color}", rich_msg)
	rich_msg = re.sub("(?<!\\\\)<", f"{main_color}", rich_msg)
	
	# Remove escape characters
	rich_msg = rich_msg.replace("\\>", f">")
	rich_msg = rich_msg.replace("\\<", f"<")
	
	logging.critical(rich_msg)


# Logger initialized
#-----------------------------------------------------------

def render_text(text, size=None, position=(0, 0), font_path=None, tolerance=0.1, layer=None):
	
	# Matplotlib requries pathlib.Path. Convert strings here.
	if font_path is not None:
		font_prop = pathlib.Path(font_path)
	else:
		font_prop = None
	
	path = TextPath(position, text, size=size, prop=font_prop)
	polys = []
	xmax = position[0]
	for points, code in path.iter_segments():
		
		if len(points) > 2:
			
			new_points = []
			idx = 1
			while idx < len(points):
				new_points.append([points[idx-1], points[idx]])
				idx += 2
			points = new_points
		
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
					
				xes = [ x_[0] for x_ in poly]
				xmax = max(xmax, max(xes))
				polys.append(poly)
	
	# Convert list of ndarrays to Polygons
	PolyObjs = []
	for p in polys:
		PolyObjs.append(gdstk.Polygon(p, layer=layer))
	
	return PolyObjs

class ChipDesign:
	
	def __init__(self):
		
		# Design specifications
		self.name = "void" # Name of design
		self.chip_size_um = [] # Size of chip [x, y]
		self.chip_edge_buffer_um = None
		self.spiral_io_buffer_um = None
		self.spiral = {} # Spiral design
		self.reversal = {} # Specs for how build reversal of spiral at center
		self.tlin = {} # TLIN specifications
		self.is_etch = False # If true, regions specify etch. Otherwise, regions specify metal/etc layer presence. Equivalent to whether or not design is inverted.
		self.io = {} # Rules for building IO components
		self.reticle_fiducial = {}
		
		self.lib = gdstk.Library()
		self.main_cell = self.lib.new_cell("MAIN")
		self.layers = {"NbTiN": 10, "Edges": 20}
		
		# Layout element objects
		self.path = None
		self.bulk = None
		self.fiducials = []
		
		# Updated parameters
		self.corner_bl = (-1, -1)
		self.corner_tr = (-1, -1)
		self.pad_height = -1
		
		self.surpress_warning_ttype = False 
	
	def update(self):
		""" Update automatically calcualted parameters """
		
		self.corner_bl = (-self.chip_size_um[0]//2, -self.chip_size_um[1]//2)
		self.corner_tr = (self.chip_size_um[0]//2, self.chip_size_um[1]//2)
		
		self.pad_height = self.io['pads']['chip_edge_buffer_um'] + self.io['pads']['height_um'] + self.io['pads']['taper_height_um']
	
	def read_conf(self, filename:str):
		
		# Open core.json
		try:
			with open(os.path.join(filename)) as f:
				file_data = json.load(f)
		except Exception as e:
			error(f"Failed to read file: {filename} ({e})")
			return False
		
		# Add logger statement
		info(f"Read file {filename}")
		
		# Assign to local variables
		for k in file_data.keys():
			setattr(self, k, file_data[k])
			# fdk = file_data[k]
			# debug(f"Writing value {MPrC}{fdk}{StdC} to variable <{MPrC}{k}{StdC}> {filename}")
		
		self.update()
		
		# Return
		return True
	
	def set(self, param:str, val):
		
		#TODO: Implement
		
		self.update()
	
	def build(self):
		""" Creates the chip design from the specifications. """
		
		# ---------------------------------------------------------------------
		# Build spiral
		
		info("Building chip")
		
		# Basic error checking
		if self.io['same_side'] and (self.io['outer']['y_line_offset_um'] >= self.io['inner']['y_line_offset_um']):
			error("Inner IO structure must have higher y-offset than outer. Cannot build chip.")
			return False
		
		if self.io['same_side'] and (self.io['outer']['y_line_offset_um']+self.io['pads']['taper_width_um']+20 >= self.io['inner']['y_line_offset_um']):
			warning("Inner and outer IO structures are detected to be close. Please verify this is desired.")
			
		
		if self.io['same_side'] and (self.io['outer']['x_pad_offset_um'] + self.io['pads']['width_um'] + 100 >= self.io['inner']['x_pad_offset_um']):
			warning("Inner and outer bond pads are detected to be close. Please verify this is desired.")
		
		
		spiral_num = self.spiral['num_rotations']//2
		spiral_b = self.spiral['spacing_um']/PI
		spiral_rot_offset = PI # Rotate the entire spiral this many radians
		center_circ_diameter = self.reversal['diameter_um']
		circ_num_pts = self.reversal['num_points']//2
		
		# Make path for 1-direction of spiral (Polar)
		theta1 = np.linspace(spiral_rot_offset, spiral_rot_offset+2*PI*spiral_num, self.spiral["num_points"]//2)
		R1 = (theta1-spiral_rot_offset)*spiral_b + center_circ_diameter
		
		if self.io['same_side']:
			# Make path for other direction of spiral (Polar) (add half rotation so end on same side)
			theta2 = np.linspace(spiral_rot_offset, spiral_rot_offset+2*PI*(spiral_num+0.5), round(self.spiral["num_points"]/2*(spiral_num+0.5)/spiral_num))
			R2 = (theta2-spiral_rot_offset)*spiral_b + center_circ_diameter
		else:
			# Make path for other direction of spiral (Polar)
			theta2 = np.linspace(spiral_rot_offset, spiral_rot_offset+2*PI*(spiral_num), round(self.spiral["num_points"]/2*(spiral_num+0.5)/spiral_num))
			R2 = (theta2-spiral_rot_offset)*spiral_b + center_circ_diameter
			
		# Convert spirals to cartesian
		X1 = R1*np.cos(theta1)
		Y1 = R1*np.sin(theta1)
		X2 = -1*R2*np.cos(theta2)
		Y2 = -1*R2*np.sin(theta2)
		
		### Select spiral Y-offset/ Check fits on wafer ------------
		#
		
		if self.io['same_side']:
		
			# Get X and Y bounds
			allYs = list(Y1)+list(Y2)
			allXs = list(X1)+list(X2)
			y_max = np.max(allYs)
			y_min = np.min(allYs)
			x_max = np.max(allXs)
			x_min = np.min(allXs)
			dY = y_max - y_min
			dX = x_max - x_min
			upper_bound = self.chip_size_um[1]/2
			lower_bound = -self.chip_size_um[1]/2 + self.io['inner']['y_line_offset_um'] + self.pad_height
			
			# Check fit
			allowed_size = upper_bound - lower_bound - self.spiral_io_buffer_um - self.chip_edge_buffer_um
			if dY > allowed_size:
				error(f"Cannot fit spiral in Y-dimension. Spiral height >{dY} um< \\> allowed region >{allowed_size} um<.")
				return False
			
			# Get height from bottom
			spiral_y_offset = lower_bound + self.spiral_io_buffer_um + (allowed_size - dY)/2 + abs(y_min)
			debug(f"Selected spiral Y offset of >{spiral_y_offset} um<.")
			debug(f"Spiral lower margin: >{self.spiral_io_buffer_um+(allowed_size-dY)/2} um<.")
			debug(f"Spiral upper margin: >{self.chip_edge_buffer_um+(allowed_size-dY)/2} um<.")
		
		else:
			
			# Get X and Y bounds
			allYs = list(Y1)+list(Y2)
			allXs = list(X1)+list(X2)
			y_max = np.max(allYs)
			y_min = np.min(allYs)
			x_max = np.max(allXs)
			x_min = np.min(allXs)
			dY = y_max - y_min
			dX = x_max - x_min
			upper_bound = self.chip_size_um[1]/2 - self.io['outer']['y_line_offset_um'] - self.pad_height
			lower_bound = -self.chip_size_um[1]/2 + self.io['inner']['y_line_offset_um'] + self.pad_height
			
			# Check fit
			allowed_size = upper_bound - lower_bound - self.spiral_io_buffer_um - self.chip_edge_buffer_um
			if dY > allowed_size:
				error(f"Cannot fit spiral in Y-dimension. Spiral height >{dY} um< \\> allowed region >{allowed_size} um<.")
				return False
			
			# Get height from bottom
			spiral_y_offset = lower_bound + self.spiral_io_buffer_um + (allowed_size - dY)/2 + abs(y_min)
			debug(f"Selected spiral Y offset of >{spiral_y_offset} um<.")
			debug(f"Spiral lower margin: >{self.spiral_io_buffer_um+(allowed_size-dY)/2} um<.")
			debug(f"Spiral upper margin: >{self.chip_edge_buffer_um+(allowed_size-dY)/2} um<.")
		
		#TODO: Check X placement
		
		#
		#### End choose spiral position --------------------
		
		# Add in spiral reversals
		if self.reversal['mode'].upper() == "CIRCLE": # Use circles to reverse direction
		
			# Create center circles
			theta_circ1 = np.linspace(0, PI, circ_num_pts)
			theta_circ2 = np.linspace(PI, 2*PI, circ_num_pts)
			
			# Convert circles to cartesian
			Xc1 = center_circ_diameter/2*np.cos(theta_circ1)-center_circ_diameter/2
			Yc1 = center_circ_diameter/2*np.sin(theta_circ1)
			Xc2 = center_circ_diameter/2*np.cos(theta_circ2)+center_circ_diameter/2
			Yc2 = center_circ_diameter/2*np.sin(theta_circ2)
			
			# Change format
			path_list1 = [[x_, y_+spiral_y_offset] for x_, y_ in zip(X1, Y1)]
			path_list1.reverse()
			path_list2 = [[x_, y_+spiral_y_offset] for x_, y_ in zip(X2, Y2)]
			circ_list1 = [[x_, y_+spiral_y_offset] for x_, y_ in zip(Xc1, Yc1)]
			circ_list1.reverse()
			circ_list2 = [[x_, y_+spiral_y_offset] for x_, y_ in zip(Xc2, Yc2)]
			
			# Add tails so there are no gaps when connecting to IO components
			tail_1 = [[path_list1[0][0], path_list1[0][1]-self.spiral['tail_length_um']]]
			if self.io['same_side']:
				tail_2 = [[path_list2[-1][0], path_list2[-1][1]-self.spiral['tail_length_um']]]
			else:
				tail_2 = [[path_list2[-1][0], path_list2[-1][1]+self.spiral['tail_length_um']]]
			
			# Union all components
			path_list = tail_1 + path_list1 + circ_list1 + circ_list2 + path_list2 + tail_2
		
		elif self.reversal['mode'].upper() == "CIRCLE_SMOOTH": # Use circles with a straight-shot into the circle to prevent sharp angles
			
			# Change format
			path_list1 = [[x_, y_+spiral_y_offset] for x_, y_ in zip(X1, Y1)]
			path_list1.reverse()
			path_list2 = [[x_, y_+spiral_y_offset] for x_, y_ in zip(X2, Y2)]
			
			
			# Add tails so there are no gaps when connecting to IO components
			tail_1 = [[path_list1[0][0], path_list1[0][1]-self.spiral['tail_length_um']]]
			if self.io['same_side']:
				tail_2 = [[path_list2[-1][0], path_list2[-1][1]-self.spiral['tail_length_um']]]
			else:
				tail_2 = [[path_list2[-1][0], path_list2[-1][1]+self.spiral['tail_length_um']]]
			
			# On inner most spirals, find where tangent is vertical. Stop spiral and extend ---------
			# vertically so it matches smoothly with the circle reversal caps:
			
			# Find start point for path1
			last_x1 = None
			idx_x1 = None
			for idx, coord in enumerate(reversed(path_list1)):
				
				# Initilize
				if idx == 0:
					last_x1 = coord[0]
					continue
				
				# Find where x-direction reverses
				if coord[0] >= last_x1:
					idx_x1 = idx
					break
				else:
					last_x1 = coord[0]
				
			
			# Modify spiral path
			final_y = path_list1[-1][1]
			path_list1 = path_list1[0:-idx_x1]
			path_list1.append([last_x1, final_y])
			
			# Find start point for path1
			last_x2 = None
			idx_x2 = None
			for idx, coord in enumerate(path_list2):
				
				# Initilize
				if idx == 0:
					last_x2 = coord[0]
					continue
				
				# Find where x-direction reverses
				if coord[0] <= last_x2:
					idx_x2 = idx
					break
				else:
					last_x2 = coord[0]
			
			# Modify spiral path
			final_y = path_list2[0][1]
			path_list2 = path_list2[idx_x2:]
			path_list2.insert(0, [last_x2, final_y])
			
			# Modify diameter to match spirals
			center_circ_diameter = abs(last_x1)
			
			# End trim spiral inners --------------------
			
			# Create center circles
			theta_circ1 = np.linspace(0, PI, circ_num_pts)
			theta_circ2 = np.linspace(PI, 2*PI, circ_num_pts)
			
			# Convert circles to cartesian
			Xc1 = center_circ_diameter/2*np.cos(theta_circ1)-center_circ_diameter/2
			Yc1 = center_circ_diameter/2*np.sin(theta_circ1)
			Xc2 = center_circ_diameter/2*np.cos(theta_circ2)+center_circ_diameter/2
			Yc2 = center_circ_diameter/2*np.sin(theta_circ2)
			
			circ_list1 = [[x_, y_+spiral_y_offset] for x_, y_ in zip(Xc1, Yc1)]
			circ_list1.reverse()
			circ_list2 = [[x_, y_+spiral_y_offset] for x_, y_ in zip(Xc2, Yc2)]
			
			# Union all components
			path_list = tail_1 + path_list1 + circ_list1 + circ_list2 + path_list2 + tail_2
		
		#### Extend spiral with straight regions as specified --------------------
		#
		
		# Shift everything down and to the left by half
		for pl in path_list:
			pl[0] -= self.spiral['horiz_stretch_um']//2
			pl[1] -= self.spiral['vert_stretch_um']//2
		
		#///////////// Perform vertical stretching //////////////////
		
		# Initialize, find when dX changes sign
		last_sdX = 0
		
		idx_reversal_pt = len(tail_1) + len(path_list1) + len(circ_list1)
		idx_horiz_lock = len(tail_1) + len(path_list1)
		idx_horiz_unlock = len(tail_1) + len(path_list1) + len(circ_list1) + len(circ_list2)
		
		# Scan over all points
		idx = 0
		while True:
			idx += 1
			
			# Check for end condition
			if idx >= len(path_list):
				break
			
			# If dX is zero, skip point
			if path_list[idx][0] - path_list[idx-1][0] == 0:
				sdX = last_sdX
			else:
				# Get sign of dX
				sdX = (path_list[idx][0] - path_list[idx-1][0])/abs(path_list[idx][0] - path_list[idx-1][0] )
			
			# Check for change
			if (last_sdX != sdX) or (idx == idx_reversal_pt):
				# Change occured
				
				# Duplicate last point
				path_list.insert(idx, [path_list[idx-1][0], path_list[idx-1][1]])
				
				# Get sign of Y change
				dY = (path_list[idx][1]-path_list[idx-1][1])
				sign_incr = 1
				while abs(dY) < 0.1:
					sign_incr += 1
					dY = (path_list[idx][1]-path_list[idx-sign_incr][1])
					if sign_incr >= 10:
						logging.error("Failed to identify change in direction while extending spiral.")
						return False
				sign_val = dY/abs(dY)
				
				# print(f"dY sign = {sign_val}, |dY| = {abs(dY)}")
				
				# Shift all remaining points up/down
				for si in range(idx, len(path_list)):
					
					# Modify Y values
					path_list[si][1] += self.spiral['vert_stretch_um'] * sign_val
				
				# Increment index to account for added point
				idx += 1
				if idx < idx_reversal_pt:
					idx_reversal_pt += 1
				if idx < idx_horiz_lock:
					idx_horiz_lock += 1
				if idx < idx_horiz_unlock:
					idx_horiz_unlock += 1
				
				
				# Update last_sdX
				last_sdX = sdX
		
		#///////////// Perform horizontal stretching //////////////////
		
		# Get sign of last dY change
		sign_incr = 1
		last_sdY = (path_list[sign_incr][1]-path_list[0][1])
		while abs(last_sdY) < 0.1:
			sign_incr += 1
			last_sdY = (path_list[sign_incr][1]-path_list[0][1])
			if sign_incr >= 10:
				logging.error("Failed to identify change in direction while extending spiral.")
				return False
		last_sdY = last_sdY/abs(last_sdY)
		
		# path_list.reverse()
		
		# Scan over all points
		idx = 0
		while True:
			idx += 1
			
			# Check for end condition
			if idx >= len(path_list):
				break
			
			# If dY is zero, skip point
			if abs(path_list[idx][1] - path_list[idx-1][1]) < 0.01:
				sdY = last_sdY
			else:
				
				# # Get sign of last dY change
				# sign_incr = 0
				# sdY = (path_list[idx+sign_incr][1]-path_list[idx][1])
				# while abs(sdY) < 0.1:
				# 	sign_incr += 1
				# 	sdY = (path_list[idx+sign_incr][1]-path_list[idx-1][1])
				# 	if sign_incr >= 10:
				# 		logging.error("Failed to identify change in direction while extending spiral.")
				# 		return False
				# sdY = sdY/abs(sdY)
				
				# Get sign of dY
				sdY = (path_list[idx][1] - path_list[idx-1][1])/abs(path_list[idx][1] - path_list[idx-1][1])
			
			# Check for change
			if (last_sdY != sdY):
				# Change occured
				
				# Duplicate last point
				path_list.insert(idx, [path_list[idx-1][0], path_list[idx-1][1]])
				
				# Get sign of X change
				dX = (path_list[idx][0]-path_list[idx-1][0])
				sign_incr = 1
				while abs(dX) < 0.1:
					sign_incr += 1
					dX = (path_list[idx][0]-path_list[idx-sign_incr][0])
					if sign_incr >= 10:
						logging.error("Failed to identify change in direction while extending spiral.")
						return False
				sign_val = dX/abs(dX)
				
				# For center reversals, divide delta evenly
				if idx > idx_horiz_lock and idx < idx_horiz_unlock:
					sign_val /= 2
				
				# Shift all remaining points up/down
				for si in range(idx, len(path_list)):
					
					# Modify X values
					path_list[si][0] += self.spiral['horiz_stretch_um'] * sign_val
				
				# Increment index to account for added point
				idx += 1
				if idx < idx_reversal_pt:
					idx_reversal_pt += 1
				if idx < idx_horiz_lock:
					idx_horiz_lock += 1
				if idx < idx_horiz_unlock:
					idx_horiz_unlock += 1
				
				# Update last_sdX
				last_sdY = sdY
		
		# path_list.reverse()
		
		#
		##### End extend spirals -----------------------------------
		
		# Calcualte total length of spiral
		last_point = None
		spiral_length = 0
		for pt in path_list:
			
			# Initialize
			if last_point is None:
				last_point = pt
				continue
			
			# Otherwise add delta
			spiral_length += np.sqrt((pt[0] - last_point[0])**2 + (pt[1] - last_point[1])**2)
			last_point = pt
		
		info(f"Total spiral length: >{spiral_length} um<.")
		
		# Create FlexPath object for pattern
		self.path = gdstk.FlexPath(path_list, self.tlin['Wcenter_um'], tolerance=1e-2, layer=self.layers["NbTiN"])
		
		# Invert selection if color is etch
		self.bulk = gdstk.rectangle(self.corner_bl, self.corner_tr, layer=self.layers['Edges'])
		
		# ---------------------------------------------------------------------
		# Build IO structures (meandered lines and bond pads)
		
		# Meander outer line: starts at (X2 and Y2)
		if self.io['same_side']:
			self.build_io_component(path_list[-1], self.io['outer'])
		else:
			self.build_io_component(path_list[-1], self.io['outer'], use_alt_side=True)
		
		# Meander inner line
		self.build_io_component(path_list[0], self.io['inner'])
		
		# ---------------------------------------------------------------------
		# Build IO structures (meandered lines and bond pads)
		
		if self.reticle_fiducial['type'].upper() == "L_CORNER":
			
			# Define local coordinates
			x_right = self.chip_size_um[0]//2
			x_left = -1*x_right
			y_up = self.chip_size_um[1]//2
			y_down = -1*y_up
			
			l_fid = self.reticle_fiducial['length_um']
			w_fid = self.reticle_fiducial['width_um']
			
			self.fiducials.append(gdstk.rectangle( (x_left, y_up-l_fid), (x_left+w_fid, y_up), layer=self.layers["NbTiN"]) )
			self.fiducials.append(gdstk.rectangle( (x_left, y_up-w_fid), (x_left+l_fid, y_up), layer=self.layers["NbTiN"]) )
			
			self.fiducials.append(gdstk.rectangle( (x_left, y_down ), (x_left+w_fid, y_down+l_fid), layer=self.layers["NbTiN"]) )
			self.fiducials.append(gdstk.rectangle( (x_left, y_down ), (x_left+l_fid, y_down+w_fid ), layer=self.layers["NbTiN"]) )
			
			self.fiducials.append(gdstk.rectangle( (x_right, y_down ), (x_right-w_fid, y_down+l_fid ), layer=self.layers["NbTiN"]) )
			self.fiducials.append(gdstk.rectangle( (x_right-l_fid, y_down ), (x_right, y_down+w_fid), layer=self.layers["NbTiN"]) )
			
			self.fiducials.append(gdstk.rectangle( (x_right-l_fid, y_up-w_fid ), (x_right, y_up ), layer=self.layers["NbTiN"]) )
			self.fiducials.append(gdstk.rectangle( (x_right-w_fid, y_up ), (x_right, y_up-l_fid ), layer=self.layers["NbTiN"]) )
		
		# ---------------------------------------------------------------------
		# Add objects to chip design
		
		if self.is_etch:
			info(f"Inverting layers to calculate etch pattern.")
			inv_paths = gdstk.boolean(self.bulk, self.path, "not", layer=self.layers["NbTiN"])
			info(f"Adding etch layers (Inverted)")
			for ip in inv_paths:
				debug(f"Added path from inverted path list.")
				self.main_cell.add(ip)
			
			# TODO: Invert fiducials
			# TODO: Invert io components
			# TODO: Invert graphics
		else:
			info(f"Adding metal layers (Non-inverted)")
			self.main_cell.add(self.path)
			self.main_cell.add(self.bulk)
			
			for f in self.fiducials:
				self.main_cell.add(f)
		
		return True
	
	def calc_taper_width(self, z:float):
		""" Calculates the width of the line given the specified taper. 
		
		Type options: (Case insensitive)
			NONE: No taper, immediately jumps to width of spiral.
			LINEAR: Linearly reduces width
		
		"""
		
		#TODO: Implement this!
		
		if self.io['taper']['type'].upper() == "NONE":
			return self.tlin['Wcenter_um']
		elif self.io['taper']['type'].upper() == "LINEAR":
			slope = (self.io['pads']['taper_width_um'] - self.tlin['Wcenter_um'])/self.io['taper']['length_um']
			if z >= self.io['taper']['length_um']:
				return self.tlin['Wcenter_um']
			return self.io['pads']['taper_width_um'] - slope*z
		else:
			ttype = self.io['taper']['type'].upper()
			if not self.surpress_warning_ttype:
				warning(f"Failed to recognize taper type >{ttype}<.")
				self.surpress_warning_ttype = True
				
			return self.tlin['Wcenter_um']
	
	def build_io_component(self, start_point, location_rules:dict, use_alt_side:bool=False):
		""" Builds the meandered lines and bond pad for one conductor"""
		
		debug("Adding taper and bond pad.")
		
		# Get offset parameters
		baseline_offset = self.chip_size_um[1]//2 # Offset to translate (y = 0) to actual bottom of chip
		just_offset = self.chip_size_um[0]//2 # Offset to translate (x = 0) to actual left side of chip
		
		# Constants defining states for state machine
		SEC_VERT_PAD = 0
		SEC_HORIZ = 1
		SEC_VERT_SPIRAL = 2
		
		# Error checking
		if self.io['curve_radius_um'] > location_rules['y_line_offset_um']:
			error("Failed to create IO component.")
			return False
		
		# Height of horizontal component of line
		line_height = self.pad_height + location_rules['y_line_offset_um']
		
		# Calculate trigger points for the two bends
		if use_alt_side:
			y_bend_pad_trigger =  baseline_offset - line_height + self.io['curve_radius_um'] 
			x_bend_spiral_trigger = start_point[0] - self.io['curve_radius_um']
		else:
			y_bend_pad_trigger = line_height - self.io['curve_radius_um'] - baseline_offset
			x_bend_spiral_trigger = start_point[0] + self.io['curve_radius_um']
			
		# Pre-calculate bend coordinates - Pad side
		if not use_alt_side:
			theta_bp = np.linspace(0, PI/2, self.io['num_points_bend'])
			Xbp = self.io['curve_radius_um']*np.cos(theta_bp)
			Ybp = self.io['curve_radius_um']*np.sin(theta_bp)
			bend_pad = [[x_-just_offset+location_rules['x_pad_offset_um']-self.io['curve_radius_um'], y_-baseline_offset+line_height-self.io['curve_radius_um']] for x_, y_ in zip(Xbp, Ybp)] # List of points for pad side bend
		else:
			theta_bp = np.linspace(0, PI/2, self.io['num_points_bend'])
			Xbp = self.io['curve_radius_um']*np.cos(theta_bp)
			Ybp = self.io['curve_radius_um']*np.sin(theta_bp)
			bend_pad = [[-x_-just_offset+location_rules['x_pad_offset_um']+self.io['curve_radius_um'], -y_+baseline_offset-line_height+self.io['curve_radius_um']] for x_, y_ in zip(Xbp, Ybp)] # List of points for pad side bend
		
		if not use_alt_side:
			# Pre-calculate bend coordinates - Spiral side
			theta_bp = np.linspace(PI, 3*PI/2, self.io['num_points_bend'])
			Xbp = self.io['curve_radius_um']*np.cos(theta_bp)
			Ybp = self.io['curve_radius_um']*np.sin(theta_bp)
			bend_spiral = [[x_+start_point[0]+self.io['curve_radius_um'], y_-baseline_offset+line_height+self.io['curve_radius_um']] for x_, y_ in zip(Xbp, Ybp)]
			bend_spiral.reverse() # List of points for spiral side bend
		else:
			# Pre-calculate bend coordinates - Spiral side
			theta_bp = np.linspace(PI, 3*PI/2, self.io['num_points_bend'])
			Xbp = self.io['curve_radius_um']*np.cos(theta_bp)
			Ybp = self.io['curve_radius_um']*np.sin(theta_bp)
			bend_spiral = [[-x_+start_point[0]-self.io['curve_radius_um'], -y_+baseline_offset-line_height-self.io['curve_radius_um']] for x_, y_ in zip(Xbp, Ybp)]
			bend_spiral.reverse() # List of points for spiral side bend
		
		# Get current point on line - initialize w/ end of bond pad
		if not use_alt_side:
			current_point = [location_rules['x_pad_offset_um']-just_offset, self.pad_height-baseline_offset]
		else:
			current_point = [location_rules['x_pad_offset_um']-just_offset, -self.pad_height+baseline_offset]
		
		# Create list of points and widths
		point_list = []
		width_list = []
		
		# Record which section of line algorithm is on
		section = SEC_VERT_PAD
		
		# Record how long along path you are, so know what taper width should be
		dist = 0 
		
		if not use_alt_side:
			# Run until break
			while True:
				
				# 
				if section == SEC_VERT_PAD:
					
					# Check when need to add first bend
					if current_point[1]+self.io['taper']['segment_length_um'] >= y_bend_pad_trigger:
						
						debug("Triggering first bend")
						
						# Loop over each point in bend, add all
						for bp in bend_pad:
							
							# Calculate distance to new point
							dX = np.sqrt((bp[0] - current_point[0])**2 + (bp[1] - current_point[1])**2)
							
							# Update positon
							current_point = bp
							dist += dX
							
							# Add to lists
							point_list.append((current_point[0], current_point[1]))
							width_list.append(self.calc_taper_width(dist))
							
						section = SEC_HORIZ
					else:
						
						# Update position
						current_point[1] += self.io['taper']['segment_length_um']
						dist += self.io['taper']['segment_length_um']
						
						# Add to lists
						point_list.append((current_point[0], current_point[1]))
						width_list.append(self.calc_taper_width(dist))
						
						# debug(f"Moving position to >{current_point}< at width >{self.calc_taper_width(dist)}< um.")
				
				elif section == SEC_HORIZ:
					
					# Check when need to add first bend
					if current_point[0]-self.io['taper']['segment_length_um'] <= x_bend_spiral_trigger:
						
						# Loop over each point in bend, add all
						for bp in bend_spiral:
							
							# Calculate distance to new point
							dX = np.sqrt((bp[0] - current_point[0])**2 + (bp[1] - current_point[1])**2)
							
							# Update positon
							current_point = bp
							dist += dX
							
							# Add to lists
							point_list.append((current_point[0], current_point[1]))
							width_list.append(self.calc_taper_width(dist))
						
						section = SEC_VERT_SPIRAL
					else:
						# Update position
						current_point[0] -= self.io['taper']['segment_length_um']
						dist += self.io['taper']['segment_length_um']
						
						# Add to lists
						point_list.append((current_point[0], current_point[1]))
						width_list.append(self.calc_taper_width(dist))
				
				if section == SEC_VERT_SPIRAL:
					
					# Check when need to add first bend
					if current_point[1]+self.io['taper']['segment_length_um'] >= start_point[1]:
						
						# Loop over each point in bend, add all
						for bp in bend_pad:
							
							# Calculate distance to new point
							dX = np.sqrt((start_point[0] - current_point[0])**2 + (start_point[1] - current_point[1])**2)
							
							# Update positon
							current_point = start_point
							dist += dX
							
							# Add to lists
							point_list.append((current_point[0], current_point[1]))
							width_list.append(self.tlin['Wcenter_um'])
						
						break
					else:
						# Update position
						current_point[1] += self.io['taper']['segment_length_um']
						dist += self.io['taper']['segment_length_um']
						
						# Add to lists
						point_list.append((current_point[0], current_point[1]))
						width_list.append(self.calc_taper_width(dist))
		else:
			
			# Run until break
			while True:
				
				# 
				if section == SEC_VERT_PAD:
					
					# Check when need to add first bend
					if current_point[1]-self.io['taper']['segment_length_um'] <= y_bend_pad_trigger:
						
						debug("Triggering first bend")
						
						# Loop over each point in bend, add all
						for bp in bend_pad:
							
							# Calculate distance to new point
							dX = np.sqrt((bp[0] - current_point[0])**2 + (bp[1] - current_point[1])**2)
							
							# Update positon
							current_point = bp
							dist += dX
							
							# Add to lists
							point_list.append((current_point[0], current_point[1]))
							width_list.append(self.calc_taper_width(dist))
							
						section = SEC_HORIZ
					else:
						
						# Update position
						current_point[1] -= self.io['taper']['segment_length_um']
						dist += self.io['taper']['segment_length_um']
						
						# Add to lists
						point_list.append((current_point[0], current_point[1]))
						width_list.append(self.calc_taper_width(dist))
						
				elif section == SEC_HORIZ:
					
					# Check when need to add first bend
					if current_point[0]+self.io['taper']['segment_length_um'] >= x_bend_spiral_trigger:
						
						# Loop over each point in bend, add all
						for bp in bend_spiral:
							
							# Calculate distance to new point
							dX = np.sqrt((bp[0] - current_point[0])**2 + (bp[1] - current_point[1])**2)
							
							# Update positon
							current_point = bp
							dist += dX
							
							# Add to lists
							point_list.append((current_point[0], current_point[1]))
							width_list.append(self.calc_taper_width(dist))
						
						section = SEC_VERT_SPIRAL
					else:
						# Update position
						current_point[0] += self.io['taper']['segment_length_um']
						dist += self.io['taper']['segment_length_um']
						
						# Add to lists
						point_list.append((current_point[0], current_point[1]))
						width_list.append(self.calc_taper_width(dist))
				
				if section == SEC_VERT_SPIRAL:
					
					# Check when need to add first bend
					if current_point[1]-self.io['taper']['segment_length_um'] <= start_point[1]:
						
						# Loop over each point in bend, add all
						for bp in bend_pad:
							
							# Calculate distance to new point
							dX = np.sqrt((start_point[0] - current_point[0])**2 + (start_point[1] - current_point[1])**2)
							
							# Update positon
							current_point = start_point
							dist += dX
							
							# Add to lists
							point_list.append((current_point[0], current_point[1]))
							width_list.append(self.tlin['Wcenter_um'])
						
						break
					else:
						# Update position
						current_point[1] -= self.io['taper']['segment_length_um']
						dist += self.io['taper']['segment_length_um']
						
						# Add to lists
						point_list.append((current_point[0], current_point[1]))
						width_list.append(self.calc_taper_width(dist))
		
		# Initialize IO structure with bond pad
		if not use_alt_side:
			io_line = gdstk.FlexPath((location_rules['x_pad_offset_um']-just_offset, self.io['pads']['chip_edge_buffer_um']-baseline_offset), self.io['pads']['width_um'], layer=self.layers["NbTiN"])
			io_line.segment((location_rules['x_pad_offset_um']-just_offset, self.io['pads']['chip_edge_buffer_um']+self.io['pads']['height_um']-baseline_offset), self.io['pads']['width_um'])
			io_line.segment((location_rules['x_pad_offset_um']-just_offset, self.io['pads']['chip_edge_buffer_um']+self.io['pads']['height_um']+self.io['pads']['taper_height_um']-baseline_offset), self.io['pads']['taper_width_um'])
		else:
			io_line = gdstk.FlexPath((location_rules['x_pad_offset_um']-just_offset, -self.io['pads']['chip_edge_buffer_um']+baseline_offset), self.io['pads']['width_um'], layer=self.layers["NbTiN"])
			io_line.segment((location_rules['x_pad_offset_um']-just_offset, -self.io['pads']['chip_edge_buffer_um']-self.io['pads']['height_um']+baseline_offset), self.io['pads']['width_um'])
			io_line.segment((location_rules['x_pad_offset_um']-just_offset, -self.io['pads']['chip_edge_buffer_um']-self.io['pads']['height_um']-self.io['pads']['taper_height_um']+baseline_offset), self.io['pads']['taper_width_um'])
		
		# Add points and widths to curve
		for idx,pt in enumerate(point_list): # width_list):
			
			w = width_list[idx]
			
			io_line.segment(pt, w)
		
		# Add objects to chip design
		self.main_cell.add(io_line)
		
		taper_length = self.io['taper']['length_um']
		info(f"Total meandered line length: >{rd(dist)}< um, Taper length: >{rd(taper_length)}<.")
		
		if dist < taper_length:
			warning("Meandered line length is less than taper length! Sharp edge present.")
	
	def custom_text(self, position:list, text:str, font_path:str=None, font_size_um:float=100, tolerance=0.1, layer=None):
		
		# Get default layer
		if layer is None:
			layer = self.layers['NbTiN']
		
		# Get text objects
		text_obj = render_text(text, size=font_size_um, font_path=font_path, position=position, tolerance=tolerance, layer=layer)
		
		# Write to design
		for to in text_obj:
			self.main_cell.add(to)
		
	
	def write(self, filename:str):
		
		if DUMMY_MODE:
			info(f"Skipping write GDS file >DUMMY_MODE<=>TRUE<.")
		else:
			self.lib.write_gds(filename)
			info(f"Wrote GDS file {MPrC}'{filename}'{StdC}")
		
		