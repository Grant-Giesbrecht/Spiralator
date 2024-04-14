from core import *

##---------------------------- Setup Scripts ---------------------------------

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
chip_d1.read_conf(os.path.join("designs", "C2024Q1_AusfC.json"))
chip_d1.build()

# Add first chip graphics
chip_d1.insert_text((600, baseline+line_gap*3+3*text_size), "C-2024-A", selected_font, text_size)
chip_d1.insert_text((600, baseline+line_gap*2+2*text_size), "FREQUENCY CONVERTER", selected_font, text_size)
chip_d1.insert_text((600, baseline+line_gap+text_size), f"UNLOADED | W = 3 um", selected_font, text_size)
chip_d1.insert_graphic((1600, -3600), os.path.join("assets", "graphics", "CU.gds"), 350)
chip_d1.insert_graphic((1000, -4000), os.path.join("assets", "graphics", "NIST.gds"), 1000, read_layer=10)

##---------------------------- Design 2 ---------------------------------

# Create first chip design
chip_d2 = ChipDesign()
chip_d2.read_conf(os.path.join("designs", "C2024Q1_AusfC.json"))
chip_d2.build()

# Add first chip graphics
chip_d2.insert_text((600, baseline+line_gap*3+3*text_size), "C-2024-A", selected_font, text_size)
chip_d2.insert_text((600, baseline+line_gap*2+2*text_size), "FREQUENCY CONVERTER", selected_font, text_size)
chip_d2.insert_text((600, baseline+line_gap+text_size), f"UNLOADED | W = 3 um", selected_font, text_size)
chip_d2.insert_graphic((1600, -3600), os.path.join("assets", "graphics", "CU.gds"), 350)
chip_d2.insert_graphic((1000, -4000), os.path.join("assets", "graphics", "NIST.gds"), 1000, read_layer=10)

##---------------------------- Design 3 ---------------------------------

# Create first chip design
chip_d3 = ChipDesign()
chip_d3.read_conf(os.path.join("designs", "C2024Q1_AusfC.json"))
chip_d3.build()

# Add first chip graphics
chip_d3.insert_text((600, baseline+line_gap*3+3*text_size), "C-2024-A", selected_font, text_size)
chip_d3.insert_text((600, baseline+line_gap*2+2*text_size), "FREQUENCY CONVERTER", selected_font, text_size)
chip_d3.insert_text((600, baseline+line_gap+text_size), f"UNLOADED | W = 3 um", selected_font, text_size)
chip_d3.insert_graphic((1600, -3600), os.path.join("assets", "graphics", "CU.gds"), 350)
chip_d3.insert_graphic((1000, -4000), os.path.join("assets", "graphics", "NIST.gds"), 1000, read_layer=10)

#------------------------- Create Master Design ---------------------

chip_meister = MultiChipDesign(3)

chip_meister.read_conf("Multi_2024Q1.json")
chip_meister.add_design(chip_d1, rotation=90, translation=[0, 5e3])
chip_meister.add_design(chip_d2, rotation=90, translation=[0, 0])
chip_meister.add_design(chip_d3, rotation=90, translation=[0, -5e3])

chip_meister.build()
chip_meister.apply_objects()

chip_meister.write(os.path.join("GDS", "MultiChip_2024Q1.gds"))