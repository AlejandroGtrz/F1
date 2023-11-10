import sys
import mpld3
from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6 import uic
import pandas as pd
from Listas import años
from Listas import estadisticas
from fastf1.core import Laps
from timple.timedelta import strftimedelta
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


class MyApp(QWidget):
	def __init__(self):
		super().__init__()
		uic.loadUi('pruebaGui2.ui', self)
		self.bAnio.addItems(años)
		self.bAnio.activated.connect(self.addCircuitos)
		self.bAnio.setCurrentIndex(-1)
		self.bCircuito.activated.connect(self.addEstadisticas)
		self.bEstadistica.activated.connect(self.addPilotos)
		self.bPiloto.activated.connect(self.activaBuscar)
		self.bBuscar.pressed.connect(self.redirecciona)
		self.bAdd.pressed.connect(self.listarPiloto)
		self.bLimpiar.pressed.connect(self.limpiar)
		plotting.setup_mpl()

	def redirecciona(self):
		if(self.bEstadistica.currentText()=="Ver Qualy"):
			self.verQualy()
		if(self.bEstadistica.currentText()=="Telemetria"):
			self.telemetria()
		if(self.bEstadistica.currentText()=="Desglose de marchas"):
			self.marchas()
		if(self.bEstadistica.currentText()=="Desglose de velocidad"):
			self.velocidad()
		if(self.bEstadistica.currentText()=="Tiempo por vuelta"):
			self.tiempoVueltas()
	def limpiar(self):
		self.clearLayout(self.plotter)
		self.lListaPilotos.setText("")
		self.activaBuscar()
		
	def listarPiloto(self):
		self.lListaPilotos.setText(self.lListaPilotos.text()+self.bPiloto.currentText()+";")
		self.bBuscar.setEnabled(True)
	def activaBuscar(self):
		if(self.bEstadistica.currentText()!="Tiempo por vuelta" and self.bEstadistica.currentText()!="Telemetria"):
			self.bBuscar.setEnabled(True)
			self.bAdd.setEnabled(False)
		if(self.bEstadistica.currentText()=="Tiempo por vuelta" or self.bEstadistica.currentText()=="Telemetria"):
			self.bAdd.setEnabled(True)
			if(self.lListaPilotos.text()==""):
				self.bBuscar.setEnabled(False)
	
	def tiempoVueltas(self):
		pilotos=[self.bPiloto.itemText(i) for i in range(self.bPiloto.count())]
		year=self.bAnio.currentText()
		ff1.Cache.enable_cache('/Users/alejandrogutierrezalvarez/Desktop/F1')
		granPremio = ff1.get_session(year, self.bCircuito.currentText(), 'R')
		laps=granPremio.load_laps()
		fig, ax = plt.subplots()
		ax.set_xlabel("Vuelta")
		ax.set_ylabel("Tiempo")
		ax.set_title("Comparativa de pilotos")
		lines=[]
		for p in pilotos:
			driver=laps.pick_driver(p)
			line, =ax.plot(driver['LapNumber'], driver['LapTime'], label=p)
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
	def marchas(self):
		year=self.bAnio.currentText()
		ff1.Cache.enable_cache('/Users/alejandrogutierrezalvarez/Desktop/F1')
		session = ff1.get_session(year, self.bCircuito.currentText(), 'R')
		laps = session.load_laps(with_telemetry=True)
		driver=laps.pick_driver(self.bPiloto.currentText())
		lap = driver.pick_fastest()
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
		figure, ax= plt.subplots()
	
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

		self.clearLayout(self.plotter)
		self.plotter.addWidget(FigureCanvas(figure))
	def velocidad(self):
		year=self.bAnio.currentText()
		ff1.Cache.enable_cache('/Users/alejandrogutierrezalvarez/Desktop/F1')
		session = ff1.get_session(year, self.bCircuito.currentText(), 'R')

		##############################################################################
		# First, we define some variables that allow us to conveniently control what
		# we want to plot.
		colormap = mpl.cm.plasma


		##############################################################################
		# Next, we load the session and select the desired data.
		laps = session.load_laps(with_telemetry=True)
		lap = laps.pick_driver(self.bPiloto.currentText()).pick_fastest()

		# Get telemetry data
		x = lap.telemetry['X']              # values for x-axis
		y = lap.telemetry['Y']              # values for y-axis
		color = lap.telemetry['Speed']      # value to base color gradient on


		##############################################################################
		# Now, we create a set of line segments so that we can color them
		# individually. This creates the points as a N x 1 x 2 array so that we can
		# stack points  together easily to get the segments. The segments array for
		# line collection needs to be (numlines) x (points per line) x 2 (for x and y)
		points = np.array([x, y]).T.reshape(-1, 1, 2)
		segments = np.concatenate([points[:-1], points[1:]], axis=1)


		##############################################################################
		# After this, we can actually plot the data.

		# We create a plot with title and adjust some setting to make it look good.
		fig, ax = plt.subplots(sharex=True, sharey=True)
		fig.suptitle(f'{self.bCircuito.currentText()} {year} - {self.bPiloto.currentText()} - Speed', size=20, y=0.97)

		# Adjust margins and turn of axis
		plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.12)
		ax.axis('off')


		# After this, we plot the data itself.
		# Create background track line
		ax.plot(lap.telemetry['X'], lap.telemetry['Y'], color='black', linestyle='-', linewidth=16, zorder=0)

		# Create a continuous norm to map from data points to colors
		norm = plt.Normalize(color.min(), color.max())
		lc = LineCollection(segments, cmap=colormap, norm=norm, linestyle='-', linewidth=5)

		# Set the values used for colormapping
		lc.set_array(color)

		# Merge all line segments together
		line = ax.add_collection(lc)


		# Finally, we create a color bar as a legend.
		cbaxes = fig.add_axes([0.25, 0.05, 0.5, 0.05])
		normlegend = mpl.colors.Normalize(vmin=color.min(), vmax=color.max())
		legend = mpl.colorbar.ColorbarBase(cbaxes, norm=normlegend, cmap=colormap, orientation="horizontal")


		# Show the plot
		self.clearLayout(self.plotter)
		self.plotter.addWidget(FigureCanvas(fig))

	def telemetria(self):
		pilotos=self.lListaPilotos.text().split(";")
		pilotos.pop()
		#cargo la sesion y selecciono el piloto
		year=self.bAnio.currentText()
		ff1.Cache.enable_cache('/Users/alejandrogutierrezalvarez/Desktop/F1')
		granPremio = ff1.get_session(year, self.bCircuito.currentText(), 'R')	
		laps=granPremio.load_laps(with_telemetry=True)
		fig, ax = plt.subplots(3)
		for p in pilotos:
			driver=laps.pick_driver(p)
			#cargo la vuelta rapida y la telemetria de la misma
			rapida=driver.pick_fastest()
			telemetry = rapida.get_car_data().add_distance()
			#for x in range(1,laps.LapNumber[-1:]):
			#self.bVueltas.add(x)
			
			ax[0].plot(telemetry['Distance'], telemetry['Speed'], label=p)
			ax[0].set(ylabel='velocidad')
			ax[0].legend(loc="lower right")
			ax[1].plot(telemetry['Distance'], telemetry['Throttle'], label=p)
			ax[1].set(ylabel='Acelerador')
			ax[2].plot(telemetry['Distance'], telemetry['Brake'], label=p)
			ax[2].set(ylabel='Freno')
			for a in ax.flat:
				a.label_outer()
        
		self.clearLayout(self.plotter)
		self.plotter.addWidget(FigureCanvas(fig))

	def addEstadisticas(self):
		self.lListaPilotos.setText("")
		self.bEstadistica.clear()
		self.bPiloto.clear()
		for e in estadisticas:
			self.bEstadistica.addItem(e)
		self.bEstadistica.setCurrentIndex(-1)

	def verQualy(self):
		year=self.bAnio.currentText()
		ff1.Cache.enable_cache('/Users/alejandrogutierrezalvarez/Desktop/F1')
		ff1.plotting.setup_mpl(mpl_timedelta_support=True, color_scheme=None, misc_mpl_mods=False)
		quali = ff1.get_session(year, self.bCircuito.currentText(), 'Q')
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

		ax.set_title(f"{quali.weekend.name} {quali.weekend.year} Clasificación\n"
			f"Vuelta Rapida: {lap_time_string} ({pole_lap['Driver']})")

		self.clearLayout(self.plotter)
		self.plotter.addWidget(FigureCanvas(figure))

	def addPilotos(self):
		self.lListaPilotos.setText("")
		if(self.bEstadistica.currentText()=="Ver Qualy"):
			self.bPiloto.clear()
			self.bPiloto.setEnabled(False)
			self.bBuscar.setEnabled(True)
			self.bAdd.setEnabled(False)
		else:
			self.bPiloto.setEnabled(True)
			self.bBuscar.setEnabled(False)
			self.bAdd.setEnabled(False)
			year=self.bAnio.currentText()
			self.bPiloto.clear()
			drivers={}
			if(self.bCircuito.currentText()!=""):
				if len(drivers)==0:
					r = requests.get("https://ergast.com/api/f1/"+str(year)+"/drivers.json")
					r = json.loads(r.text)
					drivers = r["MRData"]["DriverTable"]["Drivers"]
				for d in drivers:
					self.bPiloto.addItem(d['code'])
			self.bPiloto.setCurrentIndex(-1)
			

	def addCircuitos(self):
		self.lListaPilotos.setText("")
		self.bCircuito.clear()
		self.bEstadistica.clear()
		self.bPiloto.clear()
		year=self.bAnio.currentText()
		circuits={}
		if len(circuits)==0:
			r = requests.get("https://ergast.com/api/f1/"+str(year)+"/circuits.json")
			r = json.loads(r.text)
			circuits = r["MRData"]["CircuitTable"]["Circuits"]
		for s in circuits:
			self.bCircuito.addItem(s['circuitName'])
		self.bCircuito.setCurrentIndex(-1)

	def clearLayout(self, layout):
		while layout.count():
			child = layout.takeAt(0)
			if child.widget():
				child.widget().deleteLater()
	



if __name__ == '__main__':
	app=QApplication(sys.argv)
	myApp=MyApp()
	myApp.show()

	try:
		sys.exit(app.exec())
	except SystemExit:
		print('Cerrando ventana...')