import subprocess
import sys
#Setup
subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "req.txt"])

from threading import Thread
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QTextEdit
from PyQt6 import uic
from PyQt6.QtCore import QTimer
import os
import requests
from pydub import AudioSegment
from pydub.playback import play
from time import sleep

dir_path = os.path.dirname(os.path.realpath(__file__))

# Main functions go here
class working():
    # GUI Controls
    maxMessages= 12
    maxOneRow = 4
    messagesMaxHeight = 400
    messagesMaxWidth = 400

    # Other Shit
    username = ''
    password = ''

    charSplit = '|**|\/|**|'

    messageCountTemp = 0
    messageCountLock = False

    idTemp = 0
    idCurrent = 0
    idCounter = 0

    def sendServerRequest(place, request, username, password, amountOfMessages):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0',
        }

        pload = {'request':request, 'user':username, 'pass':password, 'maxMessages':amountOfMessages}
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
        
        uic.loadUi(dir_path+'/res/frames/messagePage.ui', self)

        # Setup updater
        self.updateMessages=QTimer()
        self.updateMessages.timeout.connect(self.createMessages)

        # Start updating messages
        self.updateMessages.start(5000)

        self.showFullScreen()
        

    def createMessages(self):
        # Split messages up into sperate objects
        messages = working.sendServerRequest('backend/getMessages.php','getMessages', working.username, working.password, working.maxMessages).split(working.charSplit)
        colum = -1
        row = 0
        layoutCheck = 0
        
        # Math bullshit
        # Bassically loop however many times there are messages
        for i in messages:
            # Gets current post it ID
            working.idCounter = i.split('<br>')[0]
            if (working.messageCountTemp == 0):
                working.idCurrent = working.idCounter
            
            # If new ID is added then execute message stuff and check if there is anything in DB
            if (working.idCurrent != working.idTemp and working.idCurrent != ""):
                #--------Create Messages--------
                # Allow x amount of messages in one row
                if (layoutCheck == working.maxOneRow):
                    # Change row
                    row += 1
                    # reset vars
                    layoutCheck = 0
                    colum = -1
                layoutCheck += 1
                # Increase colum pos
                colum += 1
                # Create messages and set props
                messageArea = QTextEdit()
                messageArea.setText(i)
                messageArea.setReadOnly(True)
                messageArea.setStyleSheet('background-color: rgb(209, 183, 15); padding-top: 10px; border-top: 50px solid; border-top-color: rgb(158, 158, 158);')
                messageArea.setMaximumHeight(working.messagesMaxHeight)
                messageArea.setMaximumWidth(working.messagesMaxWidth)

                # Add messages to grid
                self.gridLayout.addWidget(messageArea, row, colum)

                #------------------------------

                    
            working.messageCountTemp += 1

        # Check if theres any messages
        if (working.messageCountLock):
            # Prevent range error
            if (working.idTemp == "" or working.idCurrent == ""):
                working.idTemp = 0
                working.idCurrent = 0
            # This is a queue for the sound effect
            for x in range(int(working.idTemp), int(working.idCurrent)):
                # Alert if new message comes in
                alert = AudioSegment.from_mp3(dir_path + "/res/sounds/quack.mp3")
                play(alert)

        # Reset Stuff
        working.messageCountLock = True
        working.messageCountTemp = 0

        # Sets the temp id last so it can check the current id first
        if (working.messageCountTemp == 0):
            working.idTemp = working.idCurrent
        

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.w = None  # No external window yet.
        uic.loadUi(dir_path+'/res/frames/loginPage.ui', self)
        self.loginBtn.clicked.connect(self.login)

    def openWindow(self, window):
        if self.w is None:
            self.w = window()
            self.w.show()

    def login(self):
        if (self.usernameInput.text() != '' and self.passwordInput.text() != ''):
            if (working.sendServerRequest('backend/login.php', '', self.usernameInput.text(), self.passwordInput.text(), '') == "Logged In"):
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