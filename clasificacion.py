import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5 import uic
from Listas import años
import numpy as np
import fastf1 as ff1
import matplotlib
import requests
import json
from datetime import date
matplotlib.use('QT5Agg')

import matplotlib.pylab as plt
from matplotlib.backends.backend_qt5agg import FigureCanvas 
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar


class Clasificacion(QWidget):
	def __init__(self):
		super().__init__()
		uic.loadUi('Interfaces/clasificacion.ui', self)
		self.cargarTemporadas()
		self.bBuscar.pressed.connect(self.buscar)
		self.cbAnio.setMaxVisibleItems(10)  # Ajustar el valor según sea necesario


	
	def buscar(self):
		self.tableWidget.setRowCount(0)
		if(self.rbPiloto.isChecked()):
			r=requests.get("https://ergast.com/api/f1/"+self.cbAnio.currentText()+"/driverStandings.json")
			r=json.loads(r.text)
			posiciones=r["MRData"]["StandingsTable"]["StandingsLists"]
			for p in posiciones:
				for d in p["DriverStandings"]:
					self.tableWidget.insertRow(self.tableWidget.rowCount())
					item=QtWidgets.QTableWidgetItem(d["position"])
					self.tableWidget.setItem(self.tableWidget.rowCount()-1,0,item)
					item=QtWidgets.QTableWidgetItem(d["Driver"]["givenName"]+" "+d["Driver"]["familyName"])
					self.tableWidget.setItem(self.tableWidget.rowCount()-1,1,item)
					item=QtWidgets.QTableWidgetItem(d["points"])
					self.tableWidget.setItem(self.tableWidget.rowCount()-1,2,item)
					item=QtWidgets.QTableWidgetItem(d["wins"])
					self.tableWidget.setItem(self.tableWidget.rowCount()-1,3,item)
					item=QtWidgets.QTableWidgetItem(d["Driver"]["nationality"])
					self.tableWidget.setItem(self.tableWidget.rowCount()-1,4,item)
					
		if(self.rbConstructores.isChecked()):
			r=requests.get("https://ergast.com/api/f1/"+self.cbAnio.currentText()+"/constructorStandings.json")
			r=json.loads(r.text)
			posiciones=r["MRData"]["StandingsTable"]["StandingsLists"]
			for p in posiciones:
				for d in p["ConstructorStandings"]:
					self.tableWidget.insertRow(self.tableWidget.rowCount())
					item=QtWidgets.QTableWidgetItem(d["position"])
					self.tableWidget.setItem(self.tableWidget.rowCount()-1,0,item)
					item=QtWidgets.QTableWidgetItem(d["Constructor"]["name"])
					self.tableWidget.setItem(self.tableWidget.rowCount()-1,1,item)
					item=QtWidgets.QTableWidgetItem(d["points"])
					self.tableWidget.setItem(self.tableWidget.rowCount()-1,2,item)
					item=QtWidgets.QTableWidgetItem(d["wins"])
					self.tableWidget.setItem(self.tableWidget.rowCount()-1,3,item)
					item=QtWidgets.QTableWidgetItem(d["Constructor"]["nationality"])
					self.tableWidget.setItem(self.tableWidget.rowCount()-1,4,item)
				


	def cargarTemporadas(self):
		for x in range(1950,date.today().year):
			self.cbAnio.addItem(str(x))




if __name__ == '__main__':
	app=QApplication(sys.argv)
	myApp=Clasificacion()
	myApp.show()

	try:
		sys.exit(app.exec())
	except SystemExit:
		print('Cerrando ventana...')