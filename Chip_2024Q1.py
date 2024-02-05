from core import *

chip = ChipDesign()

chip.read_conf(os.path.join("designs", "C2024Q1_AusfB.json"))

# chip.add_design(os.path.join("graphics", "nist.gds"), [100, -1])

chip.build()

futura = os.path.join("assets", "futura", "futura medium bt.ttf")
chicago = os.path.join("tests", "Chicago.ttf")

selected_font = futura

text_size = 125
line_gap = 35
baseline = -4900

chip.insert_text((600, baseline+line_gap*3+3*text_size), "C-2024-A", selected_font, text_size)
chip.insert_text((600, baseline+line_gap*2+2*text_size), "FREQUENCY CONVERTER", selected_font, text_size)
chip.insert_text((600, baseline+line_gap+text_size), f"UNLOADED | W = 3 um", selected_font, text_size)

chip.insert_graphic((1600, -3600), os.path.join("assets", "graphics", "CU.gds"), 350)
chip.insert_graphic((1000, -4000), os.path.join("assets", "graphics", "NIST.gds"), 1000, read_layer=10)

chip.write(os.path.join("GDS", "Chip_2024Q1.gds"))