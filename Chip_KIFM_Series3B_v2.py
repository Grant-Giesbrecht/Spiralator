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

	# Create first chip design
	chip_d3 = ChipDesign()
	# chip_d3.read_conf(os.path.join("designs", "MC-2024Q1V-D3-AusfA.json"))
	chip_d3.read_conf(os.path.join("designs", "KIFM_Ser3B_v2.json"))
	
	# Overwrite width
	chip_d3.tlin['Wcenter_um'] = tlin_width
	
	chip_d3.build()

	text_size = 125
	line_gap = 35
	baseline = 4550
	justify_line = -2270
	
	chip_d3.insert_text((justify_line, baseline+line_gap*2+2*text_size), f"KIFM SERIES-3 Mdl. {model_str}", selected_font, text_size)
	chip_d3.insert_text((justify_line, baseline+line_gap+text_size), "FREQUENCY CONVERTER", selected_font, text_size)
	chip_d3.insert_text((justify_line, baseline), f"WIDTH = {tlin_width} um", selected_font, text_size)

	chip_d3.insert_text((-1200, -4800+line_gap+text_size), "LENGTH", selected_font, text_size, center_justify=True)
	chip_d3.insert_text((-1200, -4800), f"<TODO> mm", selected_font, text_size, center_justify=True)

	chip_d3.insert_graphic((1850, -4450), os.path.join("assets", "graphics", "CU.gds"), 350)
	chip_d3.insert_graphic((1200, -4800), os.path.join("assets", "graphics", "NIST.gds"), 1000, read_layer=10)

	#------------------------- Create Master Design ---------------------

	# chip_d1.write(os.path.join("GDS_2", f"KIFM_Ser-3_Mdl-{model_str}.gds"))

	chip_meister = MultiChipDesign(1)

	# chip_meister.read_conf("Multi_2024Q1.json")
	chip_meister.add_design(chip_d3, rotation=0, translation=[0, 0])
	# chip_meister.add_design(chip_d2, rotation=0, translation=[-1300, 0])
	# chip_meister.add_design(chip_d3, rotation=0, translation=[800, 0])

	chip_meister.build()
	chip_meister.apply_objects()

	chip_meister.write(os.path.join("GDS_2", f"KIFM_Ser-3.2_Mdl-{model_str}_v2.gds"))

# Define models
model_names = ["A", "B", "C"]
widths = [3.3, 3.7, 4.4]

# Create each
for model,w in zip(model_names, widths):
	
	create_chip(w, model)