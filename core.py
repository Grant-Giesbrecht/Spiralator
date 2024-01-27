import gdstk
import os
import json
import numpy as np
import logging
import getopt
import sys
from colorama import Fore, Back, Style
import re

PI = 3.1415926535

#TODO: For designs which are NOT inverted microstrip, you're going to
#      want to add GSG pads (currently just signal b/c cannot route gnd
#      to signal plane).

#-----------------------------------------------------------
# Parse arguments and initialize logger

LOG_LEVEL = logging.INFO

argv = sys.argv[1:]

try:
	opts, args = getopt.getopt(sys.argv[1:], "h", ["help", "debug", "info", "warning", "error", "critical"])
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
		
		self.lib = gdstk.Library()
		self.main_cell = self.lib.new_cell("MAIN")
		self.layers = {"NbTiN": 10, "Edges": 20}
		
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
			fdk = file_data[k]
			debug(f"Writing value {MPrC}{fdk}{StdC} to variable <{MPrC}{k}{StdC}> {filename}")
		
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
		if self.io['outer']['y_line_offset_um'] >= self.io['inner']['y_line_offset_um']:
			error("Inner IO structure must have higher y-offset than outer. Cannot build chip.")
			return False
		
		if self.io['outer']['y_line_offset_um']+self.io['pads']['taper_width_um']+20 >= self.io['inner']['y_line_offset_um']:
			warning("Inner and outer IO structures are detected to be close. Please verify this is desired.")
			
		
		if self.io['outer']['x_pad_offset_um'] + self.io['pads']['width_um'] + 100 >= self.io['inner']['x_pad_offset_um']:
			warning("Inner and outer bond pads are detected to be close. Please verify this is desired.")
			
		
		spiral_num = self.spiral['num_rotations']//2
		spiral_b = self.spiral['spacing_um']/PI
		spiral_rot_offset = PI # Rotate the entire spiral this many radians
		center_circ_diameter = self.reversal['diameter_um']
		circ_num_pts = self.reversal['num_points']//2
		
		# Make path for 1-direction of spiral (Polar)
		theta1 = np.linspace(spiral_rot_offset, spiral_rot_offset+2*PI*spiral_num, self.spiral["num_points"]//2)
		R1 = (theta1-spiral_rot_offset)*spiral_b + center_circ_diameter
		
		# Make path for other direction of spiral (Polar) (add half rotation so end on same side)
		theta2 = np.linspace(spiral_rot_offset, spiral_rot_offset+2*PI*(spiral_num+0.5), round(self.spiral["num_points"]/2*(spiral_num+0.5)/spiral_num))
		R2 = (theta2-spiral_rot_offset)*spiral_b + center_circ_diameter
		
		# Create center circles
		theta_circ1 = np.linspace(0, PI, circ_num_pts)
		theta_circ2 = np.linspace(PI, 2*PI, circ_num_pts)
		
		# Convert spirals to cartesian
		X1 = R1*np.cos(theta1)
		Y1 = R1*np.sin(theta1)
		X2 = -1*R2*np.cos(theta2)
		Y2 = -1*R2*np.sin(theta2)
		
		# Convert circles to cartesian
		Xc1 = center_circ_diameter/2*np.cos(theta_circ1)-center_circ_diameter/2
		Yc1 = center_circ_diameter/2*np.sin(theta_circ1)
		Xc2 = center_circ_diameter/2*np.cos(theta_circ2)+center_circ_diameter/2
		Yc2 = center_circ_diameter/2*np.sin(theta_circ2)
		
		#TODO: Calculate spiral length
		
		#TODO: Add straight shots for oval spiral
		
		### Select spiral Y-offset/ Check fits on wafer ------------
		#
		
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
		
		#TODO: Check X placement
		
		# spiral_y_offset = 1000
		
		#
		#### End choose spiral position --------------------
		
		# Change format
		path_list1 = [(x_, y_+spiral_y_offset) for x_, y_ in zip(X1, Y1)]
		path_list1.reverse()
		path_list2 = [(x_, y_+spiral_y_offset) for x_, y_ in zip(X2, Y2)]
		circ_list1 = [(x_, y_+spiral_y_offset) for x_, y_ in zip(Xc1, Yc1)]
		circ_list1.reverse()
		circ_list2 = [(x_, y_+spiral_y_offset) for x_, y_ in zip(Xc2, Yc2)]
		
		# Add tails so there are no gaps when connecting to IO components
		tail_1 = [(path_list1[0][0], path_list1[0][1]-self.spiral['tail_length_um'])]
		tail_2 = [(path_list2[-1][0], path_list2[-1][1]-self.spiral['tail_length_um'])]
		
		# Union all components
		path_list = tail_1 + path_list1 + circ_list1 + circ_list2 + path_list2 + tail_2
		
		# Create FlexPath object for full spiral + reversal
		path = gdstk.FlexPath(path_list, self.tlin['Wcenter_um'], tolerance=1e-2, layer=self.layers["NbTiN"])
		
		# Invert selection if color is etch
		bulk = gdstk.rectangle(self.corner_bl, self.corner_tr, layer=self.layers['Edges'])
		
		# ---------------------------------------------------------------------
		# Build IO structures (meandered lines and bond pads)
		
		# Meander outer line: starts at (X2 and Y2)
		self.build_io_component(path_list2[-1], self.io['outer'])
		
		# Meander inner line
		self.build_io_component(path_list1[0], self.io['inner'])
		
		# ---------------------------------------------------------------------
		# Add objects to chip design
		
		if self.is_etch:
			info(f"Inverting layers to calculate etch pattern.")
			inv_paths = gdstk.boolean(bulk, path, "not", layer=self.layers["NbTiN"])
			info(f"Adding etch layers (Inverted)")
			for ip in inv_paths:
				debug(f"Added path from inverted path list.")
				self.main_cell.add(ip)
		else:
			info(f"Adding metal layers (Non-inverted)")
			self.main_cell.add(path)
			self.main_cell.add(bulk)
		
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
	
	def build_io_component(self, start_point, location_rules:dict):
		""" Builds the meandered lines and bond pad for one conductor"""
		
		logging.debug("Adding taper and bond pad.")
		
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
		y_bend_pad_trigger = line_height - self.io['curve_radius_um'] - baseline_offset
		x_bend_spiral_trigger = start_point[0] + self.io['curve_radius_um']
		
		# Pre-calculate bend coordinates - Pad side
		theta_bp = np.linspace(0, PI/2, self.io['num_points_bend'])
		Xbp = self.io['curve_radius_um']*np.cos(theta_bp)
		Ybp = self.io['curve_radius_um']*np.sin(theta_bp)
		bend_pad = [[x_-just_offset+location_rules['x_pad_offset_um']-self.io['curve_radius_um'], y_-baseline_offset+line_height-self.io['curve_radius_um']] for x_, y_ in zip(Xbp, Ybp)] # List of points for pad side bend
		
		# Pre-calculate bend coordinates - Spiral side
		theta_bp = np.linspace(PI, 3*PI/2, self.io['num_points_bend'])
		Xbp = self.io['curve_radius_um']*np.cos(theta_bp)
		Ybp = self.io['curve_radius_um']*np.sin(theta_bp)
		bend_spiral = [[x_+start_point[0]+self.io['curve_radius_um'], y_-baseline_offset+line_height+self.io['curve_radius_um']] for x_, y_ in zip(Xbp, Ybp)]
		bend_spiral.reverse() # List of points for spiral side bend
		
		# Get current point on line - initialize w/ end of bond pad
		current_point = [location_rules['x_pad_offset_um']-just_offset, self.pad_height-baseline_offset]
				
		# Create list of points and widths
		point_list = []
		width_list = []
		
		# Record which section of line algorithm is on
		section = SEC_VERT_PAD
		
		# Record how long along path you are, so know what taper width should be
		dist = 0 
		
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
		
		# Initialize IO structure with bond pad
		io_line = gdstk.FlexPath((location_rules['x_pad_offset_um']-just_offset, self.io['pads']['chip_edge_buffer_um']-baseline_offset), self.io['pads']['width_um'], layer=self.layers["NbTiN"])
		io_line.segment((location_rules['x_pad_offset_um']-just_offset, self.io['pads']['chip_edge_buffer_um']+self.io['pads']['height_um']-baseline_offset), self.io['pads']['width_um'])
		io_line.segment((location_rules['x_pad_offset_um']-just_offset, self.io['pads']['chip_edge_buffer_um']+self.io['pads']['height_um']+self.io['pads']['taper_height_um']-baseline_offset), self.io['pads']['taper_width_um'])
		
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
		
		# (self.corner_bl[0]+self.io['outer']['x_offset_um'], self.corner_bl[1]+self.io['outer']['y_offset_um'])
		
	
	def write(self, filename:str):
		
		info(f"Writing GDS file {MPrC}'{filename}'{StdC}")
		
		self.lib.write_gds(filename)