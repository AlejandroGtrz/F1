# Form implementation generated from reading ui file 'inicio.ui'
#
# Created by: PyQt6 UI code generator 6.2.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets

from telemetria import Ui_wAnios

class Ui_wInicio(object):
    def setupUi(self, wInicio):
        wInicio.setObjectName("wInicio")
        wInicio.resize(520, 160)
        self.centralwidget = QtWidgets.QWidget(wInicio)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 50, 491, 51))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.bAnio = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.bAnio.setObjectName("bAnio")
        self.horizontalLayout_2.addWidget(self.bAnio)
        self.bPiloto = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.bPiloto.setObjectName("bPiloto")
        self.horizontalLayout_2.addWidget(self.bPiloto)
        self.bCircuito = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.bCircuito.setObjectName("bCircuito")
        self.horizontalLayout_2.addWidget(self.bCircuito)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 20, 121, 16))
        self.label.setObjectName("label")
        wInicio.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(wInicio)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 520, 22))
        self.menubar.setObjectName("menubar")
        wInicio.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(wInicio)
        self.statusbar.setObjectName("statusbar")
        wInicio.setStatusBar(self.statusbar)

        self.retranslateUi(wInicio)
        QtCore.QMetaObject.connectSlotsByName(wInicio)

        self.bAnio.clicked.connect(self.telemetria)
        

    def telemetria(self):
        self.wAnios = QtWidgets.QMainWindow()
        self.ui = Ui_wAnios()
        self.ui.setupUi(self.wAnios)
        self.wAnios.show()
    def retranslateUi(self, wInicio):
        _translate = QtCore.QCoreApplication.translate
        wInicio.setWindowTitle(_translate("wInicio", "Inicio"))
        self.bAnio.setText(_translate("wInicio", "Por año"))
        self.bPiloto.setText(_translate("wInicio", "Por piloto"))
        self.bCircuito.setText(_translate("wInicio", "Por circuito"))
        self.label.setText(_translate("wInicio", "Tipo de busqueda"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    wInicio = QtWidgets.QMainWindow()
    ui = Ui_wInicio()
    ui.setupUi(wInicio)
    wInicio.show()
    sys.exit(app.exec())