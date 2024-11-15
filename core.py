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

import matplotlib.pyplot as plt

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
		print(f"{Fore.RED}Whoops just kidding I haven't made any help text yet. ~~OOPS~~{Style.RESET_ALL}")
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

class MultiChipDesign:
	
	def __init__(self, num_designs:int):
		
		# Basic parameters
		self.chip_size_um = [] # Size of chip [x,y]
		self.num_designs = num_designs # Number of designs to subsection chip
		
		# List of designs to position on subreticle
		self.designs = []
		
		# GDSTK objects
		self.lib = gdstk.Library()
		self.main_cell = self.lib.new_cell("MAIN")
		self.layers = {"NbTiN": 0, "Aluminum": 1, "Edges": 4, "aSi": 5, "GND": 6}
	
	def read_conf(self, filename:str):
		
		# Open json
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
	
	def add_design(self, new_design, rotation:float=None, translation:list=None, rotation_center:list=[0,0]):
		''' Adds a design to the multichip and applies a rotation (degrees) and 
		translation (um).'''
		
		# Add design to list
		self.designs.append(new_design)
		
		# Rotate design
		if rotation is not None:
			
			rotation = rotation * 3.1415926535 / 180
			
			self.designs[-1].rotate(rotation, rotation_center)
		
		# Translate design
		if translation is not None:
			self.designs[-1].translate(translation[0], translation[1])
	
	def build(self):
		
		pass
	
	def apply_objects(self):
		
		
		for dsgn in self.designs:
			dsgn.apply_objects(target_cell=self.main_cell)
	
	def write(self, filename:str):
		
		if DUMMY_MODE:
			info(f"Skipping write GDS file >DUMMY_MODE<=>TRUE<.")
		else:
			self.lib.write_gds(filename)
			info(f"Wrote GDS file {MPrC}'{filename}'{StdC}")

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
		self.NbTiN_is_etch = False # If true, regions specify etch. Otherwise, regions specify metal/etc layer presence. Equivalent to whether or not design is inverted.
		self.aSi_is_etch = False # If true, regions specify etch. Otherwise, regions specify metal/etc layer presence. Equivalent to whether or not design is inverted.
		self.io = {} # Rules for building IO components
		self.reticle_fiducial = {}
		
		
		# For the time being...
		warning("Replace this section of code!!!!")
		self.aSi_pad_buffer_um = 105
		self.gnd_pad_buffer_x_um = 150
		self.gnd_pad_buffer_y_um = 110
		
		self.graphics_on_gnd = None
		
		self.lib = gdstk.Library()
		self.main_cell = self.lib.new_cell("MAIN")
		self.layers = {"NbTiN": 0, "Aluminum": 1, "Edges": 4, "aSi": 5, "GND": 6}
		
		# Layout element objects
		self.path = None
		self.bulk = None
		self.gnd = []
		self.bond_pad_hole = []
		self.Al_pad = []
		self.io_line_list = []
		self.text_obj_list = []
		self.fiducials = []
		self.temp_pads = [] # Stores bond pad dimensions. Not added to gdstk cell, but used to calculate aSi and gnd shapes.
		
		# Updated parameters
		self.corner_bl = (-1, -1)
		self.corner_tr = (-1, -1)
		self.pad_height = -1
		
		self.surpress_warning_ttype = False 
		
		self.use_steps = False
		self.step_width_um = None
		self.step_length_um = None
		self.step_spacing_um = None
		
	def configure_steps(self, ZL_width_um:float, ZH_width_um:float, ZL_length_um:float, ZH_length_um:float):
		
		self.use_steps = True
		self.step_width_um = ZL_width_um
		self.ZH_step_width_um = ZH_width_um
		self.step_length_um = ZL_length_um
		self.step_spacing_um = ZH_length_um
	
	def update(self):
		""" Update automatically calcualted parameters """
		
		# Save taper_height_um parameter
		#    Although this can be derived from the fuax_cpw_taper>cpw_sections_lengths_um parameter
		#    lots of bits of code expect this older parameter. For ease, I'm just re-calculating it
		#    automatically.
		self.io['pads']['taper_height_um'] = 0
		for csl in self.io['faux_cpw_taper']['cpw_section_lengths_um']:
			self.io['pads']['taper_height_um'] += csl
		
		# Save taper_width_um parameter
		self.io['pads']['taper_width_um'] = self.io['faux_cpw_taper']['cpw_widths_um'][-1]
		
		self.corner_bl = (-self.chip_size_um[0]//2, -self.chip_size_um[1]//2)
		self.corner_tr = (self.chip_size_um[0]//2, self.chip_size_um[1]//2)
		
		self.pad_height = self.io['pads']['chip_edge_buffer_um'] + self.io['pads']['height_um'] + self.io['pads']['taper_height_um']
	
	def read_conf(self, filename:str):
		
		# Open json
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
	
	def rotate(self, arg:float, center_point:list=[0,0]):
		''' Rotates the chip design by the value arg, in radians. '''
		
		for f in self.fiducials:
			f.rotate(arg, center_point)
		
		self.path.rotate(arg, center_point)
		self.bulk.rotate(arg, center_point)
		
		# Add to object
		for bph in self.bond_pad_hole:
			bph.rotate(arg, center_point)
		
		# Add to cell
		for alp in self.Al_pad:
			alp.rotate(arg, center_point)
		
		# Add to cell
		for g in self.gnd:
			g.rotate(arg, center_point)
		
		# Add IO lines
		for io_line in self.io_line_list:
			io_line.rotate(arg, center_point)
		
		# Add text objects
		for to in self.text_obj_list:
			to.rotate(arg, center_point)
	
	def translate(self, move_x:float, move_y:float):
		''' Translate the chip design by the value arg, in microns. '''
		
		for f in self.fiducials:
			f.translate(move_x, move_y)
		
		self.path.translate(move_x, move_y)
		self.bulk.translate(move_x, move_y)
		
		# Add to object
		for bph in self.bond_pad_hole:
			bph.translate(move_x, move_y)
		
		# Add to cell
		for alp in self.Al_pad:
			alp.translate(move_x, move_y)
		
		# Add to cell
		for g in self.gnd:
			g.translate(move_x, move_y)
		
		# Add IO lines
		for io_line in self.io_line_list:
			io_line.translate(move_x, move_y)
		
		# Add text objects
		for to in self.text_obj_list:
			to.translate(move_x, move_y)
	
	def apply_objects(self, target_cell=None):
		''' Saves all objects to the cell '''
		
		if target_cell is None:
			target_cell = self.main_cell
		
		# # This should be moved to build I think
		# if self.NbTiN_is_etch:
		# 	info(f"Inverting layers to calculate etch pattern.")
		# 	inv_paths = gdstk.boolean(self.bulk, self.path, "not", layer=self.layers["NbTiN"])
		# 	info(f"Adding etch layers (Inverted)")
		# 	for ip in inv_paths:
		# 		debug(f"Added path from inverted path list.")
		# 		target_cell.add(ip)
			
		# 	warning("NbTiN is etch needs to be fully implemented!")
			
		# 	# TODO: Invert fiducials
		# 	# TODO: Invert io components
		# 	# TODO: Invert graphics
		# else:
		# 	info(f"Adding metal layers (Non-inverted)")
			
			
			
				
		# 	if self.reticle_fiducial['on_gnd']:
				
		# 		# # Get polygon
		# 		# new_gnd = []
		# 		# for poly in target_cell.polygons:
		# 		# 	if poly.layer == self.layers['GND']:
		# 		# 		new_gnd.append(poly)
				
		# 		# # Check ground plane was found
		# 		# if len(new_gnd) < 1:
		# 		# 	error("Failed to find ground plane. Cannot add graphic to ground plane.")
		# 		# 	return False
				
		# 		# # Remove old ground plane
		# 		# target_cell.remove(*new_gnd)
				
		# 		# Subtract text from ground
		# 		for f in self.fiducials:
		# 			self.gnd = gdstk.boolean(self.gnd, f, "not", layer=self.layers["GND"])
				
		# 		# # Replace ground plane in cell
		# 		# for ng in new_gnd:
		# 		# 	target_cell.add(ng)
				
			
		for f in self.fiducials:
			target_cell.add(f)
		
		target_cell.add(self.path)
		target_cell.add(self.bulk)
		
		# Add to object
		for bph in self.bond_pad_hole:
			target_cell.add(bph)
		
		# Add to cell
		for ap in self.Al_pad:
			target_cell.add(ap)
		
		# Add to cell
		for g in self.gnd:
			target_cell.add(g)
		
		# Add IO lines
		for io_line in self.io_line_list:
			target_cell.add(io_line)
		
		# Add text objects
		for to in self.text_obj_list:
			target_cell.add(to)
	
	def build(self):
		""" Creates the chip design from the specifications. """
		
		if self.spiral['num_rotations'] == 0:
			self.build_through()
		else:
			self.build_standard()
	
	def build_through(self):
		''' Builds the chip with no spiral rotations'''
		
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
		
		
		# spiral_num = self.spiral['num_rotations']//2
		# spiral_b = self.spiral['spacing_um']/PI
		# spiral_rot_offset = PI # Rotate the entire spiral this many radians
		# center_circ_diameter = self.reversal['diameter_um']
		# circ_num_pts = self.reversal['num_points']//2
		
		# # Make path for 1-direction of spiral (Polar)
		# theta1 = np.linspace(spiral_rot_offset, spiral_rot_offset+2*PI*spiral_num, self.spiral["num_points"]//2)
		# R1 = (theta1-spiral_rot_offset)*spiral_b + center_circ_diameter
		
		# if self.io['same_side']:
		# 	# Make path for other direction of spiral (Polar) (add half rotation so end on same side)
		# 	theta2 = np.linspace(spiral_rot_offset, spiral_rot_offset+2*PI*(spiral_num+0.5), round(self.spiral["num_points"]/2*(spiral_num+0.5)/spiral_num))
		# 	R2 = (theta2-spiral_rot_offset)*spiral_b + center_circ_diameter
		# else:
		# 	# Make path for other direction of spiral (Polar)
		# 	theta2 = np.linspace(spiral_rot_offset, spiral_rot_offset+2*PI*(spiral_num), round(self.spiral["num_points"]/2*(spiral_num+0.5)/spiral_num))
		# 	R2 = (theta2-spiral_rot_offset)*spiral_b + center_circ_diameter
			
		# # Convert spirals to cartesian
		# X1 = R1*np.cos(theta1)
		# Y1 = R1*np.sin(theta1)
		# X2 = -1*R2*np.cos(theta2)
		# Y2 = -1*R2*np.sin(theta2)
		
		### Select spiral Y-offset/ Check fits on wafer ------------
		#
		
		# if self.io['same_side']:
		
		# 	# Get X and Y bounds
		# 	allYs = list(Y1)+list(Y2)
		# 	allXs = list(X1)+list(X2)
		# 	y_max = np.max(allYs)
		# 	y_min = np.min(allYs)
		# 	x_max = np.max(allXs)
		# 	x_min = np.min(allXs)
		# 	dY = y_max - y_min
		# 	dX = x_max - x_min
		# 	upper_bound = self.chip_size_um[1]/2
		# 	lower_bound = -self.chip_size_um[1]/2 + self.io['inner']['y_line_offset_um'] + self.pad_height
			
		# 	# Check fit
		# 	allowed_size = upper_bound - lower_bound - self.spiral_io_buffer_um - self.chip_edge_buffer_um
		# 	if dY > allowed_size:
		# 		error(f"Cannot fit spiral in Y-dimension. Spiral height >{dY} um< \\> allowed region >{allowed_size} um<.")
		# 		return False
			
		# 	# Get height from bottom
		# 	spiral_y_offset = lower_bound + self.spiral_io_buffer_um + (allowed_size - dY)/2 + abs(y_min)
		# 	debug(f"Selected spiral Y offset of >{spiral_y_offset} um<.")
		# 	debug(f"Spiral lower margin: >{self.spiral_io_buffer_um+(allowed_size-dY)/2} um<.")
		# 	debug(f"Spiral upper margin: >{self.chip_edge_buffer_um+(allowed_size-dY)/2} um<.")
		
		# else:
			
		# 	# Get X and Y bounds
		# 	allYs = list(Y1)+list(Y2)
		# 	allXs = list(X1)+list(X2)
		# 	y_max = np.max(allYs)
		# 	y_min = np.min(allYs)
		# 	x_max = np.max(allXs)
		# 	x_min = np.min(allXs)
		# 	dY = y_max - y_min
		# 	dX = x_max - x_min
		# 	upper_bound = self.chip_size_um[1]/2 - self.io['outer']['y_line_offset_um'] - self.pad_height
		# 	lower_bound = -self.chip_size_um[1]/2 + self.io['inner']['y_line_offset_um'] + self.pad_height
			
		# 	# Check fit
		# 	allowed_size = upper_bound - lower_bound - self.spiral_io_buffer_um - self.chip_edge_buffer_um
		# 	if dY > allowed_size:
		# 		error(f"Cannot fit spiral in Y-dimension. Spiral height >{dY} um< \\> allowed region >{allowed_size} um<.")
		# 		return False
			
		# 	# Get height from bottom
		# 	spiral_y_offset = lower_bound + self.spiral_io_buffer_um + (allowed_size - dY)/2 + abs(y_min)
		# 	debug(f"Selected spiral Y offset of >{spiral_y_offset} um<.")
		# 	debug(f"Spiral lower margin: >{self.spiral_io_buffer_um+(allowed_size-dY)/2} um<.")
		# 	debug(f"Spiral upper margin: >{self.chip_edge_buffer_um+(allowed_size-dY)/2} um<.")
		
		#TODO: Check X placement
		
		#
		#### End choose spiral position --------------------
		
		# # Add in spiral reversals
		# if self.reversal['mode'].upper() == "CIRCLE": # Use circles to reverse direction
		
		# 	# Create center circles
		# 	theta_circ1 = np.linspace(0, PI, circ_num_pts)
		# 	theta_circ2 = np.linspace(PI, 2*PI, circ_num_pts)
			
		# 	# Convert circles to cartesian
		# 	Xc1 = center_circ_diameter/2*np.cos(theta_circ1)-center_circ_diameter/2
		# 	Yc1 = center_circ_diameter/2*np.sin(theta_circ1)
		# 	Xc2 = center_circ_diameter/2*np.cos(theta_circ2)+center_circ_diameter/2
		# 	Yc2 = center_circ_diameter/2*np.sin(theta_circ2)
			
		# 	# Change format
		# 	path_list1 = [[x_, y_+spiral_y_offset] for x_, y_ in zip(X1, Y1)]
		# 	path_list1.reverse()
		# 	path_list2 = [[x_, y_+spiral_y_offset] for x_, y_ in zip(X2, Y2)]
		# 	circ_list1 = [[x_, y_+spiral_y_offset] for x_, y_ in zip(Xc1, Yc1)]
		# 	circ_list1.reverse()
		# 	circ_list2 = [[x_, y_+spiral_y_offset] for x_, y_ in zip(Xc2, Yc2)]
			
		# 	# Add tails so there are no gaps when connecting to IO components
		# 	tail_1 = [[path_list1[0][0], path_list1[0][1]-self.spiral['tail_length_um']]]
		# 	if self.io['same_side']:
		# 		tail_2 = [[path_list2[-1][0], path_list2[-1][1]-self.spiral['tail_length_um']]]
		# 	else:
		# 		tail_2 = [[path_list2[-1][0], path_list2[-1][1]+self.spiral['tail_length_um']]]
			
		# 	# Union all components
		# 	path_list = tail_1 + path_list1 + circ_list1 + circ_list2 + path_list2 + tail_2
		
		# elif self.reversal['mode'].upper() == "CIRCLE_SMOOTH": # Use circles with a straight-shot into the circle to prevent sharp angles
			
		# 	# Change format
		# 	path_list1 = [[x_, y_+spiral_y_offset] for x_, y_ in zip(X1, Y1)]
		# 	path_list1.reverse()
		# 	path_list2 = [[x_, y_+spiral_y_offset] for x_, y_ in zip(X2, Y2)]
			
			
		# 	# Add tails so there are no gaps when connecting to IO components
		# 	tail_1 = [[path_list1[0][0], path_list1[0][1]-self.spiral['tail_length_um']]]
		# 	if self.io['same_side']:
		# 		tail_2 = [[path_list2[-1][0], path_list2[-1][1]-self.spiral['tail_length_um']]]
		# 	else:
		# 		tail_2 = [[path_list2[-1][0], path_list2[-1][1]+self.spiral['tail_length_um']]]
			
		# 	# On inner most spirals, find where tangent is vertical. Stop spiral and extend ---------
		# 	# vertically so it matches smoothly with the circle reversal caps:
			
		# 	# Find start point for path1
		# 	last_x1 = None
		# 	idx_x1 = None
		# 	for idx, coord in enumerate(reversed(path_list1)):
				
		# 		# Initilize
		# 		if idx == 0:
		# 			last_x1 = coord[0]
		# 			continue
				
		# 		# Find where x-direction reverses
		# 		if coord[0] >= last_x1:
		# 			idx_x1 = idx
		# 			break
		# 		else:
		# 			last_x1 = coord[0]
				
			
		# 	# Modify spiral path
		# 	final_y = path_list1[-1][1]
		# 	path_list1 = path_list1[0:-idx_x1]
		# 	path_list1.append([last_x1, final_y])
			
		# 	# Find start point for path1
		# 	last_x2 = None
		# 	idx_x2 = None
		# 	for idx, coord in enumerate(path_list2):
				
		# 		# Initilize
		# 		if idx == 0:
		# 			last_x2 = coord[0]
		# 			continue
				
		# 		# Find where x-direction reverses
		# 		if coord[0] <= last_x2:
		# 			idx_x2 = idx
		# 			break
		# 		else:
		# 			last_x2 = coord[0]
			
		# 	# Modify spiral path
		# 	final_y = path_list2[0][1]
		# 	path_list2 = path_list2[idx_x2:]
		# 	path_list2.insert(0, [last_x2, final_y])
			
		# 	# Modify diameter to match spirals
		# 	center_circ_diameter = abs(last_x1)
			
		# 	# End trim spiral inners --------------------
			
		# 	# Create center circles
		# 	theta_circ1 = np.linspace(0, PI, circ_num_pts)
		# 	theta_circ2 = np.linspace(PI, 2*PI, circ_num_pts)
			
		# 	# Convert circles to cartesian
		# 	Xc1 = center_circ_diameter/2*np.cos(theta_circ1)-center_circ_diameter/2
		# 	Yc1 = center_circ_diameter/2*np.sin(theta_circ1)
		# 	Xc2 = center_circ_diameter/2*np.cos(theta_circ2)+center_circ_diameter/2
		# 	Yc2 = center_circ_diameter/2*np.sin(theta_circ2)
			
		# 	circ_list1 = [[x_, y_+spiral_y_offset] for x_, y_ in zip(Xc1, Yc1)]
		# 	circ_list1.reverse()
		# 	circ_list2 = [[x_, y_+spiral_y_offset] for x_, y_ in zip(Xc2, Yc2)]
			
		# 	# Union all components
		# 	path_list = tail_1 + path_list1 + circ_list1 + circ_list2 + path_list2 + tail_2
		
		#### Extend spiral with straight regions as specified --------------------
		#
		
		# # Shift everything down and to the left by half
		# for pl in path_list:
		# 	pl[0] -= self.spiral['horiz_stretch_um']//2
		# 	pl[1] -= self.spiral['vert_stretch_um']//2
		
		#///////////// Perform vertical stretching //////////////////
		
		# Initialize, find when dX changes sign
		# last_sdX = 0
		
		# idx_reversal_pt = len(tail_1) + len(path_list1) + len(circ_list1)
		# idx_horiz_lock = len(tail_1) + len(path_list1)
		# idx_horiz_unlock = len(tail_1) + len(path_list1) + len(circ_list1) + len(circ_list2)
		
		# # Scan over all points
		# idx = 0
		# while True:
		# 	idx += 1
			
		# 	# Check for end condition
		# 	if idx >= len(path_list):
		# 		break
			
		# 	# If dX is zero, skip point
		# 	if path_list[idx][0] - path_list[idx-1][0] == 0:
		# 		sdX = last_sdX
		# 	else:
		# 		# Get sign of dX
		# 		sdX = (path_list[idx][0] - path_list[idx-1][0])/abs(path_list[idx][0] - path_list[idx-1][0] )
			
		# 	# Check for change
		# 	if (last_sdX != sdX) or (idx == idx_reversal_pt):
		# 		# Change occured
				
		# 		# Duplicate last point
		# 		path_list.insert(idx, [path_list[idx-1][0], path_list[idx-1][1]])
				
		# 		# Get sign of Y change
		# 		dY = (path_list[idx][1]-path_list[idx-1][1])
		# 		sign_incr = 1
		# 		while abs(dY) < 0.1:
		# 			sign_incr += 1
		# 			dY = (path_list[idx][1]-path_list[idx-sign_incr][1])
		# 			if sign_incr >= 10:
		# 				logging.error("Failed to identify change in direction while extending spiral.")
		# 				return False
		# 		sign_val = dY/abs(dY)
				
		# 		# print(f"dY sign = {sign_val}, |dY| = {abs(dY)}")
				
		# 		# Shift all remaining points up/down
		# 		for si in range(idx, len(path_list)):
					
		# 			# Modify Y values
		# 			path_list[si][1] += self.spiral['vert_stretch_um'] * sign_val
				
		# 		# Increment index to account for added point
		# 		idx += 1
		# 		if idx < idx_reversal_pt:
		# 			idx_reversal_pt += 1
		# 		if idx < idx_horiz_lock:
		# 			idx_horiz_lock += 1
		# 		if idx < idx_horiz_unlock:
		# 			idx_horiz_unlock += 1
				
				
		# 		# Update last_sdX
		# 		last_sdX = sdX
		
		# #///////////// Perform horizontal stretching //////////////////
		
		# # Get sign of last dY change
		# sign_incr = 1
		# last_sdY = (path_list[sign_incr][1]-path_list[0][1])
		# while abs(last_sdY) < 0.1:
		# 	sign_incr += 1
		# 	last_sdY = (path_list[sign_incr][1]-path_list[0][1])
		# 	if sign_incr >= 10:
		# 		logging.error("Failed to identify change in direction while extending spiral.")
		# 		return False
		# last_sdY = last_sdY/abs(last_sdY)
		
		# # path_list.reverse()
		
		# # Scan over all points
		# idx = 0
		# while True:
		# 	idx += 1
			
		# 	# Check for end condition
		# 	if idx >= len(path_list):
		# 		break
			
		# 	# If dY is zero, skip point
		# 	if abs(path_list[idx][1] - path_list[idx-1][1]) < 0.01:
		# 		sdY = last_sdY
		# 	else:
				
		# 		# # Get sign of last dY change
		# 		# sign_incr = 0
		# 		# sdY = (path_list[idx+sign_incr][1]-path_list[idx][1])
		# 		# while abs(sdY) < 0.1:
		# 		# 	sign_incr += 1
		# 		# 	sdY = (path_list[idx+sign_incr][1]-path_list[idx-1][1])
		# 		# 	if sign_incr >= 10:
		# 		# 		logging.error("Failed to identify change in direction while extending spiral.")
		# 		# 		return False
		# 		# sdY = sdY/abs(sdY)
				
		# 		# Get sign of dY
		# 		sdY = (path_list[idx][1] - path_list[idx-1][1])/abs(path_list[idx][1] - path_list[idx-1][1])
			
		# 	# Check for change
		# 	if (last_sdY != sdY):
		# 		# Change occured
				
		# 		# Duplicate last point
		# 		path_list.insert(idx, [path_list[idx-1][0], path_list[idx-1][1]])
				
		# 		# Get sign of X change
		# 		dX = (path_list[idx][0]-path_list[idx-1][0])
		# 		sign_incr = 1
		# 		while abs(dX) < 0.1:
		# 			sign_incr += 1
		# 			dX = (path_list[idx][0]-path_list[idx-sign_incr][0])
		# 			if sign_incr >= 10:
		# 				logging.error("Failed to identify change in direction while extending spiral.")
		# 				return False
		# 		sign_val = dX/abs(dX)
				
		# 		# For center reversals, divide delta evenly
		# 		if idx > idx_horiz_lock and idx < idx_horiz_unlock:
		# 			sign_val /= 2
				
		# 		# Shift all remaining points up/down
		# 		for si in range(idx, len(path_list)):
					
		# 			# Modify X values
		# 			path_list[si][0] += self.spiral['horiz_stretch_um'] * sign_val
				
		# 		# Increment index to account for added point
		# 		idx += 1
		# 		if idx < idx_reversal_pt:
		# 			idx_reversal_pt += 1
		# 		if idx < idx_horiz_lock:
		# 			idx_horiz_lock += 1
		# 		if idx < idx_horiz_unlock:
		# 			idx_horiz_unlock += 1
				
		# 		# Update last_sdX
		# 		last_sdY = sdY
		
		#
		##### End extend spirals -----------------------------------
		
		path_list = [[self.io['outer']['x_pad_offset_um']-self.chip_size_um[0]/2,0]]
		
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
		self.gnd.append(gdstk.rectangle(self.corner_bl, self.corner_tr, layer=self.layers['Edges']))
		
		# ---------------------------------------------------------------------
		# Build IO structures (meandered lines and bond pads)
		
		# Meander outer line: starts at (X2 and Y2)
		if self.io['same_side']:
			self.build_io_component(path_list[-1], self.io['outer'], no_bends=True)
		else:
			self.build_io_component(path_list[-1], self.io['outer'], use_alt_side=True, no_bends=True)
		
		# Meander inner line
		self.build_io_component(path_list[0], self.io['inner'], no_bends=True)
		
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
			
			if 1 in self.reticle_fiducial['corners']:
				self.fiducials.append(gdstk.rectangle( (x_left, y_up-l_fid), (x_left+w_fid, y_up), layer=self.layers["NbTiN"]) )
				self.fiducials.append(gdstk.rectangle( (x_left, y_up-w_fid), (x_left+l_fid, y_up), layer=self.layers["NbTiN"]) )
			
			if 2 in self.reticle_fiducial['corners']:
				self.fiducials.append(gdstk.rectangle( (x_left, y_down ), (x_left+w_fid, y_down+l_fid), layer=self.layers["NbTiN"]) )
				self.fiducials.append(gdstk.rectangle( (x_left, y_down ), (x_left+l_fid, y_down+w_fid ), layer=self.layers["NbTiN"]) )
			
			if 3 in self.reticle_fiducial['corners']:
				self.fiducials.append(gdstk.rectangle( (x_right, y_down ), (x_right-w_fid, y_down+l_fid ), layer=self.layers["NbTiN"]) )
				self.fiducials.append(gdstk.rectangle( (x_right-l_fid, y_down ), (x_right, y_down+w_fid), layer=self.layers["NbTiN"]) )
			
			if 4 in self.reticle_fiducial['corners']:
				self.fiducials.append(gdstk.rectangle( (x_right-l_fid, y_up-w_fid ), (x_right, y_up ), layer=self.layers["NbTiN"]) )
				self.fiducials.append(gdstk.rectangle( (x_right-w_fid, y_up ), (x_right, y_up-l_fid ), layer=self.layers["NbTiN"]) )
		
		# ---------------------------------------------------------------------
		# Add objects to chip design
		
		# Add Al layer
		for pad in self.temp_pads:
			
			bl = pad[0]
			tr = pad[1]
			
			# Create Rectangle
			self.Al_pad.append(gdstk.rectangle( (bl[0], bl[1]), (tr[0], tr[1]), layer=self.layers['Aluminum'] ))
		
		#TODO: Check file for if aSi is etch or releif
		
		# Add aSi etch layer
		for pad in self.temp_pads:
			
			bl = pad[0]
			tr = pad[1]
			
			# Get direction towards edge of chip (ie. is this bond pad above or below origin)
			edge_direction = np.sign(bl[1])
			
			# Create Rectangle
			if edge_direction < 0: # Pad on bottom of chip
				bond_pad_hole_positive = gdstk.rectangle( (bl[0]-self.io['aSi_etch']['x_buffer_um'], bl[1]-self.io['aSi_etch']['extend_towards_edge_um']), (tr[0]+self.io['aSi_etch']['x_buffer_um'], tr[1]-self.io['pads']['height_um']+self.io['pads']['pad_exposed_height_um']) )
			else:
				bond_pad_hole_positive = gdstk.rectangle( (bl[0]-self.io['aSi_etch']['x_buffer_um'], bl[1]+self.io['pads']['height_um']-self.io['pads']['pad_exposed_height_um']), (tr[0]+self.io['aSi_etch']['x_buffer_um'], tr[1]+self.io['aSi_etch']['extend_towards_edge_um'] ) )
				
			# Trim the rectangle so it doesn't extend over the edge of the chip
			new_bpl_list = gdstk.boolean(self.bulk, bond_pad_hole_positive, "and", layer=self.layers["aSi"])
			for nbpl in new_bpl_list:
				self.bond_pad_hole.append(nbpl)
		
		# Add groundplane layer
		for pad in self.temp_pads:
			
			bl = pad[0]
			tr = pad[1]
			
			# Get offset parameters
			baseline_offset = self.chip_size_um[1]//2 # Offset to translate (y = 0) to actual bottom of chip
			just_offset = self.chip_size_um[0]//2 # Offset to translate (x = 0) to actual left side of chip
			
			# Get direction towards edge of chip (ie. is this bond pad above or below origin)
			edge_direction = np.sign(bl[1])
			
			# Create Rectangle
			if edge_direction < 0: # Pad on bottom of chip
				bond_pad_hole_positive = gdstk.FlexPath((bl[0]+self.io['pads']['width_um']/2, -baseline_offset-10), self.io['pads']['width_um']+self.io['pads']['gnd_gap_um']*2)
				bond_pad_hole_positive.segment((tr[0]-self.io['pads']['width_um']/2, tr[1]), self.io['pads']['width_um']+self.io['pads']['gnd_gap_um']*2)
				
				# Loop over each section of CPW taper and add it
				last_height = tr[1]
				for idx, seg_l in enumerate(self.io['faux_cpw_taper']['cpw_section_lengths_um']):
					
					seg_w = self.io['faux_cpw_taper']['cpw_widths_um'][idx]
					seg_g = self.io['faux_cpw_taper']['cpw_gaps_um'][idx]
					
					last_height += seg_l
					bond_pad_hole_positive.segment((tr[0]-self.io['pads']['width_um']/2, last_height), seg_w+seg_g*2)
			else:
				bond_pad_hole_positive = gdstk.FlexPath((tr[0]-self.io['pads']['width_um']/2, baseline_offset+10), self.io['pads']['width_um']+self.io['pads']['gnd_gap_um']*2)
				bond_pad_hole_positive.segment((bl[0]+self.io['pads']['width_um']/2, bl[1]), self.io['pads']['width_um']+self.io['pads']['gnd_gap_um']*2)
				
				# Loop over each section of CPW taper and add it
				last_height = bl[1]
				for idx, seg_l in enumerate(self.io['faux_cpw_taper']['cpw_section_lengths_um']):
					
					seg_w = self.io['faux_cpw_taper']['cpw_widths_um'][idx]
					seg_g = self.io['faux_cpw_taper']['cpw_gaps_um'][idx]
					
					last_height -= seg_l
					bond_pad_hole_positive.segment((tr[0]-self.io['pads']['width_um']/2, last_height), seg_w+seg_g*2)
			
			# Trim the rectangle so it doesn't extend over the edge of the chip
			gnd_list = gdstk.boolean(self.gnd, bond_pad_hole_positive, "not", layer=self.layers["GND"])
			
			self.gnd = gnd_list
		
		# This should be moved to build I think
		if self.NbTiN_is_etch:
			info(f"Inverting layers to calculate etch pattern.")
			inv_paths = gdstk.boolean(self.bulk, self.path, "not", layer=self.layers["NbTiN"])
			info(f"Adding etch layers (Inverted)")
			for ip in inv_paths:
				debug(f"Added path from inverted path list.")
				
				critical("Need to implement this! New version of 'target_cell.add(ip)'")
				# target_cell.add(ip)
			
			warning("NbTiN is etch needs to be fully implemented!")
			
			# TODO: Invert fiducials
			# TODO: Invert io components
			# TODO: Invert graphics
		else:
			info(f"Adding metal layers (Non-inverted)")
			
			if self.reticle_fiducial['on_gnd']:
				
				# Subtract text from ground
				for f in self.fiducials:
					self.gnd = gdstk.boolean(self.gnd, f, "not", layer=self.layers["GND"])
				
				# Clear fiducial list
				self.fiducials = []
	
		return True
		
		
	def build_standard(self):
		''' Builds the chip with non-zero spirals'''
		
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
		
		##================ MAKE STEPPED IMPEDANCE STRUCTURES
		#
		
		def approx_sign(val:float, tol:float):
			
			if np.abs(val) <= np.abs(tol):
				return 0
			
			return np.sign(val)
		
		if not self.use_steps:
			self.path = gdstk.FlexPath(path_list, self.tlin['Wcenter_um'], tolerance=1e-2, layer=self.layers["NbTiN"])
		
		else:
			
			# Prepare a flexpath with first point
			self.path = gdstk.FlexPath(path_list[0], width=self.ZH_step_width_um, joins='natural', tolerance=3e-2)
			
			# Scan over path, checking for distance traveled
			point_last = path_list[0]
			distance = 0
			is_on_step = False
			# for pl in path_list[1:]:
			
			all_x_debug = [path_list[0][0]]
			all_y_debug = [path_list[0][1]]
			
			x_wide = []
			x_narrow = []
			y_wide = []
			y_narrow = []
			
			num_ZL_sections = 0
			
			path_list_idx = 1
			while path_list_idx < len(path_list):
				# Using a while-loop because when a point is interpolated, it is added to the list,
				# and it's not cool to for-loop over a dynamically changing list. Note we're 
				# starting at index 1!
				
				# Save a local variable for ease of use, like in a for loop
				pl = path_list[path_list_idx]
				
				# Update distance 
				segment_length = np.sqrt( (pl[0]-point_last[0])**2 + (pl[1]-point_last[1])**2 )
				new_distance = distance + segment_length
				
				# Pick between step spacing or length
				if is_on_step:
					targ_distance = self.step_length_um
				else:
					targ_distance = self.step_spacing_um
				
				# If past distance, change step
				if new_distance >= targ_distance: # Need to interpolate and add step!
					
					# Interpolate new point to use
					frac_usage = (targ_distance - distance)/segment_length # Fraction of segment length needed to get to target step length
					dx = pl[0]-point_last[0]
					dy = pl[1]-point_last[1]
					interp_x = dx*frac_usage + point_last[0] # Get interpolated X
					interp_y = dy*frac_usage + point_last[1] # Get interpolated Y
					
					e_x = dx/segment_length*self.steps['step_perturbation_um']
					e_y = dy/segment_length*self.steps['step_perturbation_um']
					
					if (e_x**2 + e_y**2)**0.5 > self.steps['step_perturbation_um']*1.01:
						error(f"ex = {e_x}, e_y = {e_y}")
					
					if frac_usage >= 1:
						print(f"ex = {e_x}, e_y = {e_y}")
					
					interp_x_e = interp_x - e_x # Get interpolated X slightly perturbed
					interp_y_e = interp_y - e_y # Get interpolated Y slightly perturbed
					
					# Add interpolated points to path
					if is_on_step:
						self.path.segment([interp_x_e, interp_y_e], width=self.step_width_um)
						self.path.segment([interp_x, interp_y], width=self.ZH_step_width_um)
						
						x_wide.append(interp_x_e)
						x_narrow.append(interp_x)
						
						y_wide.append(interp_y_e)
						y_narrow.append(interp_y)
					else:
						
						num_ZL_sections += 1
						
						self.path.segment([interp_x_e, interp_y_e], width=self.ZH_step_width_um)
						self.path.segment([interp_x, interp_y], width=self.step_width_um)
						
						x_narrow.append(interp_x_e)
						x_wide.append(interp_x)
						
						y_narrow.append(interp_y_e)
						y_wide.append(interp_y)
					
					all_x_debug.append(interp_x_e)
					all_x_debug.append(interp_x)
					all_y_debug.append(interp_y_e)
					all_y_debug.append(interp_y)
					
					is_on_step = (not is_on_step) # Toggle width
					point_last = [interp_x, interp_y] # Update last point
					distance = 0 # Reset distance
					#NOTE: Do NOT increment index!
					
				else: # Continuing last step - just add the exisiting point to the list
					
					# Add to path
					if is_on_step:
						self.path.segment(pl, width=self.step_width_um)
					else:
						self.path.segment(pl, width=self.ZH_step_width_um)
					
					all_x_debug.append(pl[0])
					all_y_debug.append(pl[1])
					
					# Update last point
					point_last = pl
					distance = new_distance
					
					# Increment index
					path_list_idx += 1
		
		# plt.plot(all_x_debug, all_y_debug, marker='.', linewidth=0.2, linestyle=':')
		# plt.scatter(x_narrow, y_narrow, marker='v')
		# plt.scatter(x_wide, y_wide, marker='^')
		# plt.show()
		
		
			info(f"Added {num_ZL_sections} low impedance steps.")
		
		#
		##================ END MAKE STEPPED IMPEDANCE STRUCTURES
		
		
		# Invert selection if color is etch
		self.bulk = gdstk.rectangle(self.corner_bl, self.corner_tr, layer=self.layers['Edges'])
		self.gnd.append(gdstk.rectangle(self.corner_bl, self.corner_tr, layer=self.layers['Edges']))
		
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
			
			if 1 in self.reticle_fiducial['corners']:
				self.fiducials.append(gdstk.rectangle( (x_left, y_up-l_fid), (x_left+w_fid, y_up), layer=self.layers["NbTiN"]) )
				self.fiducials.append(gdstk.rectangle( (x_left, y_up-w_fid), (x_left+l_fid, y_up), layer=self.layers["NbTiN"]) )
			
			if 2 in self.reticle_fiducial['corners']:
				self.fiducials.append(gdstk.rectangle( (x_left, y_down ), (x_left+w_fid, y_down+l_fid), layer=self.layers["NbTiN"]) )
				self.fiducials.append(gdstk.rectangle( (x_left, y_down ), (x_left+l_fid, y_down+w_fid ), layer=self.layers["NbTiN"]) )
			
			if 3 in self.reticle_fiducial['corners']:
				self.fiducials.append(gdstk.rectangle( (x_right, y_down ), (x_right-w_fid, y_down+l_fid ), layer=self.layers["NbTiN"]) )
				self.fiducials.append(gdstk.rectangle( (x_right-l_fid, y_down ), (x_right, y_down+w_fid), layer=self.layers["NbTiN"]) )
			
			if 4 in self.reticle_fiducial['corners']:
				self.fiducials.append(gdstk.rectangle( (x_right-l_fid, y_up-w_fid ), (x_right, y_up ), layer=self.layers["NbTiN"]) )
				self.fiducials.append(gdstk.rectangle( (x_right-w_fid, y_up ), (x_right, y_up-l_fid ), layer=self.layers["NbTiN"]) )
		
		# ---------------------------------------------------------------------
		# Add objects to chip design
		
		# Add Al layer
		for pad in self.temp_pads:
			
			bl = pad[0]
			tr = pad[1]
			
			# Create Rectangle
			self.Al_pad.append(gdstk.rectangle( (bl[0], bl[1]), (tr[0], tr[1]), layer=self.layers['Aluminum'] ))
		
		#TODO: Check file for if aSi is etch or releif
		
		# Add aSi etch layer
		for pad in self.temp_pads:
			
			bl = pad[0]
			tr = pad[1]
			
			# Get direction towards edge of chip (ie. is this bond pad above or below origin)
			edge_direction = np.sign(bl[1])
			
			# Create Rectangle
			if edge_direction < 0: # Pad on bottom of chip
				bond_pad_hole_positive = gdstk.rectangle( (bl[0]-self.io['aSi_etch']['x_buffer_um'], bl[1]-self.io['aSi_etch']['extend_towards_edge_um']), (tr[0]+self.io['aSi_etch']['x_buffer_um'], tr[1]-self.io['pads']['height_um']+self.io['pads']['pad_exposed_height_um']) )
			else:
				bond_pad_hole_positive = gdstk.rectangle( (bl[0]-self.io['aSi_etch']['x_buffer_um'], bl[1]+self.io['pads']['height_um']-self.io['pads']['pad_exposed_height_um']), (tr[0]+self.io['aSi_etch']['x_buffer_um'], tr[1]+self.io['aSi_etch']['extend_towards_edge_um'] ) )
				
			# Trim the rectangle so it doesn't extend over the edge of the chip
			new_bpl_list = gdstk.boolean(self.bulk, bond_pad_hole_positive, "and", layer=self.layers["aSi"])
			for nbpl in new_bpl_list:
				self.bond_pad_hole.append(nbpl)
		
		# Add groundplane layer
		for pad in self.temp_pads:
			
			bl = pad[0]
			tr = pad[1]
			
			# Get offset parameters
			baseline_offset = self.chip_size_um[1]//2 # Offset to translate (y = 0) to actual bottom of chip
			just_offset = self.chip_size_um[0]//2 # Offset to translate (x = 0) to actual left side of chip
			
			# Get direction towards edge of chip (ie. is this bond pad above or below origin)
			edge_direction = np.sign(bl[1])
			
			# Create Rectangle
			if edge_direction < 0: # Pad on bottom of chip
				bond_pad_hole_positive = gdstk.FlexPath((bl[0]+self.io['pads']['width_um']/2, -baseline_offset-10), self.io['pads']['width_um']+self.io['pads']['gnd_gap_um']*2)
				bond_pad_hole_positive.segment((tr[0]-self.io['pads']['width_um']/2, tr[1]), self.io['pads']['width_um']+self.io['pads']['gnd_gap_um']*2)
				
				# Loop over each section of CPW taper and add it
				last_height = tr[1]
				for idx, seg_l in enumerate(self.io['faux_cpw_taper']['cpw_section_lengths_um']):
					
					seg_w = self.io['faux_cpw_taper']['cpw_widths_um'][idx]
					seg_g = self.io['faux_cpw_taper']['cpw_gaps_um'][idx]
					
					last_height += seg_l
					bond_pad_hole_positive.segment((tr[0]-self.io['pads']['width_um']/2, last_height), seg_w+seg_g*2)
			else:
				bond_pad_hole_positive = gdstk.FlexPath((tr[0]-self.io['pads']['width_um']/2, baseline_offset+10), self.io['pads']['width_um']+self.io['pads']['gnd_gap_um']*2)
				bond_pad_hole_positive.segment((bl[0]+self.io['pads']['width_um']/2, bl[1]), self.io['pads']['width_um']+self.io['pads']['gnd_gap_um']*2)
				
				# Loop over each section of CPW taper and add it
				last_height = bl[1]
				for idx, seg_l in enumerate(self.io['faux_cpw_taper']['cpw_section_lengths_um']):
					
					seg_w = self.io['faux_cpw_taper']['cpw_widths_um'][idx]
					seg_g = self.io['faux_cpw_taper']['cpw_gaps_um'][idx]
					
					last_height -= seg_l
					bond_pad_hole_positive.segment((tr[0]-self.io['pads']['width_um']/2, last_height), seg_w+seg_g*2)
			
			# Trim the rectangle so it doesn't extend over the edge of the chip
			gnd_list = gdstk.boolean(self.gnd, bond_pad_hole_positive, "not", layer=self.layers["GND"])
			
			# # Unpack list to single object
			# if len(gnd_list) != 1:
			# 	error("Failed to generate ground plane")
			# 	return False
			# else:
			# 	self.gnd = gnd_list[0]
			self.gnd = gnd_list
			
		# ---------------------------------------------------------------------
		# Add objects to chip design
		
		# warning("Remember to run apply_objects() now that it isn't automatic in build().")
		# if self.NbTiN_is_etch:
		# 	info(f"Inverting layers to calculate etch pattern.")
		# 	inv_paths = gdstk.boolean(self.bulk, self.path, "not", layer=self.layers["NbTiN"])
		# 	info(f"Adding etch layers (Inverted)")
		# 	for ip in inv_paths:
		# 		debug(f"Added path from inverted path list.")
		# 		self.main_cell.add(ip)
			
		# 	# TODO: Invert fiducials
		# 	# TODO: Invert io components
		# 	# TODO: Invert graphics
		# else:
		# 	info(f"Adding metal layers (Non-inverted)")
		# 	self.main_cell.add(self.path)
		# 	self.main_cell.add(self.bulk)
			
			
				
		# 	if self.reticle_fiducial['on_gnd']:
		# 		# Get polygon
		# 		new_gnd = []
		# 		for poly in self.main_cell.polygons:
		# 			if poly.layer == self.layers['GND']:
		# 				new_gnd.append(poly)
				
		# 		# Check ground plane was found
		# 		if len(new_gnd) < 1:
		# 			error("Failed to find ground plane. Cannot add graphic to ground plane.")
		# 			return False
				
		# 		# Remove old ground plane
		# 		self.main_cell.remove(*new_gnd)
				
		# 		# Subtract text from ground
		# 		for f in self.fiducials:
		# 			new_gnd = gdstk.boolean(new_gnd, f, "not", layer=self.layers["GND"])
				
		# 		# Replace ground plane in cell
		# 		for ng in new_gnd:
		# 			self.main_cell.add(ng)
				
		# 	else:
		# 		for f in self.fiducials:
		# 			self.main_cell.add(f)
		
		# This should be moved to build I think
		if self.NbTiN_is_etch:
			info(f"Inverting layers to calculate etch pattern.")
			inv_paths = gdstk.boolean(self.bulk, self.path, "not", layer=self.layers["NbTiN"])
			info(f"Adding etch layers (Inverted)")
			for ip in inv_paths:
				debug(f"Added path from inverted path list.")
				
				critical("Need to implement this! New version of 'target_cell.add(ip)'")
				# target_cell.add(ip)
			
			warning("NbTiN is etch needs to be fully implemented!")
			
			# TODO: Invert fiducials
			# TODO: Invert io components
			# TODO: Invert graphics
		else:
			info(f"Adding metal layers (Non-inverted)")
			
			if self.reticle_fiducial['on_gnd']:
				
				# Subtract text from ground
				for f in self.fiducials:
					self.gnd = gdstk.boolean(self.gnd, f, "not", layer=self.layers["GND"])
				
				# Clear fiducial list
				self.fiducials = []
	
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
	
	def build_io_component(self, start_point, location_rules:dict, use_alt_side:bool=False, no_bends:bool=False):
		""" Builds the meandered lines and bond pad for one conductor"""
		
		if no_bends:
			self.build_io_component_through(start_point, location_rules, use_alt_side)
		else:
			self.build_io_component_standard(start_point, location_rules, use_alt_side)
	
	def build_io_component_through(self, start_point, location_rules:dict, use_alt_side:bool):
		""" Builds bond pad and through line for one conductor"""
				
		debug("Adding taper and bond pad.")
		
		# Get offset parameters
		baseline_offset = self.chip_size_um[1]//2 # Offset to translate (y = 0) to actual bottom of chip
		just_offset = self.chip_size_um[0]//2 # Offset to translate (x = 0) to actual left side of chip
		
		# Get current point on line - initialize w/ end of bond pad
		current_point = [location_rules['x_pad_offset_um']-just_offset, -self.pad_height+baseline_offset]
		
		# Create list of points and widths
		point_list = []
		width_list = []
		
		# Record how long along path you are, so know what taper width should be
		dist = 0
			
		# Run until break
		running = True
		while running:
			
			if use_alt_side:
				# Update position
				current_point[1] -= self.io['taper']['segment_length_um']
				dist += self.io['taper']['segment_length_um']
				
				# Check for end
				if current_point[1] <= start_point[1]:
					current_point[1] = start_point[1]
					running = False
				
				# Add to lists
				point_list.append((current_point[0], current_point[1]))
				width_list.append(self.calc_taper_width(dist))
			else:
				# Update position
				current_point[1] += self.io['taper']['segment_length_um']
				dist += self.io['taper']['segment_length_um']
				
				# Check for end
				if current_point[1] >= start_point[1]:
					current_point[1] = start_point[1]
					running = False
				
				# Add to lists
				point_list.append((current_point[0], current_point[1]))
				width_list.append(self.calc_taper_width(dist))
		
		# Initialize IO structure with bond pad
		if not use_alt_side:
			
			# Create rectangular bond pad area
			io_line = gdstk.FlexPath((location_rules['x_pad_offset_um']-just_offset, self.io['pads']['chip_edge_buffer_um']-baseline_offset), self.io['pads']['width_um'], layer=self.layers["NbTiN"])
			io_line.segment((location_rules['x_pad_offset_um']-just_offset, self.io['pads']['chip_edge_buffer_um']+self.io['pads']['height_um']-baseline_offset), self.io['pads']['width_um'])
			
			# Loop over each section of CPW taper and add it
			last_height = self.io['pads']['chip_edge_buffer_um']+self.io['pads']['height_um']-baseline_offset
			for seg_w, seg_l in zip(self.io['faux_cpw_taper']['cpw_widths_um'], self.io['faux_cpw_taper']['cpw_section_lengths_um']):
				last_height += seg_l
				io_line.segment((location_rules['x_pad_offset_um']-just_offset, last_height), seg_w)
			
			# Record bond pad dimensions TODO: DOes this need to changge for CPW taper?
			pad_bb = []
			pad_bb.append([location_rules['x_pad_offset_um']-just_offset-self.io['pads']['width_um']/2, self.io['pads']['chip_edge_buffer_um']-baseline_offset]) # bottom left
			pad_bb.append([location_rules['x_pad_offset_um']-just_offset+self.io['pads']['width_um']/2, self.io['pads']['chip_edge_buffer_um']+self.io['pads']['height_um']-baseline_offset]) # top right
			self.temp_pads.append(pad_bb)
		else:
			io_line = gdstk.FlexPath((location_rules['x_pad_offset_um']-just_offset, -self.io['pads']['chip_edge_buffer_um']+baseline_offset), self.io['pads']['width_um'], layer=self.layers["NbTiN"])
			io_line.segment((location_rules['x_pad_offset_um']-just_offset, -self.io['pads']['chip_edge_buffer_um']-self.io['pads']['height_um']+baseline_offset), self.io['pads']['width_um'])
			
			# Loop over each section of CPW taper and add it
			last_height = -self.io['pads']['chip_edge_buffer_um']-self.io['pads']['height_um']+baseline_offset
			for seg_w, seg_l in zip(self.io['faux_cpw_taper']['cpw_widths_um'], self.io['faux_cpw_taper']['cpw_section_lengths_um']):
				last_height -= seg_l
				io_line.segment((location_rules['x_pad_offset_um']-just_offset, last_height), seg_w)
			
			# Record bond pad dimensions TODO: DOes this need to changge for CPW taper?
			pad_bb = []
			pad_bb.append([location_rules['x_pad_offset_um']-just_offset-self.io['pads']['width_um']/2, -self.io['pads']['chip_edge_buffer_um']-self.io['pads']['height_um']+baseline_offset]) # top right
			pad_bb.append([location_rules['x_pad_offset_um']-just_offset+self.io['pads']['width_um']/2, -self.io['pads']['chip_edge_buffer_um']+baseline_offset]) # bottom left
			
			self.temp_pads.append(pad_bb)
		
		# Add points and widths to curve
		for idx,pt in enumerate(point_list): # width_list):
			
			w = width_list[idx]
			
			io_line.segment(pt, w)
		
		self.io_line_list.append(io_line)
		
		taper_length = self.io['taper']['length_um']
		info(f"Total meandered line length: >{rd(dist)}< um, Taper length: >{rd(taper_length)}<.")
		
		if dist < taper_length:
			warning("Meandered line length is less than taper length! Sharp edge present.")
	
	def build_io_component_standard(self, start_point, location_rules:dict, use_alt_side:bool=False):
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
			
			# Create rectangular bond pad area
			io_line = gdstk.FlexPath((location_rules['x_pad_offset_um']-just_offset, self.io['pads']['chip_edge_buffer_um']-baseline_offset), self.io['pads']['width_um'], layer=self.layers["NbTiN"])
			io_line.segment((location_rules['x_pad_offset_um']-just_offset, self.io['pads']['chip_edge_buffer_um']+self.io['pads']['height_um']-baseline_offset), self.io['pads']['width_um'])
			
			# Loop over each section of CPW taper and add it
			last_height = self.io['pads']['chip_edge_buffer_um']+self.io['pads']['height_um']-baseline_offset
			for seg_w, seg_l in zip(self.io['faux_cpw_taper']['cpw_widths_um'], self.io['faux_cpw_taper']['cpw_section_lengths_um']):
				last_height += seg_l
				io_line.segment((location_rules['x_pad_offset_um']-just_offset, last_height), seg_w)
			
			# Record bond pad dimensions TODO: DOes this need to changge for CPW taper?
			pad_bb = []
			pad_bb.append([location_rules['x_pad_offset_um']-just_offset-self.io['pads']['width_um']/2, self.io['pads']['chip_edge_buffer_um']-baseline_offset]) # bottom left
			pad_bb.append([location_rules['x_pad_offset_um']-just_offset+self.io['pads']['width_um']/2, self.io['pads']['chip_edge_buffer_um']+self.io['pads']['height_um']-baseline_offset]) # top right
			self.temp_pads.append(pad_bb)
		else:
			io_line = gdstk.FlexPath((location_rules['x_pad_offset_um']-just_offset, -self.io['pads']['chip_edge_buffer_um']+baseline_offset), self.io['pads']['width_um'], layer=self.layers["NbTiN"])
			io_line.segment((location_rules['x_pad_offset_um']-just_offset, -self.io['pads']['chip_edge_buffer_um']-self.io['pads']['height_um']+baseline_offset), self.io['pads']['width_um'])
			
			# Loop over each section of CPW taper and add it
			last_height = -self.io['pads']['chip_edge_buffer_um']-self.io['pads']['height_um']+baseline_offset
			for seg_w, seg_l in zip(self.io['faux_cpw_taper']['cpw_widths_um'], self.io['faux_cpw_taper']['cpw_section_lengths_um']):
				last_height -= seg_l
				io_line.segment((location_rules['x_pad_offset_um']-just_offset, last_height), seg_w)
			
			# Record bond pad dimensions TODO: DOes this need to changge for CPW taper?
			pad_bb = []
			pad_bb.append([location_rules['x_pad_offset_um']-just_offset-self.io['pads']['width_um']/2, -self.io['pads']['chip_edge_buffer_um']-self.io['pads']['height_um']+baseline_offset]) # top right
			pad_bb.append([location_rules['x_pad_offset_um']-just_offset+self.io['pads']['width_um']/2, -self.io['pads']['chip_edge_buffer_um']+baseline_offset]) # bottom left
			
			self.temp_pads.append(pad_bb)
		
		# Add points and widths to curve
		for idx,pt in enumerate(point_list): # width_list):
			
			w = width_list[idx]
			
			io_line.segment(pt, w)
		
		self.io_line_list.append(io_line)
		
		taper_length = self.io['taper']['length_um']
		info(f"Total meandered line length: >{rd(dist)}< um, Taper length: >{rd(taper_length)}<.")
		
		if dist < taper_length:
			warning("Meandered line length is less than taper length! Sharp edge present.")
	
	def insert_text(self, position:list, text:str, font_path:str=None, font_size_um:float=100, tolerance=0.1, layer=None, center_justify:bool=False, right_justify:bool=False):
		''' Inserts custom text to the chip. Can use any TrueType font (rather than just the default supplied with gdstk). '''
		
		if self.graphics_on_gnd:
			
			# Check ground plane was found
			if len(self.gnd) < 1:
				error("Failed to find ground plane. Cannot add graphic to ground plane.")
				return False
			
			# Get text objects
			text_obj = render_text(text, size=font_size_um, font_path=font_path, position=position, tolerance=tolerance, layer=self.layers['NbTiN'])
			
			# Center Justify
			if center_justify:
				
				# Get bounding box
				min_x, max_x = None, None
				for to in text_obj:
					
					bb = to.bounding_box()
					
					if min_x is None or bb[0][0] < min_x:
						min_x = bb[0][0]
					
					if max_x is None or bb[1][0] > max_x:
						max_x = bb[1][0]
				
				# update position
				text_width = max_x - min_x
				position = (position[0] - text_width/2, position[1])
				
				# Re-render text
				text_obj = render_text(text, size=font_size_um, font_path=font_path, position=position, tolerance=tolerance, layer=self.layers['NbTiN'])
			
			elif right_justify:
				
				# Get bounding box
				min_x, max_x = None, None
				for to in text_obj:
					
					bb = to.bounding_box()
					
					if min_x is None or bb[0][0] < min_x:
						min_x = bb[0][0]
					
					if max_x is None or bb[1][0] > max_x:
						max_x = bb[1][0]
				
				# update position
				text_width = max_x - min_x
				position = (position[0] - text_width, position[1])
				
				# Re-render text
				text_obj = render_text(text, size=font_size_um, font_path=font_path, position=position, tolerance=tolerance, layer=self.layers['NbTiN'])
			
			# Subtract text from ground
			for to in text_obj:
				self.gnd = gdstk.boolean(self.gnd, text_obj, "not", layer=self.layers["GND"])
			
		else:
		
			# Get default layer
			if layer is None:
				layer = self.layers['NbTiN']
			
			# Get text objects
			text_obj = render_text(text, size=font_size_um, font_path=font_path, position=position, tolerance=tolerance, layer=layer)
			
			# Write to design
			for to in text_obj:
				self.text_object_list.append(to)
	
	def insert_graphic(self, position:list, gds_filename:str, width_um:float=-1, read_layer:int=1, read_datatype:int=0, write_layer:int=None, write_datatype:int=None):
		''' Accepts a GDS file and applies the graphic to the chip. '''
		
		read_filt = {(read_layer, read_datatype)}
			
		# Get default layer/datatype
		if write_layer is None:
			write_layer = self.layers['NbTiN']
		if write_datatype is None:
			write_datatype = 0
		
		# Read GDS File
		try:
			lib_in = gdstk.read_gds(gds_filename, filter=read_filt)
		except:
			error(f"Failed to read file '>{gds_filename}<'.")
			return False
		
		# Access top level cell
		cell_in = lib_in.top_level()
		
		# Access polygons
		all_polys = cell_in[0].polygons
		
		# Get all bounding boxes
		all_bb = []
		for poly in all_polys:
			# Check current size and scale appropriately
			bb = poly.bounding_box()
			all_bb.append([[bb[0][0], bb[0][1]], [bb[1][0], bb[1][1]]])
		
		# Get master bounding box
		bb = all_bb[0]
		for bb_ in all_bb:
			bb[0][0] = min(bb[0][0], bb_[0][0])
			bb[0][1] = min(bb[0][1], bb_[0][1])
			bb[1][0] = max(bb[1][0], bb_[1][0])
			bb[1][1] = max(bb[1][1], bb_[1][1])
		
		# Scan over all polygons
		for poly in all_polys:
			
			# Scale
			if width_um > 0:
				width = bb[1][0]-bb[0][0]
				poly.scale(width_um/width)
				info(f"Scaling graphic to width=>{width_um} um<.")
			
			# Move to requested position
			poly.translate(position[0]-bb[0][0], position[1]-bb[0][1])
		
		if self.graphics_on_gnd:
			
			# Check ground plane was found
			if len(self.gnd) < 1:
				error("Failed to find ground plane. Cannot add graphic to ground plane.")
				return False
			
			# Subtract text from ground
			for poly in all_polys:
				self.gnd = gdstk.boolean(self.gnd, poly, "not", layer=self.layers["GND"])
				
		else:
			
			# Scan over all polygons
			for poly in all_polys:
			
				# Add to main cell
				self.main_cell.add(poly)
				if write_layer is not None:
					poly.layer = write_layer
				if write_datatype is not None:
					poly.datatype = write_datatype
		
		info(f"Added graphic from file '>{gds_filename}<'.")
		
		return True
	
	def write(self, filename:str):
		
		if DUMMY_MODE:
			info(f"Skipping write GDS file >DUMMY_MODE<=>TRUE<.")
		else:
			self.lib.write_gds(filename)
			info(f"Wrote GDS file {MPrC}'{filename}'{StdC}")
		
		