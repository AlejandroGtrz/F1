import sys
import mpld3
from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6 import uic
import pandas as pd
from Listas import años
from Listas import estadisticas_comparativas
from fastf1.core import Laps
from timple.timedelta import strftimedelta
import xlwings as xw
import numpy as np
import pruebaF1 as f1
import fastf1 as ff1
from fastf1 import plotting
import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib import cm
from matplotlib.widgets import Button, RadioButtons, CheckButtons
import requests
import json
import numpy as np
from matplotlib.collections import LineCollection
mpl.use('QT5Agg')


from matplotlib.backends.backend_qt5agg import FigureCanvas 
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class Comparativas(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('Interfaces/comparativas.ui', self)

        self.listaPilotos=[]
        self.circuitos={}
        self.bAnio.addItems(años)
        self.bAnio.activated.connect(self.addCircuitos)
        self.bAnio.setCurrentIndex(-1)
        self.bCircuito.activated.connect(self.addEstadisticas)
        self.bEstadistica.activated.connect(self.addPilotos)
        self.bBuscar.pressed.connect(self.redirecciona)

    def insertHeader(self,rng, text):
        rng.value = text
        rng.font.bol = True
        rng.font.size =24
        rng.font.color = (0,0,139)

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
        for e in estadisticas_comparativas:
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
            self.tiempoVueltas()
        if(self.bEstadistica.currentText()=="Telemetria"):
            self.telemetria()
        if(self.bEstadistica.currentText()=="Mapa de calor"):
            self.mapaCalor()



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
        ff1.Cache.enable_cache('/Users/alejandrogutierrezalvarez/Desktop/F1')
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
    def mapaCalor(self):
        pilotos=self.listaPilotos
        # Descargar los datos de la sesión
        year=self.bAnio.currentText()
        ff1.Cache.enable_cache('/Users/alejandrogutierrezalvarez/Desktop/F1')
        session = ff1.get_session(int(year), self.bCircuito.currentText(), 'R')

        # Preprocesar los datos de todos los pilotos
        laps = session.load()
        laps=session.laps
        data = []
        for lap in laps:
            telemetry= lap['telemetry']
            speed = telemetry['CarStatus']['mz']            
            speed -= np.min(speed)
            speed /= np.max(speed)
            data.append(speed)

        # Generar la leyenda
        names = [lap['Driver']['code'] for lap in laps]
        fig, ax = plt.subplots()
        lines = ax.plot([], [])
        leg = ax.legend(names, loc='upper right')
        plt.close()

        # Crear la figura interactiva
        fig, ax = plt.subplots()
        heatmap = ax.imshow(data[0], cmap='viridis')
        ax.invert_yaxis()
        plt.colorbar(heatmap)
        plt.subplots_adjust(right=0.75)

        # Función para actualizar el mapa de calor al seleccionar una leyenda
        def update_legend(label):
            index = pilotos.index(label)
            heatmap.set_data(data[index])

    # Conectar la leyenda con la función de actualización
        for legline, legtext in zip(leg.get_lines(), leg.get_texts()):
            legline.set_picker(True)
            legline.set_pickradius(5)
            legtext.set_picker(True)
            legtext.set_pickradius(5)
            legline.set_visible(True)
            legtext.set_visible(True)
            legline.set_gid(legtext.get_text())
            legtext.set_gid(legtext.get_text())
        
        
        fig.canvas.mpl_connect('pick_event', lambda event: update_legend(event.artist.get_gid()))
        self.clearLayout(self.plotter)
        self.plotter.addWidget(FigureCanvas(fig))
        #plt.show()

    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()




if __name__ == '__main__':
    app=QApplication(sys.argv)
    myApp=Comparativas()
    myApp.show()
    try:
        sys.exit(app.exec())
    except SystemExit:
        print('Cerrando ventana...')
