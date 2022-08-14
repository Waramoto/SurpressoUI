import sys
import RPi.GPIO as GPIO
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QPushButton, QLabel
from functools import partial


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(13, GPIO.OUT)
        super(Ui, self).__init__()
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.background = uic.loadUi('ui/background.ui', self)
        self.showFullScreen()
        self.timerLogo = QTimer(self)
        self.timerTouch = QTimer(self)
        self.timerOneCup = QTimer(self)
        self.timerTwoCups = QTimer(self)
        self.timerLogo.setInterval(3000)
        self.timerTouch.setInterval(30000)
        self.timerOneCup.setInterval(30000)
        self.timerTwoCups.setInterval(30000)
        self.timerLogo.timeout.connect(self.mainApp)
        self.timerTouch.timeout.connect(self.touchButtonReleased)
        self.timerOneCup.timeout.connect(self.oneCupClick)
        self.timerTwoCups.timeout.connect(self.twoCupsClick)
        self.window = None
        self.oneCupClicked = False
        self.twoCupsClicked = False
        self.logoApp()

    def logoApp(self):
        super(Ui, self).__init__()
        self.window = uic.loadUi('ui/logo.ui', self)
        self.timerLogo.start()
        self.showFullScreen()

    def mainApp(self):
        self.timerLogo.stop()
        self.window.close()
        super(Ui, self).__init__()
        self.window = uic.loadUi('ui/main.ui', self)

        self.window.touchButton = self.findChild(QPushButton, 'touchButton')
        self.window.touchButton.pressed.connect(self.touchButtonPressed)
        self.window.touchButton.released.connect(self.touchButtonReleased)

        self.window.oneCupButton = self.findChild(QPushButton, 'oneCupButton')
        self.window.oneCupButton.clicked.connect(self.oneCupClick)

        self.window.twoCupsButton = self.findChild(QPushButton, 'twoCupsButton')
        self.window.twoCupsButton.clicked.connect(self.twoCupsClick)

        self.window.durationButton = self.findChild(QPushButton, 'durationButton')
        self.window.durationButton.clicked.connect(self.durationApp)

        self.window.clockButton = self.findChild(QPushButton, 'clockButton')

        self.window.languageButton = self.findChild(QPushButton, 'languageButton')

        self.showFullScreen()

    def durationApp(self):
        if self.oneCupClicked:
            self.oneCupClick()
        if self.twoCupsClicked:
            self.twoCupsClick()

        self.window.close()
        super(Ui, self).__init__()
        self.window = uic.loadUi('ui/duration.ui', self)

        self.window.backButton0 = self.findChild(QPushButton, 'backButton0')
        self.window.backButton0.clicked.connect(self.saveAndBack)

        self.window.plusButtons = []
        self.window.minusButtons = []
        self.window.numLabels = []

        for i in range(8):
            self.window.plusButtons.append(self.findChild(QPushButton, 'plusButton' + str(i)))
            self.window.minusButtons.append(self.findChild(QPushButton, 'minusButton' + str(i)))
            self.window.numLabels.append(self.findChild(QLabel, 'numLabel' + str(i)))
            self.window.plusButtons[i].clicked.connect(partial(self.increaseNum, self.window.numLabels[i]))
            self.window.minusButtons[i].clicked.connect(partial(self.decreaseNum, self.window.numLabels[i]))

        try:
            with open('config/duration.txt', 'r') as file:
                for i in range(8):
                    fr = file.read(1)
                    if fr.isnumeric():
                        if (i == 0 or i == 4) and int(fr) > 2:
                            raise FileNotFoundError
                        else:
                            self.window.numLabels[i].setText(fr)
                    else:
                        raise FileNotFoundError
        except FileNotFoundError:
            with open('config/duration.txt', 'w') as file:
                file.write('29992999')
            with open('config/duration.txt', 'r') as file:
                for i in range(8):
                    self.window.numLabels[i].setText(file.read(1))

        self.showFullScreen()

    def saveAndBack(self):
        with open('config/duration.txt', 'w') as file:
            for nl in self.window.numLabels:
                file.write(nl.text())
        self.mainApp()

    def touchButtonPressed(self):
        if self.twoCupsClicked:
            self.twoCupsClick()
        if self.oneCupClicked:
            self.oneCupClick()
        self.timerTouch.start()
        self.sendSignal()

    def touchButtonReleased(self):
        if self.timerTouch.isActive():
            self.timerTouch.stop()
            self.stopSendSignal()

    def oneCupClick(self):
        if self.twoCupsClicked:
            self.twoCupsClick()
        self.oneCupClicked = not self.oneCupClicked
        if self.oneCupClicked:
            t = ''
            try:
                with open('config/duration.txt', 'r') as file:
                    for i in range(4):
                        fr = file.read(1)
                        if fr.isnumeric():
                            if i == 0 and int(fr) > 2:
                                raise FileNotFoundError
                            else:
                                t += fr
                        else:
                            raise FileNotFoundError
            except FileNotFoundError:
                with open('config/duration.txt', 'w') as file:
                    file.write('29992999')
                t = '2999'
            self.timerOneCup.setInterval(int(t) * 10)
            self.timerOneCup.start()
            self.sendSignal()
        else:
            self.timerOneCup.stop()
            self.stopSendSignal()

    def twoCupsClick(self):
        if self.oneCupClicked:
            self.oneCupClick()
        self.twoCupsClicked = not self.twoCupsClicked
        if self.twoCupsClicked:
            t = ''
            try:
                with open('config/duration.txt', 'r') as file:
                    for i in range(4):
                        file.read(1)
                    for i in range(4):
                        fr = file.read(1)
                        if fr.isnumeric():
                            if i == 0 and int(fr) > 2:
                                raise FileNotFoundError
                            else:
                                t += fr
                        else:
                            raise FileNotFoundError
            except FileNotFoundError:
                with open('config/duration.txt', 'w') as file:
                    file.write('29992999')
                t = '2999'
            self.timerTwoCups.setInterval(int(t) * 10)
            self.timerTwoCups.start()
            self.sendSignal()
        else:
            self.timerTwoCups.stop()
            self.stopSendSignal()

    @staticmethod
    def increaseNum(num_label):
        num = int(num_label.text())
        if num_label.objectName()[-1] == '0' or num_label.objectName()[-1] == '4':
            if num == 2:
                num = 0
            else:
                num += 1
        else:
            if num == 9:
                num = 0
            else:
                num += 1
        num_label.setText(str(num))

    @staticmethod
    def decreaseNum(num_label):
        num = int(num_label.text())
        if num_label.objectName()[-1] == '0' or num_label.objectName()[-1] == '4':
            if num == 0:
                num = 2
            else:
                num -= 1
        else:
            if num == 0:
                num = 9
            else:
                num -= 1
        num_label.setText(str(num))

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
