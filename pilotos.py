import sys
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QWidget, QLabel, QScrollArea, QVBoxLayout, QPushButton, QDialog, QTextEdit
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
from bs4 import BeautifulSoup

class DetallesPiloto(QDialog):
    def __init__(self, piloto_info):
        super().__init__()

        self.setWindowTitle(f"Detalles de {piloto_info['nombre']} {piloto_info['apellido']}")
        self.setGeometry(100, 100, 1000, 400)  # Modifica el tamaño de la ventana
        layout = QHBoxLayout(self)



        # Agrega la imagen del piloto en un QLabel
        imagen_url = piloto_info["imagen_url"]
        if imagen_url:
            response = requests.get(imagen_url)
            imagen_data = response.content
            pixmap = QPixmap()
            pixmap.loadFromData(imagen_data)
            if not pixmap.isNull():
                imagen_label = QLabel(self)
                pixmap = pixmap.scaled(200,200,Qt.AspectRatioMode.KeepAspectRatio)
                imagen_label.setPixmap(pixmap)
                imagen_label.setAlignment(Qt.AlignmentFlag.AlignTop)
                imagen_label.setScaledContents(True)
                layout.addWidget(imagen_label)

        # Ajusta el tamaño del cuadro de texto y la distancia entre elementos
        textedit_width = 500
        textedit_height = 300
        spacing = 20

        # Agrega una QVBoxLayout para el resto de la información
        info_layout = QVBoxLayout()

        # Agrega información detallada sobre el piloto en etiquetas
        nombre_label = QLabel(f"Nombre: {piloto_info['nombre']} {piloto_info['apellido']}")
        puntos_label = QLabel(f"Puntos: {piloto_info['puntos']}")
        titulos_label = QLabel(f"Títulos Mundiales: {piloto_info['titulos_mundiales']}")

        # Agrega una etiqueta para la biografía
        biografia_label = QLabel("Biografía:")

        # Obtén la biografía del piloto desde Wikipedia
        biografia_texto = self.obtener_biografia_wikipedia(piloto_info)

        # Agrega un QTextEdit para mostrar la biografía con un tamaño ajustado
        biografia_textedit = QTextEdit()
        biografia_textedit.setPlainText(biografia_texto)
        biografia_textedit.setReadOnly(True)
        biografia_textedit.setMaximumSize(textedit_width, textedit_height)

        info_layout.addWidget(nombre_label)
        info_layout.addWidget(puntos_label)
        info_layout.addWidget(titulos_label)
        info_layout.addWidget(biografia_label)
        info_layout.addWidget(biografia_textedit)
        info_layout.addSpacing(spacing)

        # Ajusta el tamaño del layout de información y agrega el layout a la derecha de la imagen
        info_layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(info_layout)

        # Agrega el layout de información a la derecha de la imagen
        layout.addLayout(info_layout)

    def closeEvent(self, event):
        # Esta función se llama cuando se cierra la ventana de detalles
        event.accept()
    def obtener_biografia_wikipedia(self, piloto_info):
        # Ajustar el apellido para los casos específicos
        if piloto_info['apellido'] == 'Sainz':
            piloto_info['apellido'] = 'Sainz_Jr.'
        elif piloto_info['apellido'] == 'Russell':
            piloto_info['apellido'] = 'Russell_(piloto)'
        # Obtener la URL de la página de Wikipedia del piloto
        url_wikipedia = f"https://es.wikipedia.org/wiki/{piloto_info['nombre']}_{piloto_info['apellido']}"
        response_wikipedia = requests.get(url_wikipedia)

        if response_wikipedia.status_code == 200:
            html = response_wikipedia.text

            # Utilizar BeautifulSoup para analizar el HTML y extraer el texto de la introducción
            soup = BeautifulSoup(html, 'html.parser')

            # Encuentra el primer párrafo dentro de la clase "mw-parser-output"
            primer_parrafo = soup.find('div', {'class': 'mw-parser-output'}).find('p')

            # Si se encuentra el primer párrafo, obtén su texto
            if primer_parrafo:
                biografia_texto = primer_parrafo.text
            else:
                biografia_texto = "Información no disponible en Wikipedia."

            return biografia_texto
        else:
            return "Error al obtener la información desde Wikipedia."

class Pilotos(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Lista de Pilotos de Fórmula 1")
        self.setGeometry(100, 100, 500, 720)
        self.setMinimumSize(500, 720)  # Establece el tamaño mínimo de la ventana
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
            nombre_label = QLabel(f"{piloto['nombre']} {piloto['apellido']}\nPuntos: {piloto['puntos']}\nPosición: {piloto['posicion']}\nTítulos: {piloto['titulos_mundiales']}")
            nombre_label.setFont(QFont("Times New Roman", 14))

            # Agrega una imagen desde la URL obtenida del diccionario de piloto.
            # Agrega manejo de errores al cargar imágenes.
            imagen_url = piloto["imagen_url"]
            if imagen_url:
                response = requests.get(imagen_url)
                imagen_data = response.content
                pixmap = QPixmap()
                pixmap.loadFromData(imagen_data)
                if pixmap.isNull():
                    pixmap2 = QPixmap('Resources/Unknown.png')
                    pixmap2 = pixmap2.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)  # Ajusta el tamaño de la imagen
                    imagen_label = QLabel(self)
                    imagen_label.setPixmap(pixmap2)
                    imagen_label.setAlignment(Qt.AlignmentFlag.AlignTop)  # Alinear la imagen en la parte superior
                    imagen_label.setScaledContents(True)  # Permitir escalar el contenido de la etiqueta
                else:
                    pixmap = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)  # Ajusta el tamaño de la imagen
                    imagen_label = QLabel(self)
                    imagen_label.setPixmap(pixmap)
                    imagen_label.setAlignment(Qt.AlignmentFlag.AlignTop)  # Alinear la imagen en la parte superior
                    imagen_label.setScaledContents(True)  # Permitir escalar el contenido de la etiqueta
                """Opcion 2, tamaño de imagen estatico pero creo que queda mejor
                #response = requests.get(imagen_url)
                #imagen_data = response.content
                #pixmap = QPixmap()
                #pixmap.loadFromData(imagen_data)
                #pixmap = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)  # Ajusta el tamaño de la imagen
                imagen_label = QLabel(self)
                imagen_label.setPixmap(pixmap)
                imagen_label.setFixedSize(200, 200)  # Establece el tamaño deseado
                """

                
            card_layout.addWidget(imagen_label)
            card_layout.addWidget(nombre_label)
            card_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            card_widget.mousePressEvent = lambda event, piloto=piloto: self.mostrar_detalles(piloto)

            scroll_layout.addWidget(card_widget)

        scroll_area.setWidget(scroll_widget)

        # Crea un botón para cerrar la ventana.
        boton_cerrar = QPushButton("Cerrar", central_widget)
        boton_cerrar.clicked.connect(self.close)

        central_layout.addWidget(scroll_area)
        central_layout.addWidget(boton_cerrar)
        central_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.setCentralWidget(central_widget)

    def mostrar_detalles(self, piloto_info):
        detalles_window = DetallesPiloto(piloto_info)
        detalles_window.exec_()

def obtener_pilotos():
    # Obtener los datos de la clasificación de pilotos desde la API de ergast.
    response_clasificacion = requests.get("http://ergast.com/api/f1/current/driverStandings.json")
    datos_clasificacion = response_clasificacion.json()

    # Obtener los datos de los pilotos desde la API de ergast.
    response_pilotos = requests.get("http://ergast.com/api/f1/current/drivers.json")
    datos_pilotos = response_pilotos.json()

    pilotos = []

    if "MRData" in datos_clasificacion and "StandingsTable" in datos_clasificacion["MRData"]:
        standings = datos_clasificacion["MRData"]["StandingsTable"]["StandingsLists"]
        if standings:
            pilotos_data = standings[0]["DriverStandings"]

            for i, piloto_data in enumerate(pilotos_data):
                # Obtener información adicional de cada piloto usando la API de Ergast Developer.
                url_detallada = f"http://ergast.com/api/f1/drivers/{piloto_data['Driver']['driverId']}.json"
                response_detallada = requests.get(url_detallada)
                datos_detallados = response_detallada.json()

                # Obtener la cantidad de victorias.
                url_victorias = f"http://ergast.com/api/f1/drivers/{piloto_data['Driver']['driverId']}/results.json?limit=1000"
                response_victorias = requests.get(url_victorias)
                datos_victorias = response_victorias.json()

                victorias = sum(result.get("position", "") == "1" for result in datos_victorias.get("MRData", {}).get("RaceTable", {}).get("Races", []))

                # Obtener la cantidad de títulos mundiales.
                url_titulos_mundiales = f"http://ergast.com/api/f1/drivers/{piloto_data['Driver']['driverId']}/driverStandings/1.json"
                response_titulos_mundiales = requests.get(url_titulos_mundiales)
                datos_titulos_mundiales = response_titulos_mundiales.json()

                titulos_mundiales = len(datos_titulos_mundiales.get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", []))

                piloto = {
                    "posicion": piloto_data["position"],
                    "nombre": piloto_data["Driver"]["givenName"],
                    "apellido": piloto_data["Driver"]["familyName"],
                    "puntos": piloto_data["points"],
                    "imagen_url": f"https://media.formula1.com/content/dam/fom-website/drivers/2023Drivers/{piloto_data['Driver']['familyName']}.jpg.img.512.large.jpg",
                    "titulos_mundiales": titulos_mundiales
                }

                pilotos.append(piloto)

    return pilotos


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myApp = Pilotos()
    myApp.show()
    sys.exit(app.exec())
