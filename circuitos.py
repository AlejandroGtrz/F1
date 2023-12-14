import sys
import mpld3
# With these lines:
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QComboBox, QLineEdit, QProgressBar, QDialog
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
        data=[]
        for p in self.pilotos:
            driver=laps.pick_driver(p)
            data.append(driver['LapTimeSeconds'])
        ax.boxplot(data, labels=self.pilotos, showfliers=False)
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

    def ExportarPDF(self):
        self.plotter.itemAt(0).widget().figure.savefig('./Figura.pdf')
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

    def mapaVelocidad(self):
        year = self.bAnio.currentText()
        circuito = self.bCircuito.currentText()  # Use .get() to handle missing key
        if circuito is None:
            # Handle the case where the circuit is missing
            # You can display an error message or handle it as needed
            return

        ff1.Cache.enable_cache('./')
        session = ff1.get_session(int(year), circuito, 'R')
        weekend = session.event
        session.load()
        lap = session.laps.pick_fastest()

        # Get telemetry data
        x = np.array(lap.telemetry['X'])
        y = np.array(lap.telemetry['Y'])
        color = lap.telemetry['Speed']      # value to base the color gradient on

        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)

        # We create a plot with title and adjust some settings to make it look good.
        fig, ax = plt.subplots(sharex=True, sharey=True, figsize=(12, 6.75))
        fig.suptitle(f'{weekend.name} {year} - Speed', size=24, y=0.97)

        # Adjust margins and turn off the axis
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.12)
        ax.axis('off')

        # Plot the background track line
        ax.plot(x, y, color='black', linestyle='-', linewidth=16, zorder=0)

        # Create a continuous norm to map from data points to colors
        colormap = plt.get_cmap('viridis')  # You should choose a suitable colormap
        norm = plt.Normalize(color.min(), color.max())
        lc = LineCollection(segments, cmap=colormap, norm=norm, linestyle='-', linewidth=5)

        # Set the values used for colormapping
        lc.set_array(color)

        # Merge all line segments together
        line = ax.add_collection(lc)

        # Create a colorbar
        cbaxes = fig.add_axes([0.25, 0.05, 0.5, 0.05])
        normlegend = mpl.colors.Normalize(vmin=color.min(), vmax=color.max())
        legend = mpl.colorbar.Colorbar(cbaxes, norm=normlegend, cmap=colormap, orientation="horizontal")

        # Clear the previous layout and add the new figure
        self.clearLayout(self.plotter)
        self.plotter.addWidget(FigureCanvas(fig))

    def redirecciona(self):
        if(self.bEstadistica.currentText()=="Tiempo por vuelta"):
            self.tiempoVueltas()
        if(self.bEstadistica.currentText()=="Telemetria"):
            self.telemetria()
        if(self.bEstadistica.currentText()=="Adelantamientos"):
            self.adelantamientos()
        if(self.bEstadistica.currentText()=="Marchas vuelta"):
            self.marchasVuelta()
        if(self.bEstadistica.currentText()=="Ver Qualy"):
            self.verQualy()
        if(self.bEstadistica.currentText()=="Tiempo medio pit stop"):
            self.infoParadas()
        if(self.bEstadistica.currentText()=="Mapa de velocidad"):
            self.mapaVelocidad()
        if(self.bEstadistica.currentText()=="Información de neumaticos"):
            self.infoNeumaticos()
        if(self.bEstadistica.currentText()=="Ritmo de carrera"):
            pilotos = self.listaPilotos
            year = self.bAnio.currentText()
            circuito = self.bCircuito.currentText()
            
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
            self.ritmo_carrera_thread.resultReady.connect(self.mostrar_grafico_ritmo_carrera)
            
            self.ritmo_carrera_thread.finished.connect(progress_dialog.accept)

            # Paso 4: Iniciar el hilo RitmoCarreraThread
            self.ritmo_carrera_thread.start()
            # Mostrar el diálogo de progreso
            progress_dialog.exec_()
    def mostrar_grafico_ritmo_carrera(self, fig):
        # Mostrar el gráfico en un canvas de Matplotlib
        self.clearLayout(self.plotter)
        self.plotter.addWidget(FigureCanvas(fig))
    def ritmoCarrera(self):
        pilotos=self.listaPilotos
        year=self.bAnio.currentText()
        ff1.Cache.enable_cache('./')
        granPremio = ff1.get_session(int(year), self.bCircuito.currentText(), 'R')
        laps = granPremio.load().laps
        laps['LapTimeSeconds'] = laps['LapTime'].dt.total_seconds()
        laps = laps.loc[(laps['PitOutTime'].isnull() & laps['PitInTime'].isnull())]
        fig, ax = plt.subplots()
        data=[]
        for p in pilotos:
            driver=laps.pick_driver(p)
            data.append(driver['LapTimeSeconds'])
        ax.boxplot(data, labels=pilotos, showfliers=False)
        #print(laps['LapTimeSeconds'], laps['Driver']) 
        self.clearLayout(self.plotter)
        self.plotter.addWidget(FigureCanvas(fig))

    def verQualy(self):
        year=self.bAnio.currentText()
        ff1.Cache.enable_cache('./')
        ff1.plotting.setup_mpl(mpl_timedelta_support=True, color_scheme=None, misc_mpl_mods=False)
        quali = ff1.get_session(int(year), self.bCircuito.currentText(), 'Q')
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
            color = ff1.plotting.team_color(lap['Team'])
            team_colors.append(color)
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

        ax.set_title(f"{quali.event['EventName']} {quali.event.year} Qualifying\n"
             f"Fastest Lap: {lap_time_string} ({pole_lap['Driver']})")

        self.clearLayout(self.plotter)
        self.plotter.addWidget(FigureCanvas(figure))

    def infoNeumaticos(self):
        year=self.bAnio.currentText()
        ff1.Cache.enable_cache('./')
        session = ff1.get_session(int(year), self.bCircuito.currentText(), 'R')
        session.load()
        laps = session.laps
        drivers = session.drivers
        drivers = [session.get_driver(driver)["Abbreviation"] for driver in drivers]
        stints = laps[["Driver", "Stint", "Compound", "LapNumber"]]
        stints = stints.groupby(["Driver", "Stint", "Compound"])
        stints = stints.count().reset_index()
        stints = stints.rename(columns={"LapNumber": "StintLength"})
        fig, ax = plt.subplots(figsize=(5, 10))

        for driver in drivers:
            driver_stints = stints.loc[stints["Driver"] == driver]

            previous_stint_end = 0
            for idx, row in driver_stints.iterrows():
                # each row contains the compound name and stint length
                # we can use these information to draw horizontal bars
                plt.barh(
                    y=driver,
                    width=row["StintLength"],
                    left=previous_stint_end,
                    color=ff1.plotting.COMPOUND_COLORS[row["Compound"]],
                    edgecolor="black",
                    fill=True
                )

                previous_stint_end += row["StintLength"]
        plt.title("Compuestos utilizados durante la carrera")
        plt.xlabel("Número de vuelta")
        plt.grid(False)
        # invert the y-axis so drivers that finish higher are closer to the top
        ax.invert_yaxis()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)

        self.clearLayout(self.plotter)
        self.plotter.addWidget(FigureCanvas(fig))


 
    def telemetria(self):
        pilotos=self.listaPilotos
        #cargo la sesion y selecciono el piloto
        year=self.bAnio.currentText()
        ff1.Cache.enable_cache('./')
        granPremio = ff1.get_session(int(year), self.bCircuito.currentText(), 'R')	
        laps=granPremio.load()
        laps=granPremio.laps
        fig, ax = plt.subplots(3, sharex=True)
        lines=[]
        lines1=[]
        lines2=[]
        for p in pilotos:
            driver=laps.pick_driver(p)
			#cargo la vuelta rapida y la telemetria de la misma
            rapida=driver.pick_fastest()
            telemetry = rapida.get_car_data().add_distance()
			#for x in range(1,laps.LapNumber[-1:]):
			#self.bVueltas.add(x)
			
            line1,=ax[0].plot(np.array(telemetry['Distance']), np.array(telemetry['Speed']), label=p)
            ax[0].set(ylabel='velocidad')
            line2,=ax[1].plot(np.array(telemetry['Distance']), np.array(telemetry['Throttle']), label=p)
            ax[1].set(ylabel='Acelerador')
            line3,=ax[2].plot(np.array(telemetry['Distance']), np.array(telemetry['Brake']), label=p)
            ax[2].set(ylabel='Freno')
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
			# On the pick event, find the original line corresponding to the legend
			# # proxy line, and toggle its visibility.
            legline = event.artist
            origline = lined[legline]
            for o in origline:
                visible = not o.get_visible()
                o.set_visible(visible)
			# Change the alpha on the line in the legend so we can see what lines
			# have been toggled.
                legline.set_alpha(1.0 if visible else 0.2)
                fig.canvas.draw()
        fig.canvas.mpl_connect('pick_event', on_pick)
        self.clearLayout(self.plotter)
        self.plotter.addWidget(FigureCanvas(fig))
        #fig.savefig("/Users/alejandrogutierrezalvarez/Desktop/F1/prueba.pdf")        
    def tiempoVueltas(self):
        pilotos=self.listaPilotos
        year=self.bAnio.currentText()
        ff1.Cache.enable_cache('./')
        granPremio = ff1.get_session(int(year), self.bCircuito.currentText(), 'R')
        granPremio.load()
        laps=granPremio.laps
        fig, ax = plt.subplots()
        ax.set_xlabel("Vuelta")
        ax.set_ylabel("Tiempo")
        ax.set_title("Comparativa de pilotos")
        lines=[]
        for p in pilotos:
            driver=laps.pick_driver(p)
            line, =ax.plot(np.array(driver['LapNumber']), np.array(driver['LapTime']), label=p)
            lines.append(line)
        leg=ax.legend(fancybox=True, shadow=True, loc="upper right")
        lined= dict()
        for legline, origline in zip(leg.get_lines(), lines):
            legline.set_picker(5)  # Enable picking on the legend line.
            origline.set_visible(False)
            legline.set_alpha(0.2)
            lined[legline] = origline
        lines[0].set_visible(True)
        leg.get_lines()[0].set_alpha(1)
        def on_pick(event):
			# On the pick event, find the original line corresponding to the legend
			# # proxy line, and toggle its visibility.
            legline = event.artist
            origline = lined[legline]
            visible = not origline.get_visible()
            origline.set_visible(visible)
			# Change the alpha on the line in the legend so we can see what lines
			# have been toggled.
            legline.set_alpha(1.0 if visible else 0.2)
            fig.canvas.draw()

        fig.canvas.mpl_connect('pick_event', on_pick)
        self.clearLayout(self.plotter)
        self.plotter.addWidget(FigureCanvas(fig))
    def adelantamientos(self):
        ff1.plotting.setup_mpl(misc_mpl_mods=False)
        year = self.bAnio.currentText()
        ff1.Cache.enable_cache('./')
        session = ff1.get_session(2023, self.bCircuito.currentText(), 'R')
        session.load(telemetry=False, weather=False)
        fig, ax = plt.subplots(figsize=(8.0, 4.9))
        for drv in session.drivers:
            drv_laps = session.laps.pick_driver(drv)

            abb = drv_laps['Driver'].iloc[0]
            color = ff1.plotting.driver_color(abb)

            # Convert 'LapNumber' and 'Position' to NumPy arrays
            lap_numbers = drv_laps['LapNumber'].values
            positions = drv_laps['Position'].values

            ax.plot(lap_numbers, positions, label=abb, color=color)

        ax.set_ylim([20.5, 0.5])
        ax.set_yticks([1, 5, 10, 15, 20])
        ax.set_xlabel('Vuelta')
        ax.set_ylabel('Posición')
        ax.legend(bbox_to_anchor=(1.0, 1.02))
        plt.tight_layout()
        self.clearLayout(self.plotter)
        self.plotter.addWidget(FigureCanvas(fig))
    def marchasVuelta(self):
        year=self.bAnio.currentText()
        ff1.Cache.enable_cache('./')
        session = ff1.get_session(int(year), self.bCircuito.currentText(), 'R')
        session.load()
        laps = session.laps
        lap = laps.pick_fastest()
        tel = lap.get_telemetry()

        x = np.array(tel['X'].values)
        y = np.array(tel['Y'].values)

        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        gear = tel['nGear'].to_numpy().astype(float)

        cmap = cm.get_cmap('Paired')
        lc_comp = LineCollection(segments, norm=plt.Normalize(1, cmap.N+1), cmap=cmap)
        lc_comp.set_array(gear)
        lc_comp.set_linewidth(4)

        # Create the figure and axes
        fig = Figure(figsize=(8, 6), dpi=100)
        ax = fig.add_subplot(111)

        # Add the LineCollection to the axes
        ax.add_collection(lc_comp)
        ax.axis('equal')
        ax.tick_params(labelleft=False, left=False, labelbottom=False, bottom=False)

        title = plt.suptitle(
        f"Fastest Lap Gear Shift Visualization\n"
        f"{lap['Driver']} - {session.event['EventName']} {session.event.year}"
)                           

        # Add the colorbar to the plot
        cbar = fig.colorbar(mappable=lc_comp, label="Gear", boundaries=np.arange(1, 10))
        cbar.set_ticks(np.arange(1.5, 9.5))
        cbar.set_ticklabels(np.arange(1, 9))

        self.clearLayout(self.plotter)
        self.plotter.addWidget(FigureCanvas(fig))



    def get_round_number(self, year, circuit_name):
        base_url = 'http://ergast.com/api/f1'
        url = f'{base_url}/{year}.json'

        response = requests.get(url)
        data = response.json()

        races = data['MRData']['RaceTable']['Races']
        circuit_round_map = {race['Circuit']['circuitName']: race['round'] for race in races}

        return circuit_round_map.get(circuit_name)

    def infoParadas(self):
        base_url = 'http://ergast.com/api/f1'
        year = self.bAnio.currentText()
        circuit_name = self.bCircuito.currentText()
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

        #color_orden=[]
        #for driver in avg_pit_stop_time.iterrows():
            #color_orden.append(ff1.plotting.team_color(driver[1]['driverId']))
        #avg_pit_stop_time['color']=color_orden        
        #ax.bar(avg_pit_stop_time['driverId'],avg_pit_stop_time['duration'], color=avg_pit_stop_time['color'])
        ax.bar(avg_pit_stop_time['driverId'],avg_pit_stop_time['duration'])

        ax.set_xticklabels(avg_pit_stop_time['driverId'], rotation=45, ha='right')

        # Set labels and title
        ax.set_xlabel('Driver')
        ax.set_ylabel('Average Pit Stop Time (s)')
        ax.set_title('Average Pit Stop Time per Driver')
        self.clearLayout(self.plotter)
        self.plotter.addWidget(FigureCanvas(fig))


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
