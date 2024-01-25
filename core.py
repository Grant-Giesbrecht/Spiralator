import gdstk
import os
import json
import numpy as np
import logging
import getopt
import sys
from colorama import Fore, Back, Style

PI = 3.1415926535

#-----------------------------------------------------------
# Parse arguments and initialize logger

LOG_LEVEL = logging.ERROR

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
PrC = Fore.YELLOW
MPrC = Fore.LIGHTCYAN_EX
StdC = Fore.LIGHTBLUE_EX
quiet_color = Fore.WHITE
# logging.basicConfig(stream=sys.stdout, format='%(asctime)s - %(message)s', level=logging.INFO)
logging.basicConfig(format=f'::{PrC}%(levelname)s{Style.RESET_ALL}::{StdC} %(message)s{quiet_color} (Received at %(asctime)s){Style.RESET_ALL}', level=LOG_LEVEL)

# Logger initialized
#-----------------------------------------------------------

class ChipDesign:
	
	def __init__(self):
		
		# Design specifications
		self.name = "void" # Name of design
		self.chip_size_um = [] # Size of chip [x, y] 
		self.spiral = {} # Spiral design
		self.reversal = {} # Specs for how build reversal of spiral at center
		self.tlin = {} # TLIN specifications
		self.is_etch = False # If true, regions specify etch. Otherwise, regions specify metal/etc layer presence. Equivalent to whether or not design is inverted.
		
		self.lib = gdstk.Library()
		self.main_cell = self.lib.new_cell("MAIN")
		self.layers = {"NbTiN": 10, "Edges": 20}
	
	def read_conf(self, filename:str):
		
		# Open core.json
		try:
			with open(os.path.join(filename)) as f:
				file_data = json.load(f)
		except Exception as e:
			logging.error(f"Failed to read file: {filename} ({e})")
			return False
		
		# Add logger statement
		logging.info(f"Read file {filename}")
		
		# Assign to local variables
		for k in file_data.keys():
			setattr(self, k, file_data[k])
			fdk = file_data[k]
			logging.debug(f"Writing value {MPrC}{fdk}{StdC} to variable <{MPrC}{k}{StdC}> {filename}")
		
		# Return
		return True
	
	def set(self, param:str, val):
		pass
	
	def build(self):
		""" Creates the chip design from the specifications. """
		
		# ---------------------------------------------------------------------
		# Build spiral
		
		logging.info("Building chip")
		
		spiral_num = self.spiral['num_rotations']//2
		spiral_b = self.spiral['spacing_um']/2/PI
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
		
		# Change format
		path_list1 = [(x_, y_) for x_, y_ in zip(X1, Y1)]
		path_list1.reverse()
		path_list2 = [(x_, y_) for x_, y_ in zip(X2, Y2)]
		circ_list1 = [(x_, y_) for x_, y_ in zip(Xc1, Yc1)]
		circ_list1.reverse()
		circ_list2 = [(x_, y_) for x_, y_ in zip(Xc2, Yc2)]
		path_list = path_list1 + circ_list1 + circ_list2 + path_list2
		
		# Create FlexPath object for full spiral + reversal
		path = gdstk.FlexPath(path_list, self.tlin['Wcenter_um'], tolerance=1e-2, layer=self.layers["NbTiN"])
		
		# Invert selection if color is etch
		corner_bl = (-self.chip_size_um[0]//2, -self.chip_size_um[1]//2)
		corner_tr = (self.chip_size_um[0]//2, self.chip_size_um[1]//2)
		bulk = gdstk.rectangle(corner_bl, corner_tr, layer=self.layers['Edges'])
		
		if self.is_etch:
			logging.info(f"Inverting layers to calculate etch pattern.")
			inv_paths = gdstk.boolean(bulk, path, "not", layer=self.layers["NbTiN"])
			logging.info(f"Adding etch layers (Inverted)")
			for ip in inv_paths:
				logging.debug(f"Added path from inverted path list.")
				self.main_cell.add(ip)
		else:
			logging.info(f"Adding metal layers (Non-inverted)")
			self.main_cell.add(path)
			self.main_cell.add(bulk)
	
	def write(self, filename:str):
		
		logging.info(f"Writing GDS file {MPrC}'{filename}'{StdC}")
		
		self.lib.write_gds(filename)