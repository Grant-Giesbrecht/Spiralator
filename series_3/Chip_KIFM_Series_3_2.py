from spiralator.core import *

##---------------------------- Setup Scripts ---------------------------------



def create_chip(tlin_width:float, model_str:str, repo_path, design_path, conf_X):

	
	# Prepare fonts
	futura = "C:\\Users\\grant\\Documents\\GitHub\\Spiralator\\assets\\futura\\futura medium bt.ttf"
	# chicago = os.path.join("tests", "Chicago.ttf")
	selected_font = futura
	text_size = 125
	line_gap = 35
	baseline = -4900

	# Create first chip design
	chip_d3 = ChipDesign()
	# chip_d3.read_conf(os.path.join("designs", "MC-2024Q1V-D3-AusfA.json"))
	chip_d3.read_conf(conf_X)
	
	# Overwrite width
	chip_d3.tlin['Wcenter_um'] = tlin_width
	
	chip_d3.build()

	text_size = 125
	line_gap = 35
	baseline = 4550
	justify_line = -2270
	
	text_size = 125
	line_gap = 35
	baseline = 4150
	justify_line = -1300
	
	chip_d3.insert_text((justify_line, baseline+line_gap*3.25+3.25*text_size), f"KINETIC INDUCTANCE", selected_font, text_size, center_justify=True)
	chip_d3.insert_text((justify_line, baseline+line_gap*2.25+2.25*text_size), f"FREQUENCY CONVERTER", selected_font, text_size, center_justify=True)
	chip_d3.insert_text((justify_line, baseline+line_gap+text_size), f"SERIES-3.2 Mdl. {model_str}", selected_font, text_size, center_justify=True)
	chip_d3.insert_text((justify_line, baseline), f"WIDTH = {tlin_width} µm", selected_font, text_size, center_justify=True)
	
	# chip_d3.insert_text((justify_line, baseline+line_gap*2+2*text_size), f"KIFM SERIES-3 Mdl. {model_str}", selected_font, text_size)# chip_d3.insert_text((justify_line, baseline+line_gap+text_size), "FREQUENCY CONVERTER", selected_font, text_size)
	# chip_d3.insert_text((justify_line, baseline), f"WIDTH = {tlin_width} um", selected_font, text_size)

	chip_d3.insert_text((-1200, -4800+line_gap+text_size), "NO STEPS", selected_font, text_size, center_justify=True)
	chip_d3.insert_text((-1200, -4800), f"L = 1119.71 mm", selected_font, text_size, center_justify=True)

	chip_d3.insert_graphic((1520, -4800), os.path.join(repo_path, "assets", "graphics", "CU.gds"), 350)
	chip_d3.insert_graphic((1200, -4400), os.path.join(repo_path, "assets", "graphics", "NIST.gds"), 1000, read_layer=10)
	
	# chip_d3.insert_graphic((920, 4125), os.path.join("assets", "graphics", "CU.gds"), 350)
	# chip_d3.insert_graphic((600, 4525), os.path.join("assets", "graphics", "NIST.gds"), 1000, read_layer=10)

	#------------------------- Create Master Design ---------------------

	# chip_d1.write(os.path.join("GDS_2", f"KIFM_Ser-3_Mdl-{model_str}.gds"))

	chip_meister = MultiChipDesign(1)

	# chip_meister.read_conf("Multi_2024Q1.json")
	chip_meister.add_design(chip_d3, rotation=0, translation=[0, 0])
	# chip_meister.add_design(chip_d2, rotation=0, translation=[-1300, 0])
	# chip_meister.add_design(chip_d3, rotation=0, translation=[800, 0])

	chip_meister.build()
	chip_meister.apply_objects()

	chip_meister.write(os.path.join(design_path, f"KIFM_Ser-3.2_Mdl-{model_str}.gds"))

REPO_PATH = "C:\\Users\\grant\\Documents\\GitHub\\Spiralator"
DESIGN_PATH_A = os.path.join(REPO_PATH, "series_3", "Series 3.2", "model_a")
DESIGN_PATH_B = os.path.join(REPO_PATH, "series_3", "Series 3.2", "model_b")
DESIGN_PATH_C = os.path.join(REPO_PATH, "series_3", "Series 3.2", "model_c")
DESIGN_PATH_D = os.path.join(REPO_PATH, "series_3", "Series 3.2", "model_d")
DESIGN_PATH_E = os.path.join(REPO_PATH, "series_3", "Series 3.2", "model_e")

# Define models
model_names = ["A", "B", "C", "D", "E"]
widths = [2.9, 3.2, 3.5, 3.9, 4.3]
design_paths = [DESIGN_PATH_A, DESIGN_PATH_B, DESIGN_PATH_C, DESIGN_PATH_D, DESIGN_PATH_E]

conf_x = os.path.join(REPO_PATH, "series_3", "Series 3.2", "KIFM_Ser3_2.json")

# Create each
for model,w,dp in zip(model_names, widths, design_paths):
	
	create_chip(w, model, REPO_PATH, dp, conf_x)