from core import *

##---------------------------- Setup Scripts ---------------------------------



def create_chip(tlin_width:float, model_str:str):
	
	# Prepare fonts
	futura = os.path.join("assets", "futura", "futura medium bt.ttf")
	chicago = os.path.join("tests", "Chicago.ttf")
	selected_font = futura
	text_size = 125
	line_gap = 35
	baseline = -4900
	
	##---------------------------- Design 1 ---------------------------------

	# Create first chip design
	chip_d1 = ChipDesign()
	chip_d1.read_conf(os.path.join("designs", "MC-2024Q1V-D1-AusfA.json"))
	
	# Overwrite width
	chip_d1.tlin['Wcenter_um'] = tlin_width
	
	chip_d1.build()

	chip_d1.insert_text((0, -4000+line_gap+text_size), "LENGTH", selected_font, text_size, center_justify=True)
	chip_d1.insert_text((0, -4000), f"4.1 mm", selected_font, text_size, center_justify=True)

	##---------------------------- Design 2 ---------------------------------

	# Create first chip design
	chip_d2 = ChipDesign()
	chip_d2.read_conf(os.path.join("designs", "MC-2024Q1V-D2-AusfA.json"))
	
	# Overwrite width
	chip_d2.tlin['Wcenter_um'] = tlin_width
	
	chip_d2.build()

	chip_d2.insert_text((0, -4000+line_gap+text_size), "LENGTH", selected_font, text_size, center_justify=True)
	chip_d2.insert_text((0, -4000), f"43.1 mm", selected_font, text_size, center_justify=True)

	##---------------------------- Design 3 ---------------------------------

	# Create first chip design
	chip_d3 = ChipDesign()
	chip_d3.read_conf(os.path.join("designs", "MC-2024Q1V-D3-AusfA.json"))
	
	# Overwrite width
	chip_d3.tlin['Wcenter_um'] = tlin_width
	
	chip_d3.build()

	text_size = 125
	line_gap = 35
	baseline = 3500
	justify_line = -1600

	chip_d3.insert_text((justify_line, baseline+line_gap*2+2*text_size), f"C-2024-{model_str}", selected_font, text_size)
	chip_d3.insert_text((justify_line, baseline+line_gap+text_size), "FREQUENCY CONVERTER", selected_font, text_size)
	chip_d3.insert_text((justify_line, baseline), f"WIDTH = {tlin_width} um", selected_font, text_size)

	chip_d3.insert_text((0, -4000+line_gap+text_size), "LENGTH", selected_font, text_size, center_justify=True)
	chip_d3.insert_text((0, -4000), f"454.6 mm", selected_font, text_size, center_justify=True)

	chip_d3.insert_graphic((600, -4800), os.path.join("assets", "graphics", "CU.gds"), 350)
	chip_d3.insert_graphic((600, -4300), os.path.join("assets", "graphics", "NIST.gds"), 1000, read_layer=10)

	#------------------------- Create Master Design ---------------------

	chip_meister = MultiChipDesign(3)

	chip_meister.read_conf("Multi_2024Q1.json")
	chip_meister.add_design(chip_d1, rotation=0, translation=[-2100, 0])
	chip_meister.add_design(chip_d2, rotation=0, translation=[-1300, 0])
	chip_meister.add_design(chip_d3, rotation=0, translation=[800, 0])

	chip_meister.build()
	chip_meister.apply_objects()

	chip_meister.write(os.path.join("GDS", f"MultiChip_2024Q1_{model_str}.gds"))

# Define models
model_names = ["A", "B", "C", "D", "E"]
widths = [2.5, 3, 3.3, 3.7, 4.4]

# Create each
for model,w in zip(model_names, widths):
	
	create_chip(w, model)