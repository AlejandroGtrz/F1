import fastf1 as ff1
import fastf1.plotting
import matplotlib.pyplot as plt


fastf1.plotting.setup_mpl(misc_mpl_mods=False)
# Obtener los datos de la carrera
session = ff1.get_session(2021, 1, 'Q')
session.load()
drivers = session.drivers
driver_colors = {}
print(drivers)