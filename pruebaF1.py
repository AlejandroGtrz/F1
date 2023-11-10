import fastf1 as ff1
from fastf1 import plotting
import pandas as pd
from matplotlib import pyplot as plt
from timple.timedelta import strftimedelta
from fastf1.core import Laps
from matplotlib.collections import LineCollection
from matplotlib import cm

import numpy as np

plotting.setup_mpl()



def cargarGP(gp, año):
    ff1.Cache.enable_cache('/Users/alejandrogutierrezalvarez/Desktop/F1')
    granPremio = ff1.get_session(año, gp, 'R')
    laps=granPremio.load_laps()
    return pd.unique(laps['Driver'])

def compararPilotos(gp, año, pilotos):
    ff1.Cache.enable_cache('/Users/alejandrogutierrezalvarez/Desktop/F1')
    granPremio = ff1.get_session(año, gp, 'R')
    laps=granPremio.load_laps()
    fig, ax = plt.subplots()
    ax.set_xlabel("Vuelta")
    ax.set_ylabel("Tiempo")
    ax.set_title("Comparativa de pilotos")
    for p in pilotos:
        piloto=laps.pick_driver(p)
        ax.plot(piloto['LapNumber'], piloto['LapTime'], label=p)
    ax.legend(loc="upper center")
    plt.show()

def vueltasRapidas(gp, año):
    ff1.Cache.enable_cache('/Users/alejandrogutierrezalvarez/Desktop/F1')
    granPremio = ff1.get_session(año, gp, 'Q')
    vueltaRapida=granPremio.load_laps().pick_fastest()
    return vueltaRapida['LapTime'], vueltaRapida['Driver']

def resultadosQualy(gp, año):
    ff1.Cache.enable_cache('/Users/alejandrogutierrezalvarez/Desktop/F1')
    ff1.plotting.setup_mpl(mpl_timedelta_support=True, color_scheme=None, misc_mpl_mods=False)
    quali = ff1.get_session(año, gp, 'Q')
    laps = quali.load_laps()
    drivers = pd.unique(laps['Driver'])
    list_fastest_laps = list()
    for drv in drivers:
        drvs_fastest_lap = laps.pick_driver(drv).pick_fastest()
        list_fastest_laps.append(drvs_fastest_lap)
    fastest_laps = Laps(list_fastest_laps).sort_values(by='LapTime').reset_index(drop=True)
    pole_lap = fastest_laps.pick_fastest()
    fastest_laps['LapTimeDelta'] = fastest_laps['LapTime'] - pole_lap['LapTime']
    team_colors = list()
    for index, lap in fastest_laps.iterlaps():
        color = ff1.plotting.team_color(lap['Team'])
        team_colors.append(color)
    fig, ax = plt.subplots()
    ax.barh(fastest_laps.index, fastest_laps['LapTimeDelta'],
        color=team_colors, edgecolor='grey')
    ax.set_yticks(fastest_laps.index)
    ax.set_yticklabels(fastest_laps['Driver'])

    ax.invert_yaxis()

    ax.set_axisbelow(True)
    ax.xaxis.grid(True, linestyle='--', color='black', zorder=-1000)
    lap_time_string = strftimedelta(pole_lap['LapTime'], '%m:%s.%ms')

    plt.suptitle(f"{quali.weekend.name} {quali.weekend.year} Clasificación\n"
             f"Vuelta Rapida: {lap_time_string} ({pole_lap['Driver']})")

    plt.show()

def marchasVuelta(gp, año):
    ff1.Cache.enable_cache('/Users/alejandrogutierrezalvarez/Desktop/F1')
    session = ff1.get_session(año, gp, 'Q')
    laps = session.load_laps(with_telemetry=True)
    lap = laps.pick_fastest()
    tel = lap.get_telemetry()
    # sphinx_gallery_defer_figures

    ##############################################################################
    # Prepare the data for plotting by converting it to the appropriate numpy
    # data types

    x = np.array(tel['X'].values)
    y = np.array(tel['Y'].values)

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    gear = tel['nGear'].to_numpy().astype(float)
    # sphinx_gallery_defer_figures

    ##############################################################################
    # Create a line collection. Set a segmented colormap and normalize the plot
    # to full integer values of the colormap

    cmap = cm.get_cmap('Paired')
    lc_comp = LineCollection(segments, norm=plt.Normalize(1, cmap.N+1), cmap=cmap)
    lc_comp.set_array(gear)
    lc_comp.set_linewidth(4)
    # sphinx_gallery_defer_figures

    ##############################################################################
    # Create the plot

    plt.gca().add_collection(lc_comp)
    plt.axis('equal')
    plt.tick_params(labelleft=False, left=False, labelbottom=False, bottom=False)

    title = plt.suptitle(
        f"Fastest Lap Gear Shift Visualization\n"
        f"{lap['Driver']} - {session.weekend.name} {session.weekend.year}"
    )
    # sphinx_gallery_defer_figures


    ##############################################################################
    # Add a colorbar to the plot. Shift the colorbar ticks by +0.5 so that they
    # are centered for each color segment.

    cbar = plt.colorbar(mappable=lc_comp, label="Gear", boundaries=np.arange(1, 10))
    cbar.set_ticks(np.arange(1.5, 9.5))
    cbar.set_ticklabels(np.arange(1, 9))


    plt.show()

def desgloseTelemetria(gp, año, piloto):
    ff1.Cache.enable_cache('/Users/alejandrogutierrezalvarez/Desktop/F1')
    granPremio = ff1.get_session(año, gp, 'R')
    laps=granPremio.load_laps(with_telemetry=True)
    driver=laps.pick_driver(piloto)
    rapida=driver.pick_fastest()
    telemetry = rapida.get_car_data().add_distance()
    fig, ax = plt.subplots(3)
    fig.suptitle("Telemetría vuelta rapida")

    ax[0].plot(telemetry['Distance'], telemetry['Speed'], label=piloto)
    ax[0].set(ylabel='velocidad')
    ax[0].legend(loc="lower right")
    ax[1].plot(telemetry['Distance'], telemetry['Throttle'], label=piloto)
    ax[1].set(ylabel='Acelerador')
    ax[2].plot(telemetry['Distance'], telemetry['Brake'], label=piloto)
    ax[2].set(ylabel='Freno')
    for a in ax.flat:
        a.label_outer()
        
    plt.show()


        




