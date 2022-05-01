import sys
from PyQt6 import QtWidgets,QtGui,QtCore
from PyQt6.QtWebEngineWidgets import *
app=QtWidgets.QApplication(sys.argv)
w=QWebEngineView()
w.load(QtCore.QUrl('https://quackyos.com')) ## load google on startup
w.showMaximized()
app.exec()