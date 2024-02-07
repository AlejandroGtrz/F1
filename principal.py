import sys
from PyQt5 import QtWidgets, QtGui, QtCore, uic, QtWebEngineWidgets, uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QToolTip
import requests
import json
from circuitos import Circuitos
from pilotos import Pilotos
from clasificacion import Clasificacion

class MyApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Carga la interfaz de usuario desde el archivo .ui
        uic.loadUi('Interfaces/principal.ui', self)

        # Configura los botones y sus funciones
        self.bClasificacion.setIcon(QtGui.QIcon('Resources/Copa.png'))
        self.bClasificacion.setIconSize(QtCore.QSize(64, 64))
        self.bClasificacion.pressed.connect(self.Abrir_Clasificacion)
        self.bClasificacion.setToolTip("Abrir ventana Clasificación")

        self.bPilotos.setIcon(QtGui.QIcon('Resources/Pilotos.png'))
        self.bPilotos.setIconSize(QtCore.QSize(64, 64))
        self.bPilotos.pressed.connect(self.Abrir_Pilotos)
        self.bPilotos.setToolTip("Abrir ventana Pilotos")

        self.bCircuitos.setIcon(QtGui.QIcon('Resources/Circuitos.png'))
        self.bCircuitos.setIconSize(QtCore.QSize(64, 64))
        self.bCircuitos.pressed.connect(self.Abrir_Circuitos)
        self.bCircuitos.setToolTip("Abrir ventana Estadísticas")



        # Crea un visor web para cargar la página de Twitter
        self.twitter_view = QtWebEngineWidgets.QWebEngineView()
        self.twitter_view.setUrl(QtCore.QUrl("https://www.formula1.com/"))
        self.lTwitter.addWidget(self.twitter_view)

        # Obtén el podio y clasificación (esto se puede mover a funciones separadas si es necesario)
        self.Obtener_Podio()

        # Personalizar el tamaño de las columnas de la tabla
        self.twResultados.setColumnWidth(0, 70)
        self.twResultados.setColumnWidth(1, 138)
        self.twResultados.setColumnWidth(2, 70)

        # Personalizar el alto del header
        header = self.twResultados.horizontalHeader()
        header.setFixedHeight(30)


    def Obtener_Podio(self):
        r = requests.get("http://ergast.com/api/f1/current/last/results.json")
        r = json.loads(r.text)
        resultado = r["MRData"]["RaceTable"]["Races"][0]["Results"]
        # Obtener el nombre de la carrera
        nombre_carrera = r["MRData"]["RaceTable"]["Races"][0]["raceName"]
        self.label.setText(f"Último Resultado: {nombre_carrera}")
        for d in resultado:
            self.twResultados.insertRow(self.twResultados.rowCount())
            item = QtWidgets.QTableWidgetItem(d["position"])
            item.setTextAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
            self.twResultados.setItem(self.twResultados.rowCount() - 1, 0, item)
            item = QtWidgets.QTableWidgetItem(d["Driver"]["givenName"] + " " + d["Driver"]["familyName"])
            item.setTextAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
            self.twResultados.setItem(self.twResultados.rowCount() - 1, 1, item)            
            item = QtWidgets.QTableWidgetItem(d["points"])
            item.setTextAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
            self.twResultados.setItem(self.twResultados.rowCount() - 1, 2, item)

    def Obtener_Clasificacion(self):
        r = requests.get("http://ergast.com/api/f1/current/driverStandings.json")
        r = json.loads(r.text)
        resultado = r["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"]

        for d in resultado:
            self.twClasificacion.insertRow(self.twClasificacion.rowCount())
            item = QtWidgets.QTableWidgetItem(d["position"])
            self.twClasificacion.setItem(self.twClasificacion.rowCount() - 1, 0, item)
            item = QtWidgets.QTableWidgetItem(d["Driver"]["givenName"] + " " + d["Driver"]["familyName"])
            self.twClasificacion.setItem(self.twClasificacion.rowCount() - 1, 1, item)
            item = QtWidgets.QTableWidgetItem(d["points"])
            self.twClasificacion.setItem(self.twClasificacion.rowCount() - 1, 2, item)

    def Abrir_Clasificacion(self):
        self.ui = Clasificacion()
        self.ui.show()

    def Abrir_Pilotos(self):
        self.ui = Pilotos()
        self.ui.show()

    def Abrir_Circuitos(self):
        self.ui = Circuitos()
        self.ui.show()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    myApp = MyApp()
    myApp.show()
    sys.exit(app.exec())
