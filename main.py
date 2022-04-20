from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QTextEdit
from PyQt6 import uic
from PyQt6.QtCore import Qt
import sys
import os
import requests
from random import randint
import subprocess
#Setup
subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "req.txt"])

dir_path = os.path.dirname(os.path.realpath(__file__))

class working():
    username = ''
    password = ''
    messageCount = 0
    maxMessages= 21
    maxOneRow = 7

    def sendServerRequest(place, request, username, password):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0',
        }

        pload = {'request':request, 'user':username, 'pass':password}
        r = requests.post('https://www.quackyos.com/QuackShack/' + place, data=pload, headers=headers)
        output = str(r.text)
        return output

class messagesPage(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self):
        super().__init__()
        
        uic.loadUi(dir_path+'/frames/messagePage.ui', self)

        # Split messages up into sperate objects
        messages = working.sendServerRequest('backend/getMessages.php','getMessages', working.username, working.password).split("<br>")
        labelPlaceColum = -1
        row = 0
        layoutCheck = 0
        
        # Math bullshit
        # Bassically loop however many times there are messages
        for i in messages:
            # This is to keep track of current amount of messages
            working.messageCount += 1
            # Only allow x amount of messages to be displayed
            if (working.messageCount <= working.maxMessages):
                # Allow 4 messages in one row
                if (layoutCheck == working.maxOneRow):
                    # Change row
                    row += 1
                    # reset vars
                    layoutCheck = 0
                    labelPlaceColum = -1
                layoutCheck += 1
                # Increase colum pos
                labelPlaceColum += 1
                # Create messages and set text
                messageArea = QTextEdit()
                messageArea.setText(i)
                messageArea.setReadOnly(True)

                # Add messages to grid
                self.gridLayout.addWidget(messageArea, row, labelPlaceColum)

        self.showFullScreen()


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

    def login(self):
        if (self.usernameInput.text() != '' and self.passwordInput.text() != ''):
            if (working.sendServerRequest('backend/login.php', '', self.usernameInput.text(), self.passwordInput.text()) == "Logged In"):
                print('Change Page')
                working.username = self.usernameInput.text()
                working.password = self.passwordInput.text()
                self.hide()
                self.openWindow(messagesPage)
            else:
                print('Alert user failed login')


app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec()