from core import *

chip = ChipDesign()

chip.read_conf(os.path.join("designs", "C2024Q1.json"))

chip.build()

chip.write(os.path.join("GDS", "Chip_2024Q1.gds"))