import sys
import mpld3
import os
# With these lines:
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QComboBox, QLineEdit, QProgressBar, QDialog, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtCore import Qt
from PyQt5 import uic, QtGui
import pandas as pd
import seaborn as sns
from Listas import años
from Listas import estadisticas_circuitos
from fastf1.core import Laps
from timple.timedelta import strftimedelta
import numpy as np
import fastf1 as ff1
from fastf1 import plotting
import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib import cm
from matplotlib.widgets import Button, RadioButtons, CheckButtons
from matplotlib.animation import FuncAnimation
from plotnine import ggplot, aes, geom_line
import requests
import json
import numpy as np
from matplotlib.collections import LineCollection
from fastf1.plotting import driver_color
mpl.use('Qt5Agg')

from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

class mapaVelocidadThread(QThread):
    resultReady=pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pilotos = []
        self.year = ""
        self.circuito = ""
        
    def setParams(self, pilotos, year, circuito):
        self.pilotos = pilotos
        self.year = year
        self.circuito = circuito

    def run(self):
        if self.circuito is None:
            return

        ff1.Cache.enable_cache('./')
        session = ff1.get_session(int(self.year), self.circuito, 'R')
        weekend = session.event
        session.load()
        lap = session.laps.pick_fastest()

        # Obtenemos datos de telemtria
        x = np.array(lap.telemetry['X'])
        y = np.array(lap.telemetry['Y'])
        color = lap.telemetry['Speed']      # Valor que vamos a utilizar para la gradiente de color

        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)

       
        fig, ax = plt.subplots(sharex=True, sharey=True, figsize=(12, 6.75))
        title = ax.set_title(
            f"Velocidad en la vuelta rápida-"
            f"{lap['Driver']} - {session.event['EventName']} {session.event.year}")


        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.12)
        ax.axis('off')


        ax.plot(x, y, color='black', linestyle='-', linewidth=16, zorder=0)


        colormap = plt.get_cmap('viridis')  
        norm = plt.Normalize(color.min(), color.max())
        lc = LineCollection(segments, cmap=colormap, norm=norm, linestyle='-', linewidth=5)


        lc.set_array(color)

        line = ax.add_collection(lc)


        cbaxes = fig.add_axes([0.25, 0.05, 0.5, 0.05])
        normlegend = mpl.colors.Normalize(vmin=color.min(), vmax=color.max())
        legend = mpl.colorbar.Colorbar(cbaxes, norm=normlegend, cmap=colormap, orientation="horizontal")


        self.resultReady.emit(fig)

class RitmoCarreraThread(QThread):
    resultReady = pyqtSignal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pilotos = []
        self.year = ""
        self.circuito = ""
        
    def setParams(self, pilotos, year, circuito):
        self.pilotos = pilotos
        self.year = year
        self.circuito = circuito
        
    def run(self):
        ff1.Cache.enable_cache('./')
        granPremio = ff1.get_session(int(self.year), self.circuito, 'R')
        granPremio.load()
        laps=granPremio.laps
        laps['LapTimeSeconds'] = laps['LapTime'].dt.total_seconds()
        laps = laps.loc[(laps['PitOutTime'].isnull() & laps['PitInTime'].isnull())]
        fig, ax = plt.subplots()
        ax.set_xlabel('Piloto')
        ax.set_ylabel('Ritmo del piloto en la carrera (s)')
        data=[]
        for p in self.pilotos:
            driver=laps.pick_driver(p)
            data.append(driver['LapTimeSeconds'])
        ax.boxplot(data, labels=self.pilotos, showfliers=False)
        self.resultReady.emit(fig)

class verQualyThread(QThread):
    resultReady = pyqtSignal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pilotos = []
        self.year = ""
        self.circuito = ""
        
    def setParams(self, pilotos, year, circuito):
        self.pilotos = pilotos
        self.year = year
        self.circuito = circuito
        
    def run(self):
        ff1.Cache.enable_cache('./')
        ff1.plotting.setup_mpl(mpl_timedelta_support=True, color_scheme=None, misc_mpl_mods=False)
        quali = ff1.get_session(int(self.year), self.circuito, 'Q')
        quali.load()
        laps = quali.laps
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
            if pd.notna(lap['Team']):  # comprobamos que el valor del equipo no sea NaT
                color = ff1.plotting.team_color(lap['Team'])
                team_colors.append(color)
            else:
                team_colors.append('pink')  # en caso de que lo sea añadimos un color por defecto
        figure = Figure()
        ax = figure.add_subplot()
        ax.barh(fastest_laps.index, fastest_laps['LapTimeDelta'],
             color=team_colors, edgecolor='grey')
        ax.set_yticks(fastest_laps.index)
        ax.set_yticklabels(fastest_laps['Driver'])

        ax.invert_yaxis()

        ax.set_axisbelow(True)
        ax.xaxis.grid(True, linestyle='--', color='black', zorder=-1000)
        lap_time_string = strftimedelta(pole_lap['LapTime'], '%m:%s.%ms')

        ax.set_title(f"{quali.event['EventName']} {quali.event.year} Clasificación\n"
             f"Vuelta Rapida: {lap_time_string} ({pole_lap['Driver']})")
        self.resultReady.emit(figure)    

class infoNeumaticosThread(QThread):
    resultReady = pyqtSignal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pilotos = []
        self.year = ""
        self.circuito = ""
        
    def setParams(self, pilotos, year, circuito):
        self.pilotos = pilotos
        self.year = year
        self.circuito = circuito
        
    def run(self):
        ff1.Cache.enable_cache('./')
        session = ff1.get_session(int(self.year), self.circuito, 'R')
        session.load()
        laps = session.laps
        drivers = session.drivers
        drivers = [session.get_driver(driver)["Abbreviation"] for driver in drivers]
        stints = laps[["Driver", "Stint", "Compound", "LapNumber"]]
        stints = stints.groupby(["Driver", "Stint", "Compound"])
        stints = stints.count().reset_index()
        stints = stints.rename(columns={"LapNumber": "StintLength"})
        fig, ax = plt.subplots(figsize=(5, 10))

        legend_dict = {}  # Creamos un diccionario para mapear colores y compuestos
        for driver in drivers:
            driver_stints = stints.loc[stints["Driver"] == driver]
            previous_stint_end = 0
            for idx, row in driver_stints.iterrows():
                # Añadimos la información del compuesto al diccionario
                legend_dict[row["Compound"]] = ff1.plotting.COMPOUND_COLORS[row["Compound"]]
                plt.barh(
                    y=driver,
                    width=row["StintLength"],
                    left=previous_stint_end,
                    color=ff1.plotting.COMPOUND_COLORS[row["Compound"]],
                    edgecolor="black",
                    fill=True
                )
                previous_stint_end += row["StintLength"]

        # Creamos la leyenda utilizando la información del diccionario
        handles = [plt.Rectangle((0,0),1,1, color=color) for color in legend_dict.values()]
        labels = legend_dict.keys()
        plt.legend(handles, labels, loc='lower right',bbox_to_anchor=(1, 1))

        plt.title("Compuestos utilizados durante la carrera")
        plt.xlabel("Número de vuelta")
        plt.grid(False)
        ax.invert_yaxis()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        self.resultReady.emit(fig)    

class tiempoVueltasThread(QThread):
    resultReady = pyqtSignal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pilotos = []
        self.year = ""
        self.circuito = ""
        
    def setParams(self, pilotos, year, circuito):
        self.pilotos = pilotos
        self.year = year
        self.circuito = circuito
        
    def run(self):
        ff1.Cache.enable_cache('./')
        granPremio = ff1.get_session(int(self.year), self.circuito, 'R')
        granPremio.load()
        laps=granPremio.laps
        fig, ax = plt.subplots()
        ax.set_xlabel("Vuelta")
        ax.set_ylabel("Tiempo")
        ax.set_title("Comparativa de pilotos")
        lines=[]
        for p in self.pilotos:
            driver=laps.pick_driver(p)
            line, =ax.plot(np.array(driver['LapNumber']), np.array(driver['LapTime']), label=p)
            lines.append(line)
        leg=ax.legend(fancybox=True, shadow=True, loc="upper right")
        lined= dict()
        for legline, origline in zip(leg.get_lines(), lines):
            legline.set_picker(5)  # habilitar seleccion en la leyenda.
            origline.set_visible(False)
            legline.set_alpha(0.2)
            lined[legline] = origline
        lines[0].set_visible(True)
        leg.get_lines()[0].set_alpha(1)
        def on_pick(event):
            legline = event.artist
            origline = lined[legline]
            visible = not origline.get_visible()
            origline.set_visible(visible)
            legline.set_alpha(1.0 if visible else 0.2)
            fig.canvas.draw()

        fig.canvas.mpl_connect('pick_event', on_pick)
        self.resultReady.emit(fig)

class telemetriaThread(QThread):
    resultReady = pyqtSignal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pilotos = []
        self.year = ""
        self.circuito = ""
        
    def setParams(self, pilotos, year, circuito):
        self.pilotos = pilotos
        self.year = year
        self.circuito = circuito
        
    def run(self):
        plt.close('all')

        ff1.Cache.enable_cache('./')
        granPremio = ff1.get_session(int(self.year), self.circuito, 'R')
        laps=granPremio.load()
        laps=granPremio.laps
        fig, ax = plt.subplots(3, sharex=True)
        lines=[]
        lines1=[]
        lines2=[]
        for p in self.pilotos:
            driver=laps.pick_driver(p)
			#cargo la vuelta rapida y la telemetria de la misma
            rapida=driver.pick_fastest()
            try:
                telemetry = rapida.get_car_data().add_distance()
            except Exception as e:
                print(f"Error al obtener datos para el piloto {p}: {e}")
                continue			#for x in range(1,laps.LapNumber[-1:]):
                #self.bVueltas.add(x)
			
            line1,=ax[0].plot(np.array(telemetry['Distance']), np.array(telemetry['Speed']), label=p)
            ax[0].set(ylabel='velocidad')
            line2,=ax[1].plot(np.array(telemetry['Distance']), np.array(telemetry['Throttle']), label=p)
            ax[1].set(ylabel='Acelerador')
            line3,=ax[2].plot(np.array(telemetry['Distance']), np.array(telemetry['Brake']), label=p)
            ax[2].set(ylabel='Freno')
            ax[2].set_xlabel('Distancia (metros)')
            lines.append(line1)
            lines1.append(line2)
            lines2.append(line3)

        handles, labels = ax[0].get_legend_handles_labels()
        leg=fig.legend(handles, labels, loc='center right')
        #fig.legend(lines, pilotos, loc='best')
        lined= dict()
        for legline, origline, origline2, origline3 in zip(leg.get_lines(), lines, lines1, lines2):
            legline.set_picker(5)
            origline.set_visible(False)
            origline2.set_visible(False)
            origline3.set_visible(False)
            legline.set_alpha(0.2)
            lined[legline] = [origline, origline2, origline3]
        lines[0].set_visible(True)
        lines1[0].set_visible(True)
        lines2[0].set_visible(True)
        leg.get_lines()[0].set_alpha(1)
        def on_pick(event):
            legline = event.artist
            origline = lined[legline]
            for o in origline:
                visible = not o.get_visible()
                o.set_visible(visible)
                legline.set_alpha(1.0 if visible else 0.2)
                fig.canvas.draw()
        fig.canvas.mpl_connect('pick_event', on_pick)
        self.resultReady.emit(fig)    

class adelantamientosThread(QThread):
    resultReady = pyqtSignal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pilotos = []
        self.year = ""
        self.circuito = ""
        
    def setParams(self, pilotos, year, circuito):
        self.pilotos = pilotos
        self.year = year
        self.circuito = circuito
        
    def run(self):
        ff1.Cache.enable_cache('./')
        session = ff1.get_session(int(self.year), self.circuito, 'R')
        session.load(telemetry=False, weather=False)
        fig, ax = plt.subplots(figsize=(8.0, 4.9))
        for drv in session.drivers:
            drv_laps = session.laps.pick_driver(drv)

            abb = drv_laps['Driver'].iloc[0]


            # Convertir 'LapNumber' y 'Position' en arrays de NumPy 
            lap_numbers = drv_laps['LapNumber'].values
            positions = drv_laps['Position'].values

            ax.plot(lap_numbers, positions, label=abb)

        ax.set_ylim([20.5, 0.5])
        ax.set_yticks([1, 5, 10, 15, 20])
        ax.set_xlabel('Vuelta')
        ax.set_ylabel('Posición')
        ax.legend(bbox_to_anchor=(1.0, 1.02))
        plt.tight_layout()
        self.resultReady.emit(fig)

class marchasVueltaThread(QThread):
    resultReady = pyqtSignal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pilotos = []
        self.year = ""
        self.circuito = ""
        
    def setParams(self, pilotos, year, circuito):
        self.pilotos = pilotos
        self.year = year
        self.circuito = circuito
        
    def run(self):
        ff1.Cache.enable_cache('./')
        session = ff1.get_session(int(self.year), self.circuito, 'R')
        print(self.circuito)
        session.load()
        laps = session.laps
        lap = laps.pick_fastest()
        tel = lap.get_telemetry()

        x = np.array(tel['X'].values)
        y = np.array(tel['Y'].values)

        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        gear = tel['nGear'].to_numpy().astype(float)

        cmap = cm.get_cmap('Paired',8)
        lc_comp = LineCollection(segments, norm=plt.Normalize(1, 9), cmap=cmap)  # Normalizar de 1 a 9
        lc_comp.set_array(gear)
        lc_comp.set_linewidth(4)

        # Creamos la figura y los ejes
        fig = Figure(figsize=(8, 6), dpi=100)
        ax = fig.add_subplot(111)

        # Añadimos LineCollection a los ejes
        ax.add_collection(lc_comp)
        ax.axis('equal')
        ax.tick_params(labelleft=False, left=False, labelbottom=False, bottom=False)

        title = ax.set_title(
            f"Distribución de marchas en la vuelta rápida\n"
            f"{lap['Driver']} - {session.event['EventName']} {session.event.year}")

        # Añadimos la colorbar al plot
        cbar = fig.colorbar(mappable=lc_comp, label="Gear", boundaries=np.arange(0.5, 9.5))
        cbar.set_ticks(np.arange(1, 9))  # Establecer los ticks de 1 a 8
        cbar.set_ticklabels(np.arange(1, 9))  # Establecer las etiquetas de los ticks de 1 a 8

        self.resultReady.emit(fig)

class infoParadasThread(QThread):
    resultReady = pyqtSignal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pilotos = []
        self.year = ""
        self.circuito = ""
        
    def setParams(self, pilotos, year, circuito):
        self.pilotos = pilotos
        self.year = year
        self.circuito = circuito
    def get_round_number(self, year, circuit_name):
        base_url = 'http://ergast.com/api/f1'
        url = f'{base_url}/{year}.json'

        response = requests.get(url)
        data = response.json()

        races = data['MRData']['RaceTable']['Races']
        circuit_round_map = {race['Circuit']['circuitName']: race['round'] for race in races}

        return circuit_round_map.get(circuit_name)
    def run(self):
        base_url = 'http://ergast.com/api/f1'
        year = self.year
        circuit_name = self.circuito
        round_number = self.get_round_number(year, circuit_name)
        url = f'{base_url}/{year}/{round_number}/pitstops.json'

        response = requests.get(url)
        data = response.json()

        pit_stops = data['MRData']['RaceTable']['Races'][0]['PitStops']
        df_pit_stops = pd.DataFrame(pit_stops)
        df_pit_stops['duration'] = df_pit_stops['duration'].astype(float)
        avg_pit_stop_time = df_pit_stops.groupby('driverId')['duration'].mean().reset_index()
        fig, ax = plt.subplots()
        #DESCOMENTAR PARA AÑADIR COLOR, INCOMPATIBLE CON ERGAST
        #ff1.Cache.enable_cache('/Users/alejandrogutierrezalvarez/Desktop/F1')
        #session = ff1.get_session(int(year),1, 'R')
        #ff1.plotting.setup_mpl(mpl_timedelta_support=True, color_scheme=None, misc_mpl_mods=False)
        print(df_pit_stops)
        #color_orden=[]
        #for driver in avg_pit_stop_time.iterrows():
            #color_orden.append(ff1.plotting.team_color(driver[1]['driverId']))
        #avg_pit_stop_time['color']=color_orden        
        #ax.bar(avg_pit_stop_time['driverId'],avg_pit_stop_time['duration'], color=avg_pit_stop_time['color'])
        # Obtener colores de equipo para cada piloto


        ax.bar(avg_pit_stop_time['driverId'],avg_pit_stop_time['duration'])

        ax.set_xticklabels(avg_pit_stop_time['driverId'], rotation=45, ha='right')

        # Etiquetas y titulo
        ax.set_xlabel('Piloto')
        ax.set_ylabel('Tiempo medio pit stop (s)')
        ax.set_title('Tiempo medio pit stop por Drivepilotor')
        fig.tight_layout()
        self.resultReady.emit(fig)

class Circuitos(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('Interfaces/circuitos.ui', self)
        self.listaPilotos=[]
        self.circuitos={}
        self.bAnio.addItems(años)
        self.bAnio.activated.connect(self.addCircuitos)
        self.bAnio.setPlaceholderText("Seleccionar")
        self.bAnio.setCurrentIndex(-1)
        self.bCircuito.activated.connect(self.addEstadisticas)
        self.bCircuito.setPlaceholderText("Seleccionar")
        self.bEstadistica.activated.connect(self.addPilotos)
        self.bEstadistica.setPlaceholderText("Seleccionar")
        self.bEstadistica.currentIndexChanged.connect(self.actualizarTexto)
        self.bBuscar.pressed.connect(self.redirecciona)
        self.bPdf.setIcon(QtGui.QIcon('Resources/pdf.png'))
        self.bPdf.pressed.connect(self.ExportarPDF)
        ff1.plotting.setup_mpl(misc_mpl_mods=False)

    def actualizarTexto(self):
        if(self.bEstadistica.currentText()=="Tiempo por vuelta"):
            self.textEdit.setPlainText("Tiempo por vuelta: Muestra el tiempo que le ha llevado a cada piloto completar una vuelta")
        if(self.bEstadistica.currentText()=="Telemetria"):
            self.textEdit.setPlainText("Telemetria: Muestra distintos datos de la telemetría de los pilotos, cuanto pisan el acelerador, cuanto pisan el freno y la velocidad")
        if(self.bEstadistica.currentText()=="Adelantamientos"):
            self.textEdit.setPlainText("Adelantamientos: Permite ver como han ido evolucionando las posiciones de los pilotos en cada vuelta")
        if(self.bEstadistica.currentText()=="Marchas vuelta"):
            self.textEdit.setPlainText("Marchas vuelta: Dibuja el mapa del circuito seleccionado y lo divide en tramos en función de la marcha que tuviera engranada el piloto en cada uno")
        if(self.bEstadistica.currentText()=="Ver Qualy"):
            self.textEdit.setPlainText("Ver Qualy: Muestra los resultados de la Qualy para el año y circuito seleccionados")
        if(self.bEstadistica.currentText()=="Tiempo medio pit stop"):
            self.textEdit.setPlainText("Tiempo medio pit stop: Muestra el tiempo medio que pasan los pilotos en boxes")
        if(self.bEstadistica.currentText()=="Mapa de velocidad"):
            self.textEdit.setPlainText("Mapa de velocidad: Dibuja el mapa del circuito seleccionado y lo divide en tramos en función de la velocidad que tuviera el piloto en ese momento")
        if(self.bEstadistica.currentText()=="Información de neumaticos"):
            self.textEdit.setPlainText("Información de neumáticos: Muestra los diferentes compuestos de neumático que ha usado un piloto durante la carrera")
        if(self.bEstadistica.currentText()=="Ritmo de carrera"):
            self.textEdit.setPlainText("Ritmo de carrera: Muestra en forma de gráfico de cajas el ritmo que han tenido los pilotos durante una carrera")
        self.textEdit.setStyleSheet("font-size: 18pt; font-weight: bold;")

    def ExportarPDF(self):
        file_path = './Figura.pdf'
        
        # Verificar si el archivo ya existe
        file_exists = os.path.exists(file_path)

        # Mostrar un diálogo de confirmación
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText("¿Desea exportar la figura como PDF?")
        msg.setWindowTitle("Confirmar exportación")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)


        msg.setInformativeText("Se creará un nuevo archivo Figura.pdf. ¿Desea continuar?")

        result = msg.exec_()

        if result == QMessageBox.Yes:
            # Si se confirma la exportación, verificar si ya existe un archivo con el mismo nombre
            if file_exists:
                # Obtener un nombre de archivo único incrementando el número
                base_name, ext = os.path.splitext(file_path)
                index = 1
                new_file_path = f'{base_name}{index}{ext}'
                while os.path.exists(new_file_path):
                    index += 1
                    new_file_path = f'{base_name}{index}{ext}'
                file_path = new_file_path

            # Guardar la figura en el archivo PDF
            self.plotter.itemAt(0).widget().figure.savefig(file_path)
            QMessageBox.information(self, "Éxito", f"Archivo PDF guardado en {file_path}")
        else:
            QMessageBox.information(self, "Cancelado", "Exportación de PDF cancelada.")
    
    def addCircuitos(self):
        self.bCircuito.clear()
        self.bEstadistica.clear()
        self.bBuscar.setEnabled(False)
        year=self.bAnio.currentText()
        circuits={}
        if len(circuits)==0:
        	r = requests.get("https://ergast.com/api/f1/"+str(year)+"/circuits.json")
        	r = json.loads(r.text)
        	circuits = r["MRData"]["CircuitTable"]["Circuits"]
        for s in circuits:
            self.bCircuito.addItem(s['circuitName'])
            self.circuitos[s['circuitName']]=s['circuitId']

        self.bCircuito.setCurrentIndex(-1)

    def addEstadisticas(self):
        self.bBuscar.setEnabled(False)
        self.bEstadistica.clear()
        for e in estadisticas_circuitos:
            self.bEstadistica.addItem(e)
        self.bEstadistica.setCurrentIndex(-1)

    def addPilotos(self):
        self.listaPilotos.clear()
        year=self.bAnio.currentText()
        circuito=self.circuitos[self.bCircuito.currentText()]
        drivers={}
        if(self.bCircuito.currentText()!=""):
            if len(drivers)==0:
                r = requests.get("https://ergast.com/api/f1/"+str(year)+"/circuits/"+circuito+"/drivers.json")
                r = json.loads(r.text)
                drivers = r["MRData"]["DriverTable"]["Drivers"]
            for d in drivers:
                self.listaPilotos.append(d['code'])
        self.bBuscar.setEnabled(True)

    def redirecciona(self):
        if(self.bEstadistica.currentText()=="Tiempo por vuelta"):
            pilotos = self.listaPilotos
            year = self.bAnio.currentText()
            circuito = self.circuitos[self.bCircuito.currentText()]
            
            # Paso 0: Crear una instancia de QDialog para mostrar la barra de progreso
            progress_dialog = QDialog(self)
            progress_dialog.setWindowTitle("Cargando...")
            progress_dialog.setWindowModality(Qt.WindowModal)

            # Crear una barra de progreso
            progress_bar = QProgressBar(progress_dialog)
            progress_bar.setRange(0, 0)  # Configurar la barra de progreso indeterminada
            progress_bar.setAlignment(Qt.AlignCenter)

            # Layout para el diálogo de progreso
            layout = QVBoxLayout(progress_dialog)
            layout.addWidget(progress_bar)

             # Paso 1: Crear una instancia de tiempoVueltasThread
            self.tiempoVueltas_thread = tiempoVueltasThread()
    
            # Paso 2: Configurar los parámetros necesarios para tiempoVueltasThread
            self.tiempoVueltas_thread.setParams(pilotos, year, circuito)
    
            # Paso 3: Conectar la señal resultReady del hilo a una ranura en la clase principal Circuitos
            self.tiempoVueltas_thread.resultReady.connect(self.mostrar_grafico)
            
            self.tiempoVueltas_thread.finished.connect(progress_dialog.accept)

            # Paso 4: Iniciar el hilo tiempoVueltasThread
            self.tiempoVueltas_thread.start()
            # Mostrar el diálogo de progreso
            progress_dialog.exec_()
        if(self.bEstadistica.currentText()=="Telemetria"):
            pilotos = self.listaPilotos
            year = self.bAnio.currentText()
            circuito = self.circuitos[self.bCircuito.currentText()]
            
            # Paso 0: Crear una instancia de QDialog para mostrar la barra de progreso
            progress_dialog = QDialog(self)
            progress_dialog.setWindowTitle("Cargando...")
            progress_dialog.setWindowModality(Qt.WindowModal)

            # Crear una barra de progreso
            progress_bar = QProgressBar(progress_dialog)
            progress_bar.setRange(0, 0)  # Configurar la barra de progreso indeterminada
            progress_bar.setAlignment(Qt.AlignCenter)

            # Layout para el diálogo de progreso
            layout = QVBoxLayout(progress_dialog)
            layout.addWidget(progress_bar)

             # Paso 1: Crear una instancia de telemetriaThread
            self.telemetria_thread = telemetriaThread()
    
            # Paso 2: Configurar los parámetros necesarios para telemetriaThread
            self.telemetria_thread.setParams(pilotos, year, circuito)
    
            # Paso 3: Conectar la señal resultReady del hilo a una ranura en la clase principal Circuitos
            self.telemetria_thread.resultReady.connect(self.mostrar_grafico)
            
            self.telemetria_thread.finished.connect(progress_dialog.accept)

            # Paso 4: Iniciar el hilo telemetriaThread
            self.telemetria_thread.start()
            # Mostrar el diálogo de progreso
            progress_dialog.exec_()
        if(self.bEstadistica.currentText()=="Adelantamientos"):
            pilotos = self.listaPilotos
            year = self.bAnio.currentText()
            circuito = self.circuitos[self.bCircuito.currentText()]
            
            # Paso 0: Crear una instancia de QDialog para mostrar la barra de progreso
            progress_dialog = QDialog(self)
            progress_dialog.setWindowTitle("Cargando...")
            progress_dialog.setWindowModality(Qt.WindowModal)

            # Crear una barra de progreso
            progress_bar = QProgressBar(progress_dialog)
            progress_bar.setRange(0, 0)  # Configurar la barra de progreso indeterminada
            progress_bar.setAlignment(Qt.AlignCenter)

            # Layout para el diálogo de progreso
            layout = QVBoxLayout(progress_dialog)
            layout.addWidget(progress_bar)

             # Paso 1: Crear una instancia de adelantamientosThread
            self.adelantamientos_thread = adelantamientosThread()
    
            # Paso 2: Configurar los parámetros necesarios para adelantamientosThread
            self.adelantamientos_thread.setParams(pilotos, year, circuito)
    
            # Paso 3: Conectar la señal resultReady del hilo a una ranura en la clase principal Circuitos
            self.adelantamientos_thread.resultReady.connect(self.mostrar_grafico)
            
            self.adelantamientos_thread.finished.connect(progress_dialog.accept)

            # Paso 4: Iniciar el hilo RitmoCarreraThread
            self.adelantamientos_thread.start()
            # Mostrar el diálogo de progreso
            progress_dialog.exec_()
        if(self.bEstadistica.currentText()=="Marchas vuelta"):
            pilotos = self.listaPilotos
            year = self.bAnio.currentText()
            circuito = self.circuitos[self.bCircuito.currentText()]
            
            # Paso 0: Crear una instancia de QDialog para mostrar la barra de progreso
            progress_dialog = QDialog(self)
            progress_dialog.setWindowTitle("Cargando...")
            progress_dialog.setWindowModality(Qt.WindowModal)

            # Crear una barra de progreso
            progress_bar = QProgressBar(progress_dialog)
            progress_bar.setRange(0, 0)  # Configurar la barra de progreso indeterminada
            progress_bar.setAlignment(Qt.AlignCenter)

            # Layout para el diálogo de progreso
            layout = QVBoxLayout(progress_dialog)
            layout.addWidget(progress_bar)

             # Paso 1: Crear una instancia de marchasVueltaThread
            self.marchasVuelta_thread = marchasVueltaThread()
    
            # Paso 2: Configurar los parámetros necesarios para marchasVueltaThread
            self.marchasVuelta_thread.setParams(pilotos, year, circuito)
    
            # Paso 3: Conectar la señal resultReady del hilo a una ranura en la clase principal Circuitos
            self.marchasVuelta_thread.resultReady.connect(self.mostrar_grafico)
            
            self.marchasVuelta_thread.finished.connect(progress_dialog.accept)

            # Paso 4: Iniciar el hilo marchasVueltaThread
            self.marchasVuelta_thread.start()
            # Mostrar el diálogo de progreso
            progress_dialog.exec_()
        if(self.bEstadistica.currentText()=="Ver Qualy"):
            pilotos = self.listaPilotos
            year = self.bAnio.currentText()
            circuito = self.circuitos[self.bCircuito.currentText()]
            
            # Paso 0: Crear una instancia de QDialog para mostrar la barra de progreso
            progress_dialog = QDialog(self)
            progress_dialog.setWindowTitle("Cargando...")
            progress_dialog.setWindowModality(Qt.WindowModal)

            # Crear una barra de progreso
            progress_bar = QProgressBar(progress_dialog)
            progress_bar.setRange(0, 0)  # Configurar la barra de progreso indeterminada
            progress_bar.setAlignment(Qt.AlignCenter)

            # Layout para el diálogo de progreso
            layout = QVBoxLayout(progress_dialog)
            layout.addWidget(progress_bar)

             # Paso 1: Crear una instancia de verQualyThread
            self.ver_qualy_thread = verQualyThread()
    
            # Paso 2: Configurar los parámetros necesarios para verQualyThread
            self.ver_qualy_thread.setParams(pilotos, year, circuito)
    
            # Paso 3: Conectar la señal resultReady del hilo a una ranura en la clase principal Circuitos
            self.ver_qualy_thread.resultReady.connect(self.mostrar_grafico)
            
            self.ver_qualy_thread.finished.connect(progress_dialog.accept)

            # Paso 4: Iniciar el hilo verQualyThread
            self.ver_qualy_thread.start()
            # Mostrar el diálogo de progreso
            progress_dialog.exec_()
        if(self.bEstadistica.currentText()=="Tiempo medio pit stop"):
            pilotos = self.listaPilotos
            year = self.bAnio.currentText()
            circuito = self.circuitos[self.bCircuito.currentText()]
            
            # Paso 0: Crear una instancia de QDialog para mostrar la barra de progreso
            progress_dialog = QDialog(self)
            progress_dialog.setWindowTitle("Cargando...")
            progress_dialog.setWindowModality(Qt.WindowModal)

            # Crear una barra de progreso
            progress_bar = QProgressBar(progress_dialog)
            progress_bar.setRange(0, 0)  # Configurar la barra de progreso indeterminada
            progress_bar.setAlignment(Qt.AlignCenter)

            # Layout para el diálogo de progreso
            layout = QVBoxLayout(progress_dialog)
            layout.addWidget(progress_bar)

             # Paso 1: Crear una instancia de infoParadasThread
            self.infoParadas_thread = infoParadasThread()
    
            # Paso 2: Configurar los parámetros necesarios para infoParadasThread
            self.infoParadas_thread.setParams(pilotos, year, circuito)
    
            # Paso 3: Conectar la señal resultReady del hilo a una ranura en la clase principal Circuitos
            self.infoParadas_thread.resultReady.connect(self.mostrar_grafico)
            
            self.infoParadas_thread.finished.connect(progress_dialog.accept)

            # Paso 4: Iniciar el hilo infoParadasThread
            self.infoParadas_thread.start()
            # Mostrar el diálogo de progreso
            progress_dialog.exec_()
        if(self.bEstadistica.currentText()=="Mapa de velocidad"):
            pilotos = self.listaPilotos
            year = self.bAnio.currentText()
            circuito = self.circuitos[self.bCircuito.currentText()]
            
            # Paso 0: Crear una instancia de QDialog para mostrar la barra de progreso
            progress_dialog = QDialog(self)
            progress_dialog.setWindowTitle("Cargando...")
            progress_dialog.setWindowModality(Qt.WindowModal)

            # Crear una barra de progreso
            progress_bar = QProgressBar(progress_dialog)
            progress_bar.setRange(0, 0)  # Configurar la barra de progreso indeterminada
            progress_bar.setAlignment(Qt.AlignCenter)

            # Layout para el diálogo de progreso
            layout = QVBoxLayout(progress_dialog)
            layout.addWidget(progress_bar)

             # Paso 1: Crear una instancia de mapaVelocidadThread
            self.mapa_velocidad_thread = mapaVelocidadThread()
    
            # Paso 2: Configurar los parámetros necesarios para mapaVelocidadThread
            self.mapa_velocidad_thread.setParams(pilotos, year, circuito)
    
            # Paso 3: Conectar la señal resultReady del hilo RitmoCarreraThread a una ranura en la clase principal Circuitos
            self.mapa_velocidad_thread.resultReady.connect(self.mostrar_grafico)
            
            self.mapa_velocidad_thread.finished.connect(progress_dialog.accept)

            # Paso 4: Iniciar el hilo mapaVelocidadThread
            self.mapa_velocidad_thread.start()
            # Mostrar el diálogo de progreso
            progress_dialog.exec_()
        if(self.bEstadistica.currentText()=="Información de neumaticos"):
            pilotos = self.listaPilotos
            year = self.bAnio.currentText()
            circuito = self.circuitos[self.bCircuito.currentText()]
            
            # Paso 0: Crear una instancia de QDialog para mostrar la barra de progreso
            progress_dialog = QDialog(self)
            progress_dialog.setWindowTitle("Cargando...")
            progress_dialog.setWindowModality(Qt.WindowModal)

            # Crear una barra de progreso
            progress_bar = QProgressBar(progress_dialog)
            progress_bar.setRange(0, 0)  # Configurar la barra de progreso indeterminada
            progress_bar.setAlignment(Qt.AlignCenter)

            # Layout para el diálogo de progreso
            layout = QVBoxLayout(progress_dialog)
            layout.addWidget(progress_bar)

             # Paso 1: Crear una instancia de infoNeumaticosThread
            self.ver_neumaticos_thread = infoNeumaticosThread()
    
            # Paso 2: Configurar los parámetros necesarios para infoNeumaticosThread
            self.ver_neumaticos_thread.setParams(pilotos, year, circuito)
    
            # Paso 3: Conectar la señal resultReady del hilo a una ranura en la clase principal Circuitos
            self.ver_neumaticos_thread.resultReady.connect(self.mostrar_grafico)
            
            self.ver_neumaticos_thread.finished.connect(progress_dialog.accept)

            # Paso 4: Iniciar el hilo infoNeumaticosThread
            self.ver_neumaticos_thread.start()
            # Mostrar el diálogo de progreso
            progress_dialog.exec_()
        if(self.bEstadistica.currentText()=="Ritmo de carrera"):
            pilotos = self.listaPilotos
            year = self.bAnio.currentText()
            circuito = self.circuitos[self.bCircuito.currentText()]
            
            # Paso 0: Crear una instancia de QDialog para mostrar la barra de progreso
            progress_dialog = QDialog(self)
            progress_dialog.setWindowTitle("Cargando...")
            progress_dialog.setWindowModality(Qt.WindowModal)

            # Crear una barra de progreso
            progress_bar = QProgressBar(progress_dialog)
            progress_bar.setRange(0, 0)  # Configurar la barra de progreso indeterminada
            progress_bar.setAlignment(Qt.AlignCenter)

            # Layout para el diálogo de progreso
            layout = QVBoxLayout(progress_dialog)
            layout.addWidget(progress_bar)

             # Paso 1: Crear una instancia de RitmoCarreraThread
            self.ritmo_carrera_thread = RitmoCarreraThread()
    
            # Paso 2: Configurar los parámetros necesarios para RitmoCarreraThread
            self.ritmo_carrera_thread.setParams(pilotos, year, circuito)
    
            # Paso 3: Conectar la señal resultReady del hilo RitmoCarreraThread a una ranura en la clase principal Circuitos
            self.ritmo_carrera_thread.resultReady.connect(self.mostrar_grafico)
            
            self.ritmo_carrera_thread.finished.connect(progress_dialog.accept)

            # Paso 4: Iniciar el hilo RitmoCarreraThread
            self.ritmo_carrera_thread.start()
            # Mostrar el diálogo de progreso
            progress_dialog.exec_()

    def mostrar_grafico(self, fig):
        # Mostrar el gráfico en un canvas de Matplotlib
        self.clearLayout(self.plotter)
        self.plotter.addWidget(FigureCanvas(fig))
        self.bBuscar.setEnabled(True)

    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()



if __name__ == '__main__':
    app=QApplication(sys.argv)
    myApp=Circuitos()
    myApp.show()
    try:
        sys.exit(app.exec())
    except SystemExit:
        print('Cerrando ventana...')
