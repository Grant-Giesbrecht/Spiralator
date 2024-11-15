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
	
	# ##---------------------------- Design 1 ---------------------------------

	# Create first chip design
	chip_d1 = ChipDesign()
	chip_d1.read_conf(os.path.join("designs", "KIFM_Ser3_1_Tr1_v3.json"))
	
	# Overwrite width
	chip_d1.tlin['Wcenter_um'] = tlin_width
	
	chip_d1.build()

	# chip_d1.insert_text((0, -4000+line_gap+text_size), "LENGTH", selected_font, text_size, center_justify=True)
	# chip_d1.insert_text((0, -4000), f"4.1 mm", selected_font, text_size, center_justify=True)
	
	chip_d1.apply_objects()
	chip_d1.write(os.path.join("GDS_2", f"KIFM_Ser-3.1_Tr1_Mdl-{model_str}.gds"))
	
	# ##---------------------------- Design 2 ---------------------------------

	# Create first chip design
	chip_d2 = ChipDesign()
	chip_d2.read_conf(os.path.join("designs", "KIFM_Ser3_1_Tr3_v3.json"))
	chip_d2.configure_steps(ZL_width_um=6, ZH_width_um=2, ZL_length_um=8, ZH_length_um=264)
	
	# Overwrite width
	chip_d2.tlin['Wcenter_um'] = tlin_width
	
	chip_d2.build()

	# chip_d2.insert_text((0, -4000+line_gap+text_size), "LENGTH", selected_font, text_size, center_justify=True)
	# chip_d2.insert_text((0, -4000), f"43.1 mm", selected_font, text_size, center_justify=True)

	##---------------------------- Design 3 ---------------------------------

	# Create first chip design
	chip_d3 = ChipDesign()
	# chip_d3.read_conf(os.path.join("designs", "MC-2024Q1V-D3-AusfA.json"))
	chip_d3.read_conf(os.path.join("designs", "KIFM_Ser3_1_Tr2_v3.json"))
	
	chip_d3.configure_steps(ZL_width_um=6, ZH_width_um=2, ZL_length_um=8, ZH_length_um=264)
	
	# Overwrite width
	chip_d3.tlin['Wcenter_um'] = tlin_width
	
	chip_d3.build()

	text_size = 125
	line_gap = 35
	baseline = 4000
	justify_line = -1000
	
	chip_d3.insert_text((justify_line, baseline+line_gap*3.25+3.25*text_size), f"KINETIC INDUCTANCE", selected_font, text_size, center_justify=True)
	chip_d3.insert_text((justify_line, baseline+line_gap*2.25+2.25*text_size), f"FREQUENCY CONVERTER", selected_font, text_size, center_justify=True)
	chip_d3.insert_text((justify_line, baseline+line_gap+text_size), f"SERIES-3.1 Mdl. A", selected_font, text_size, center_justify=True)
	chip_d3.insert_text((justify_line, baseline), f"WIDTH = {tlin_width} µm", selected_font, text_size, center_justify=True)
	
	# chip_d3.insert_text((justify_line, baseline+line_gap*3.25+3.25*text_size), f"Kinetic Inductance", selected_font, text_size, center_justify=True)
	# chip_d3.insert_text((justify_line, baseline+line_gap*2.25+2.25*text_size), f"Frequency Converter", selected_font, text_size, center_justify=True)
	# chip_d3.insert_text((justify_line, baseline+line_gap+text_size), f"SERIES-3.1 MODEL A", selected_font, text_size, center_justify=True)
	# chip_d3.insert_text((justify_line, baseline), f"WIDTH = {tlin_width} µm", selected_font, text_size, center_justify=True)
	
	# chip_d3.insert_text((justify_line, baseline+line_gap*2+2*text_size), f"KIFM SERIES-3 Mdl. {model_str}", selected_font, text_size)
	# chip_d3.insert_text((justify_line, baseline+line_gap+text_size), "FREQUENCY CONVERTER", selected_font, text_size)
	# chip_d3.insert_text((justify_line, baseline), f"WIDTH = {tlin_width} um", selected_font, text_size)

	line_gap = 25
	baseline = -4900
	justify_line = -1670
	chip_d3.insert_text((justify_line, baseline+line_gap*2+2*text_size), "TRACE-1", selected_font, text_size, center_justify=False)
	chip_d3.insert_text((justify_line, baseline+line_gap+text_size), "NO STEPS", selected_font, text_size, center_justify=False)
	chip_d3.insert_text((justify_line, baseline), f"L = 8.65 mm", selected_font, text_size, center_justify=False)
	
	baseline = -4000
	justify_line = 0
	chip_d3.insert_text((justify_line, baseline+line_gap*2+2*text_size), "TRACE-2", selected_font, text_size, center_justify=True)
	chip_d3.insert_text((justify_line, baseline+line_gap+text_size), "N = 1435", selected_font, text_size, center_justify=True)
	chip_d3.insert_text((justify_line, baseline), f"L = 390.5 mm", selected_font, text_size, center_justify=True)
	
	baseline = -4900
	justify_line = 1670
	chip_d3.insert_text((justify_line, baseline+line_gap*2+2*text_size), "TRACE-3", selected_font, text_size, right_justify=True)
	chip_d3.insert_text((justify_line, baseline+line_gap+text_size), "N = <TODO>", selected_font, text_size, right_justify=True)
	chip_d3.insert_text((justify_line, baseline), f"L = 8.65 mm", selected_font, text_size, right_justify=True)

	# chip_d3.insert_graphic((600, -4800), os.path.join("assets", "graphics", "CU.gds"), 350)
	# chip_d3.insert_graphic((600, -4300), os.path.join("assets", "graphics", "NIST.gds"), 1000, read_layer=10)
	
	chip_d3.insert_graphic((920, 4125), os.path.join("assets", "graphics", "CU.gds"), 350)
	chip_d3.insert_graphic((600, 4525), os.path.join("assets", "graphics", "NIST.gds"), 1000, read_layer=10)

	#------------------------- Create Master Design ---------------------
	
	chip_d3.apply_objects()
	chip_d3.write(os.path.join("GDS_2", f"KIFM_Ser-3.1_Tr2_Mdl-{model_str}.gds"))
	
	# chip_d1.write(os.path.join("GDS_2", f"KIFM_Ser-3_Mdl-{model_str}.gds"))

	chip_meister = MultiChipDesign(2)

	# # chip_meister.read_conf("Multi_2024Q1.json")
	chip_meister.add_design(chip_d1, rotation=0, translation=[-2125, 0])
	chip_meister.add_design(chip_d3, rotation=0, translation=[0, 0])
	chip_meister.add_design(chip_d2, rotation=0, translation=[2125, 0])
	# chip_meister.add_design(chip_d3, rotation=0, translation=[800, 0])

	chip_meister.build()
	chip_meister.apply_objects()

	chip_meister.write(os.path.join("GDS_2", f"KIFM_Ser-3.1_Mdl-{model_str}.gds"))

# Define models
model_names = ["A", "B", "C"]
widths = [3.3, 3.7, 4.4]

model_names = ["C"]
widths = [3.3]

# Create each
for model,w in zip(model_names, widths):
	
	create_chip(w, model)