import sys
import requests
from PyQt6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QWidget, QLabel, QScrollArea, QVBoxLayout, QPushButton
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt

class Pilotos(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Lista de Pilotos de Fórmula 1")
        self.setGeometry(100, 100, 500, 720)
        self.setStyleSheet("background-color: white;")

        # Crea una lista de pilotos de Fórmula 1.
        self.pilotos = obtener_pilotos()

        # Crea un widget central y un layout para agregar elementos.
        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        for piloto in self.pilotos:
            card_widget = QWidget()
            card_layout = QHBoxLayout(card_widget)
            card_widget.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc; margin: 5px; padding: 5px;")


            # Crear una etiqueta para mostrar el nombre y los puntos en líneas separadas
            nombre_label = QLabel(f"{piloto['nombre']} {piloto['apellido']}\nPuntos: {piloto['puntos']}\nPosición: {piloto['posicion']}")
            nombre_label.setFont(QFont("Times New Roman", 14))
            nombre_label.setFixedSize(200, 200)  # Establece el tamaño deseado

            # Agrega una imagen desde la URL obtenida del diccionario de piloto.
            # Agrega manejo de errores al cargar imágenes.
            imagen_url = piloto["imagen_url"]
            if imagen_url:
                response = requests.get(imagen_url)
                imagen_data = response.content
                pixmap = QPixmap()
                pixmap.loadFromData(imagen_data)
                pixmap = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)  # Ajusta el tamaño de la imagen
                imagen_label = QLabel(self)
                imagen_label.setPixmap(pixmap)
                imagen_label.setFixedSize(200, 200)  # Establece el tamaño deseado

            card_layout.addWidget(imagen_label)
            card_layout.addWidget(nombre_label)
            card_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

            scroll_layout.addWidget(card_widget)

        scroll_area.setWidget(scroll_widget)

        # Crea un botón para cerrar la ventana.
        boton_cerrar = QPushButton("Cerrar", central_widget)
        boton_cerrar.clicked.connect(self.close)

        central_layout.addWidget(scroll_area)
        central_layout.addWidget(boton_cerrar)
        central_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.setCentralWidget(central_widget)

def obtener_pilotos():
    """Obtiene la clasificación de pilotos de Fórmula 1 de la API de ergast, incluyendo sus imágenes desde un archivo.

    Devuelve:
        Una lista de diccionarios, donde cada diccionario contiene la información de un piloto.
    """
    # Obtener los datos de la clasificación de pilotos desde la API de ergast.
    response_clasificacion = requests.get("http://ergast.com/api/f1/current/driverStandings.json")
    datos_clasificacion = response_clasificacion.json()

    # Obtener los datos de los pilotos desde la API de ergast.
    response_pilotos = requests.get("http://ergast.com/api/f1/current/drivers.json")
    datos_pilotos = response_pilotos.json()
    
    pilotos = []

    # Leer las URLs de las imágenes desde el archivo drivers_img.txt.
    with open("Resources/drivers_img.txt", "r") as archivo:
        lineas = archivo.readlines()

    if "MRData" in datos_clasificacion and "StandingsTable" in datos_clasificacion["MRData"]:
        standings = datos_clasificacion["MRData"]["StandingsTable"]["StandingsLists"]
        if standings:
            pilotos_data = standings[0]["DriverStandings"]

            for i, piloto_data in enumerate(pilotos_data):
                piloto = {
                    "posicion": piloto_data["position"],
                    "nombre": piloto_data["Driver"]["givenName"],
                    "apellido": piloto_data["Driver"]["familyName"],
                    "puntos": piloto_data["points"],
                    "imagen_url": "https://media.formula1.com/content/dam/fom-website/drivers/2023Drivers/"+piloto_data["Driver"]["familyName"]+".jpg.img.512.large.jpg"
                }

                # Verificar si hay una URL en el archivo y asignarla al diccionario del piloto.
                #if i < len(lineas):
                #   piloto["imagen_url"] = lineas[i].strip()

                pilotos.append(piloto)

    return pilotos

if __name__ == '__main__':
    app = QApplication(sys.argv)
    myApp = Pilotos()
    myApp.show()
    sys.exit(app.exec())
