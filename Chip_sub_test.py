from core import *

# Fiducial corner numbering:
# 1 = top left
# 2 = bottom left
# 3 = bottom right
# 4 = top right

chip = ChipDesign()

# chip.read_conf(os.path.join("designs", "MC-2024Q1-D1-AusfA.json"))
chip.read_conf(os.path.join("designs", "MC-2024Q1V-D1-AusfA.json"))

chip.build()

futura = os.path.join("assets", "futura", "futura medium bt.ttf")
chicago = os.path.join("tests", "Chicago.ttf")

selected_font = futura

text_size = 125
line_gap = 35
baseline = 3500
justify_line = -1600

chip.insert_text((justify_line, baseline+line_gap*3+3*text_size), "C-2024-A", selected_font, text_size)
chip.insert_text((justify_line, baseline+line_gap*2+2*text_size), "FREQUENCY CONVERTER", selected_font, text_size)
chip.insert_text((justify_line, baseline+line_gap+text_size), f"UNLOADED | W = 3 um", selected_font, text_size)

chip.insert_graphic((700, -4800), os.path.join("assets", "graphics", "CU.gds"), 350)
chip.insert_graphic((-1600, -4800), os.path.join("assets", "graphics", "NIST.gds"), 1000, read_layer=10)

chip.apply_objects()
chip.write(os.path.join("GDS", "test.gds"))