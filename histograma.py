import fastf1
import numpy as np
from matplotlib import pyplot as plt

# Descargar los datos de la sesión
fastf1.Cache.enable_cache('/Users/alejandrogutierrezalvarez/Desktop/F1')
session = fastf1.get_session(2021, 'Bahrain', 'Q')

# Cargar los datos de telemetría de todas las vueltas
laps = session.load_laps(with_telemetry=True)

# Preprocesar los datos de telemetría de todas las vueltas


# Calcular los tiempos en boxes para cada piloto
driver_times = {}
for driver in session.drivers:
    driver_name = driver.full_name
    driver_laps = session.load_laps(with_telemetry=True, driver_name)
    driver_box_times = []
    for lap in driver_laps:
        telemetry = lap['telemetry']
        ts = telemetry['Lap']['Time'][:-1]
        idxs = np.where(telemetry['CarStatus']['m_lERSDeployedThisLap'] == -20.0)[0]
        if len(idxs) >= 2:
            driver_box_times.append(ts[idxs[1]] - ts[idxs[0]])
    driver_times[driver_name] = driver_box_times

# Generar el histograma de tiempos en boxes
fig, ax = plt.subplots()
ax.hist(driver_times.values(), bins=20, label=driver_times.keys())
ax.set_title('Tiempos en boxes')
ax.set_xlabel('Tiempo (s)')
ax.set_ylabel('Frecuencia')
ax.legend()
plt.show()
