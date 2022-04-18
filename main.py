from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget
from PyQt6 import uic
import sys
import os
import requests
from random import randint
import subprocess
#Setup
subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "req.txt"])

dir_path = os.path.dirname(os.path.realpath(__file__))
class messagesPage(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self):
        super().__init__()
        uic.loadUi(dir_path+'/frames/messagePage.ui', self)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.w = None  # No external window yet.
        uic.loadUi(dir_path+'/frames/loginPage.ui', self)
        self.loginBtn.clicked.connect(self.login)

    def openWindow(self, window):
        if self.w is None:
            self.w = window()
            self.w.show()

    def sendServerRequest(self, place, request):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0',
        }

        pload = {'request':request, 'user':self.usernameInput.text(), 'pass':self.passwordInput.text()}
        r = requests.post('https://www.quackyos.com/QuackShack/' + place, data=pload, headers=headers)
        output = str(r.text)
        return output

    def login(self):
        if (self.usernameInput.text() != '' and self.passwordInput.text() != ''):
            if (self.sendServerRequest('backend/login.php', '') == "Logged In"):
                print('Change Page')
                self.hide()
                self.openWindow(messagesPage)
            else:
                print('Alert user failed login')


app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec()