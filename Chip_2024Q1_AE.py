from core import *

# Read fonts
futura = os.path.join("assets", "futura", "futura medium bt.ttf")
chicago = os.path.join("tests", "Chicago.ttf")
selected_font = futura

# Select graphics positions
text_size = 125
line_gap = 35
baseline = -4900

## ------------------------ Create chip-A ---------------------

model_str = "A"
tlin_width = 2.5

# Create chip object
chip_a = ChipDesign()

# Read parameters - overwrite width
chip_a.read_conf(os.path.join("designs", "C2024Q1_AusfB.json"))
chip_a.tlin['Wcenter_um'] = tlin_width

# Build chip
chip_a.build()

# Add graphics
chip_a.insert_text((600, baseline+line_gap*3+3*text_size), f"C-2024Q1-{model_str}", selected_font, text_size)
chip_a.insert_text((600, baseline+line_gap*2+2*text_size), "FREQUENCY CONVERTER", selected_font, text_size)
chip_a.insert_text((600, baseline+line_gap+text_size), f"UNLOADED | W = {tlin_width} um", selected_font, text_size)

chip_a.insert_graphic((1600, -3600), os.path.join("assets", "graphics", "CU.gds"), 350)
chip_a.insert_graphic((1000, -4000), os.path.join("assets", "graphics", "NIST.gds"), 1000, read_layer=10)

chip_a.write(os.path.join("GDS", f"chip_2024Q1_{model_str}.gds"))

## ------------------------ Create chip-B ---------------------

model_str = "B"
tlin_width = 3

# Create chip object
chip_b = ChipDesign()

# Read parameters - overwrite width
chip_b.read_conf(os.path.join("designs", "C2024Q1_AusfB.json"))
chip_b.tlin['Wcenter_um'] = tlin_width

# Build chip
chip_b.build()

# Add graphics
chip_b.insert_text((600, baseline+line_gap*3+3*text_size), f"C-2024Q1-{model_str}", selected_font, text_size)
chip_b.insert_text((600, baseline+line_gap*2+2*text_size), "FREQUENCY CONVERTER", selected_font, text_size)
chip_b.insert_text((600, baseline+line_gap+text_size), f"UNLOADED | W = {tlin_width} um", selected_font, text_size)

chip_b.insert_graphic((1600, -3600), os.path.join("assets", "graphics", "CU.gds"), 350)
chip_b.insert_graphic((1000, -4000), os.path.join("assets", "graphics", "NIST.gds"), 1000, read_layer=10)

chip_b.write(os.path.join("GDS", f"chip_2024Q1_{model_str}.gds"))

## ------------------------ Create chip-C ---------------------

model_str = "C"
tlin_width = 3.3

# Create chip object
chip_c = ChipDesign()

# Read parameters - overwrite width
chip_c.read_conf(os.path.join("designs", "C2024Q1_AusfB.json"))
chip_c.tlin['Wcenter_um'] = tlin_width

# Build chip
chip_c.build()

# Add graphics
chip_c.insert_text((600, baseline+line_gap*3+3*text_size), f"C-2024Q1-{model_str}", selected_font, text_size)
chip_c.insert_text((600, baseline+line_gap*2+2*text_size), "FREQUENCY CONVERTER", selected_font, text_size)
chip_c.insert_text((600, baseline+line_gap+text_size), f"UNLOADED | W = {tlin_width} um", selected_font, text_size)

chip_c.insert_graphic((1600, -3600), os.path.join("assets", "graphics", "CU.gds"), 350)
chip_c.insert_graphic((1000, -4000), os.path.join("assets", "graphics", "NIST.gds"), 1000, read_layer=10)

chip_c.write(os.path.join("GDS", f"chip_2024Q1_{model_str}.gds"))

## ------------------------ Create chip-D ---------------------

model_str = "D"
tlin_width = 3.7

# Create chip object
chip_d = ChipDesign()

# Read parameters - overwrite width
chip_d.read_conf(os.path.join("designs", "C2024Q1_AusfB.json"))
chip_d.tlin['Wcenter_um'] = tlin_width

# Build chip
chip_d.build()

# Add graphics
chip_d.insert_text((600, baseline+line_gap*3+3*text_size), f"C-2024Q1-{model_str}", selected_font, text_size)
chip_d.insert_text((600, baseline+line_gap*2+2*text_size), "FREQUENCY CONVERTER", selected_font, text_size)
chip_d.insert_text((600, baseline+line_gap+text_size), f"UNLOADED | W = {tlin_width} um", selected_font, text_size)

chip_d.insert_graphic((1600, -3600), os.path.join("assets", "graphics", "CU.gds"), 350)
chip_d.insert_graphic((1000, -4000), os.path.join("assets", "graphics", "NIST.gds"), 1000, read_layer=10)

chip_d.write(os.path.join("GDS", f"chip_2024Q1_{model_str}.gds"))

## ------------------------ Create chip-E ---------------------

model_str = "E"
tlin_width = 4.4

# Create chip object
chip_e = ChipDesign()

# Read parameters - overwrite width
chip_e.read_conf(os.path.join("designs", "C2024Q1_AusfB.json"))
chip_e.tlin['Wcenter_um'] = tlin_width

# Build chip
chip_e.build()

# Add graphics
chip_e.insert_text((600, baseline+line_gap*3+3*text_size), f"C-2024Q1-{model_str}", selected_font, text_size)
chip_e.insert_text((600, baseline+line_gap*2+2*text_size), "FREQUENCY CONVERTER", selected_font, text_size)
chip_e.insert_text((600, baseline+line_gap+text_size), f"UNLOADED | W = {tlin_width} um", selected_font, text_size)

chip_e.insert_graphic((1600, -3600), os.path.join("assets", "graphics", "CU.gds"), 350)
chip_e.insert_graphic((1000, -4000), os.path.join("assets", "graphics", "NIST.gds"), 1000, read_layer=10)

chip_e.write(os.path.join("GDS", f"chip_2024Q1_{model_str}.gds"))