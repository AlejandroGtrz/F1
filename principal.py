import sys
from PyQt5 import QtWidgets, QtGui, QtCore, uic, QtWebEngineWidgets, uic
import requests
import json
from comparativas import Comparativas

class MyApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Carga la interfaz de usuario desde el archivo .ui
        uic.loadUi('Interfaces/principal.ui', self)

        # Configura los botones y sus funciones
        self.bClasificacion.setIcon(QtGui.QIcon('Resources/Copa.png'))
        self.bClasificacion.setIconSize(QtCore.QSize(64, 64))
        self.bClasificacion.pressed.connect(self.Abrir_Clasificacion)

        self.bPilotos.setIcon(QtGui.QIcon('Resources/Pilotos.png'))
        self.bPilotos.setIconSize(QtCore.QSize(64, 64))
        self.bPilotos.pressed.connect(self.Abrir_Comparativas)

        self.bCircuitos.setIcon(QtGui.QIcon('Resources/Circuitos.png'))
        self.bCircuitos.setIconSize(QtCore.QSize(64, 64))
        self.bCircuitos.pressed.connect(self.Abrir_Circuitos)

        self.bParadas.setIcon(QtGui.QIcon('Resources/Pitstop.png'))
        self.bParadas.setIconSize(QtCore.QSize(64, 64))

        # Crea un visor web para cargar la página de Twitter
        self.twitter_view = QtWebEngineWidgets.QWebEngineView()
        self.twitter_view.setUrl(QtCore.QUrl("https://f1.com/"))
        self.lTwitter.addWidget(self.twitter_view)

        # Obtén el podio y clasificación (esto se puede mover a funciones separadas si es necesario)
        self.Obtener_Podio()

    def Obtener_Podio(self):
        r = requests.get("http://ergast.com/api/f1/current/last/results.json")
        r = json.loads(r.text)
        resultado = r["MRData"]["RaceTable"]["Races"][0]["Results"]
        for d in resultado:
            self.twResultados.insertRow(self.twResultados.rowCount())
            item = QtWidgets.QTableWidgetItem(d["position"])
            self.twResultados.setItem(self.twResultados.rowCount() - 1, 0, item)
            item = QtWidgets.QTableWidgetItem(d["Driver"]["givenName"] + " " + d["Driver"]["familyName"])
            self.twResultados.setItem(self.twResultados.rowCount() - 1, 2, item)
            item = QtWidgets.QTableWidgetItem(d["points"])
            self.twResultados.setItem(self.twResultados.rowCount() - 1, 1, item)

    def Obtener_Clasificacion(self):
        r = requests.get("http://ergast.com/api/f1/current/driverStandings.json")
        r = json.loads(r.text)
        resultado = r["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"]
        for d in resultado:
            self.twClasificacion.insertRow(self.twClasificacion.rowCount())
            item = QtWidgets.QTableWidgetItem(d["position"])
            self.twClasificacion.setItem(self.twClasificacion.rowCount() - 1, 0, item)
            item = QtWidgets.QTableWidgetItem(d["Driver"]["givenName"] + " " + d["Driver"]["familyName"])
            self.twClasificacion.setItem(self.twClasificacion.rowCount() - 1, 2, item)
            item = QtWidgets.QTableWidgetItem(d["points"])
            self.twClasificacion.setItem(self.twClasificacion.rowCount() - 1, 1, item)

    def Abrir_Clasificacion(self):
        # Aquí puedes realizar alguna acción relacionada con la clasificación si lo deseas.
        pass

    def Abrir_Comparativas(self):
        self.ui = Comparativas()
        self.ui.show()

    def Abrir_Circuitos(self):
        self.ui = Circuitos()
        self.ui.show()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    myApp = MyApp()
    myApp.show()
    sys.exit(app.exec())
