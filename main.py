from concurrent.futures import thread
import subprocess
import sys
#Setup
subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "req.txt"])


import platform
machineOs = platform.system()
if (machineOs == 'Darwin' or machineOs == 'Linux'):
    from pydub import AudioSegment
    from pydub.playback import play
else:
    from audioplayer import AudioPlayer

from threading import Thread
from gtts import gTTS
import os
import requests
from time import sleep
# PyQt Libs
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QTextEdit, QPushButton
from PyQt6 import uic
from PyQt6.QtCore import QThread, pyqtSlot, QObject, pyqtSignal, Qt

dir_path = os.path.dirname(os.path.realpath(__file__))

# Main functions go here
class working():
    # GUI Controls
    maxOneRow = 4
    maxOneColum = 3
    maxMessages= maxOneRow*maxOneColum
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

    queueCounter = 0
    messageQueue = []
    messageFunction = ''

    def sendServerRequest(place, request, username, password, amountOfMessages):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0',
        }

        pload = {'request':request, 'user':username, 'pass':password, 'maxMessages':amountOfMessages}
        r = requests.post('https://www.quackyos.com/QuackShack/' + place, data=pload, headers=headers)
        output = str(r.text)
        return output

class checkMessagesThreaded(QObject):
    def __init__(self, signal_to_emit, parent=None):
        super().__init__(parent)
        self.signal_to_emit = signal_to_emit

    @pyqtSlot()
    def executeThread( self ):
        while True:
            print('Slot doing stuff in:', QThread.currentThread())
            sleep(5)

            try:
                # Split messages up into sperate objects
                messages = working.sendServerRequest('backend/getMessages.php','getMessages', working.username, working.password, working.maxMessages).split(working.charSplit)
                
                # Math bullshit
                # Bassically loop however many times there are messages
                for i in messages:
                    # check if there is anything in DB
                    if (len(i) != 0):
                        # Gets current post it ID
                        working.idCounter = i.split('|')[0]
                        working.messageFunction = i.split('|')[3]
                        if (working.messageCountTemp == 0):
                            working.idCurrent = working.idCounter

                        messagesLeft = int(working.idCurrent) - int(working.idTemp)
                        print(messagesLeft)
                        if (messagesLeft != 0):
                            # If new ID is added then execute message stuff
                            while working.queueCounter < int(working.idCurrent) - int(working.idTemp) and working.messageCountLock:
                                working.messageQueue.insert(0, working.messageFunction)
                                
                                self.signal_to_emit.emit(str(i))
                                working.queueCounter += 1
                                break
                                
                        working.messageCountTemp += 1

                # Check if theres any messages
                if (working.messageCountLock):
                    # Prevent range error
                    if (working.idTemp == "" or working.idCurrent == ""):
                        working.idTemp = 0
                        working.idCurrent = 0
                    # This is a queue for the sound effect
                    for x in range(0, len(working.messageQueue)):
                        # Alert if new message comes in
                        audioThread= Thread(target=audioPlayer.playSound(working.messageQueue[x]))
                        audioThread.start()
                    working.messageQueue = []

                # Reset Stuff
                working.messageCountLock = True
                working.messageCountTemp = 0
                working.queueCounter = 0

                # Sets the temp id last so it can check the current id first
                if (working.messageCountTemp == 0):
                    working.idTemp = working.idCurrent
            except Exception as e:
                print("Create Message Error: " + str(e))

class audioPlayer():
    def playSound(sound):
        try:
            if (machineOs == 'Darwin' or machineOs == 'Linux'):
                alert = AudioSegment.from_mp3(dir_path + "/res/sounds/" + sound)
                play(alert)
            else:
                AudioPlayer(dir_path + "/res/sounds/" + sound).play(block=True)
        except Exception as e:
            print('Playsound Error: ' + str(e))

class messagesPage(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    sig = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        
        uic.loadUi(dir_path+'/res/frames/messagePage.ui', self)

        self.showFullScreen()

        # Start thread button
        self.startMessageThreadButton = QPushButton()
        self.startMessageThreadButton.setStyleSheet("QPushButton"
                             "{"
                             "background-color : lightgreen;"
                             "}"
                             "QPushButton::pressed"
                             "{"
                             "background-color : red;"
                             "}")
        self.gridLayout.addWidget(self.startMessageThreadButton)
        
        self.colum = -1
        self.row = 0
        self.layoutCheck = 0

        self.worker = checkMessagesThreaded(self.sig)
        thread = QThread(self) 
        self.worker.moveToThread(thread)
        thread.start()
        self.startMessageThreadButton.clicked.connect(self.worker.executeThread)
        self.sig.connect(self.createMessages)

    @pyqtSlot(str)
    def createMessages(self, text):
        print('Creating Messages')

        # Allow x amount of messages in one row
        if (self.layoutCheck == working.maxOneRow):
            # Change row
            self.row += 1
            
            # reset vars
            self.layoutCheck = 0
            self.colum = -1
        if (self.row == working.maxOneColum):
            # reset vars
            self.layoutCheck = 0
            self.row = 0
        self.layoutCheck += 1
        # Increase colum pos
        self.colum += 1
        # Create messages and set props
        self.messageArea = QTextEdit()
        self.messageArea.setReadOnly(True)
        self.messageArea.setStyleSheet('background-color: rgb(209, 183, 15); padding-top: 10px; border-top: 50px solid; border-top-color: rgb(158, 158, 158);')
        self.messageArea.setMaximumHeight(working.messagesMaxHeight)
        self.messageArea.setMaximumWidth(working.messagesMaxWidth)
        # Add messages to grid
        self.messageArea.setText(text)
        self.gridLayout.addWidget(self.messageArea, self.row, self.colum)
        

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