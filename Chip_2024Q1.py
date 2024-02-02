from core import *

chip = ChipDesign()

chip.read_conf(os.path.join("designs", "C2024Q1_AusfB.json"))

# chip.add_design(os.path.join("graphics", "nist.gds"), [100, -1])

chip.build()

futura = os.path.join("assets", "futura", "futura medium bt.ttf")
chicago = os.path.join("tests", "Chicago.ttf")

text_size = 125
line_gap = 35
baseline = -4900
chip.custom_text((50, baseline+line_gap*2+2*text_size), "C-2024-A Frequency Converter", futura, text_size)
chip.custom_text((50, baseline+line_gap+text_size), f"Unloaded, W = 3 um", futura, text_size)

chip.write(os.path.join("GDS", "Chip_2024Q1.gds"))