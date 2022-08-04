import sys
import RPi.GPIO as GPIO
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.window = None
        GPIO.setmode(GPIO.BOARD)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.mainApp()

    def mainApp(self):
        self.window = uic.loadUi('ui/main.ui', self)
        self.window.testButton = self.findChild(QPushButton, 'testButton')
        self.window.testButton.pressed.connect(self.sendSignal)
        self.window.testButton.released.connect(self.stopSendSignal)

    @staticmethod
    def sendSignal():
        GPIO.output(13, True)

    @staticmethod
    def stopSendSignal():
        GPIO.output(13, False)


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.showFullScreen()
    app.exec_()


if __name__ == '__main__':
    main()
