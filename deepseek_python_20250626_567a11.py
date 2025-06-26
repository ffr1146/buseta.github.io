from bus_eta import get_bus_eta

etas = get_bus_eta('104', '001034')
for eta in etas:
    print(eta['eta'], eta['rmk_en'])