import sys
import RPi.GPIO as GPIO
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QPushButton, QLabel
from functools import partial
from datetime import datetime, timedelta


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(13, GPIO.OUT)

        super(Ui, self).__init__()
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.background = uic.loadUi('ui/background.ui', self)
        self.showFullScreen()

        self.timerMilliseconds = QTimer(self)
        self.timerSeconds = QTimer(self)
        self.timerLogo = QTimer(self)
        self.timerTouch = QTimer(self)
        self.timerOneCup = QTimer(self)
        self.timerTwoCups = QTimer(self)
        self.timerMilliseconds.setInterval(10)
        self.timerSeconds.setInterval(1000)
        self.timerLogo.setInterval(3000)
        self.timerTouch.setInterval(30000)
        self.timerOneCup.setInterval(30000)
        self.timerTwoCups.setInterval(30000)
        self.timerMilliseconds.timeout.connect(self.updateStopwatch)
        self.timerSeconds.timeout.connect(self.updateClock)
        self.timerLogo.timeout.connect(self.mainApp)
        self.timerTouch.timeout.connect(self.touchButtonReleased)
        self.timerOneCup.timeout.connect(self.oneCupClick)
        self.timerTwoCups.timeout.connect(self.twoCupsClick)
        self.window = None
        self.language = 0
        self.clock = 0
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
        self.timerSeconds.start()

        self.window.close()
        super(Ui, self).__init__()
        self.window = uic.loadUi('ui/main.ui', self)

        self.window.timeLabel = self.findChild(QLabel, 'timeLabel')

        self.window.clockButton = self.findChild(QPushButton, 'clockButton')
        self.window.clockButton.setText((datetime.now() + timedelta(seconds=self.clock)).strftime('%H:%M:%S'))

        self.window.touchButton = self.findChild(QPushButton, 'touchButton')
        self.window.touchButton.pressed.connect(self.touchButtonPressed)
        self.window.touchButton.released.connect(self.touchButtonReleased)

        self.window.oneCupButton = self.findChild(QPushButton, 'oneCupButton')
        self.window.oneCupButton.clicked.connect(self.oneCupClick)
        if self.oneCupClicked:
            self.window.oneCupButton.setStyleSheet('QPushButton {'
                                                   'background-color: rgb(235, 235, 235);'
                                                   'color: rgb(0, 0, 0); border-radius:  80px;'
                                                   'border-style: solid; border-width: 15px;'
                                                   'border-color: rgb(254, 205, 84);'
                                                   '}')

        self.window.twoCupsButton = self.findChild(QPushButton, 'twoCupsButton')
        self.window.twoCupsButton.clicked.connect(self.twoCupsClick)
        if self.twoCupsClicked:
            self.window.twoCupsButton.setStyleSheet('QPushButton {'
                                                    'background-color: rgb(235, 235, 235);'
                                                    'color: rgb(0, 0, 0); border-radius:  80px;'
                                                    'border-style: solid; border-width: 15px;'
                                                    'border-color: rgb(254, 205, 84);'
                                                    '}')

        self.window.durationButton = self.findChild(QPushButton, 'durationButton')
        self.window.durationButton.clicked.connect(self.durationApp)

        self.window.clockButton = self.findChild(QPushButton, 'clockButton')
        self.window.clockButton.clicked.connect(self.clockApp)

        self.window.languageButton = self.findChild(QPushButton, 'languageButton')
        self.window.languageButton.clicked.connect(self.languageApp)

        self.getClock()
        self.getLanguage()
        if self.language == 1:
            self.window.languageButton.setText('EN')
        elif self.language == 2:
            self.window.languageButton.setText('RU')
        else:
            self.window.languageButton.setText('UA')

        self.showFullScreen()

    def durationApp(self):
        self.timerSeconds.stop()

        self.window.close()
        super(Ui, self).__init__()
        self.window = uic.loadUi('ui/duration.ui', self)

        self.window.grindingDurationLabel = self.findChild(QLabel, 'grindingDurationLabel')

        self.window.singleServingLabel = self.findChild(QLabel, 'singleServingLabel')

        self.window.doubleServingLabel = self.findChild(QLabel, 'doubleServingLabel')

        self.window.numLabels = []

        self.window.backButton0 = self.findChild(QPushButton, 'backButton0')
        self.window.backButton0.clicked.connect(self.saveDurAndBack)

        self.window.plusButtons = []

        self.window.minusButtons = []

        for i in range(8):
            self.window.plusButtons.append(self.findChild(QPushButton, 'plusButton' + str(i)))
            self.window.minusButtons.append(self.findChild(QPushButton, 'minusButton' + str(i)))
            self.window.numLabels.append(self.findChild(QLabel, 'numLabel' + str(i)))
            self.window.plusButtons[i].clicked.connect(partial(self.increaseNumDur, self.window.numLabels[i]))
            self.window.minusButtons[i].clicked.connect(partial(self.decreaseNumDur, self.window.numLabels[i]))

        self.getLanguage()
        if self.language == 1:
            self.window.grindingDurationLabel.setText('Grinding duration')
            self.window.singleServingLabel.setText('Single serving')
            self.window.doubleServingLabel.setText('Double serving')
        elif self.language == 2:
            self.window.grindingDurationLabel.setText('Длительность помола')
            self.window.singleServingLabel.setText('Одинарная порция')
            self.window.doubleServingLabel.setText('Двойная порция')
        else:
            self.window.grindingDurationLabel.setText('Тривалість помолу')
            self.window.singleServingLabel.setText('Одинарна порція')
            self.window.doubleServingLabel.setText('Подвійна порція')

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

    def languageApp(self):
        self.timerSeconds.stop()

        self.window.close()
        super(Ui, self).__init__()
        self.window = uic.loadUi('ui/language.ui', self)

        self.window.languageChangeLabel = self.findChild(QLabel, 'languageChangeLabel')

        self.window.backButton2 = self.findChild(QPushButton, 'backButton2')
        self.window.backButton2.clicked.connect(self.mainApp)

        self.window.UAButton = self.findChild(QPushButton, 'UAButton')
        self.window.UAButton.clicked.connect(partial(self.setLanguage, '0'))

        self.window.ENButton = self.findChild(QPushButton, 'ENButton')
        self.window.ENButton.clicked.connect(partial(self.setLanguage, '1'))

        self.window.RUButton = self.findChild(QPushButton, 'RUButton')
        self.window.RUButton.clicked.connect(partial(self.setLanguage, '2'))

        self.getLanguage()
        if self.language == 1:
            self.window.languageChangeLabel.setText('Switch language')
        elif self.language == 2:
            self.window.languageChangeLabel.setText('Смена языка')
        else:
            self.window.languageChangeLabel.setText('Зміна мови')

        self.showFullScreen()

    def clockApp(self):
        self.timerSeconds.stop()

        self.window.close()
        super(Ui, self).__init__()
        self.window = uic.loadUi('ui/clock.ui', self)

        self.window.timeSettingsLabel = self.findChild(QLabel, 'timeSettingsLabel')

        self.window.numLabels1 = []

        self.window.backButton1 = self.findChild(QPushButton, 'backButton1')
        self.window.backButton1.clicked.connect(self.saveClockAndBack)

        self.window.plusButtons1 = []

        self.window.minusButtons1 = []

        t = (datetime.now() + timedelta(seconds=self.clock)).strftime('%H%M%S')
        for i in range(6):
            self.window.plusButtons1.append(self.findChild(QPushButton, 'plusButton1' + str(i)))
            self.window.minusButtons1.append(self.findChild(QPushButton, 'minusButton1' + str(i)))
            self.window.numLabels1.append(self.findChild(QLabel, 'numLabel1' + str(i)))
            self.window.plusButtons1[i].clicked.connect(partial(self.increaseNumClock, self.window.numLabels1[i]))
            self.window.minusButtons1[i].clicked.connect(partial(self.decreaseNumClock, self.window.numLabels1[i]))
            self.window.numLabels1[i].setText(t[i])

        self.getLanguage()
        if self.language == 1:
            self.window.timeSettingsLabel.setText('Time settings')
        elif self.language == 2:
            self.window.timeSettingsLabel.setText('Настройка времени')
        else:
            self.window.timeSettingsLabel.setText('Налаштування часу')

        self.showFullScreen()

    def getLanguage(self):
        try:
            with open('config/language.txt', 'r') as file:
                fr = file.read(1)
                if fr.isnumeric() and int(fr) < 3:
                    self.language = int(fr)
                else:
                    raise FileNotFoundError
        except FileNotFoundError:
            with open('config/language.txt', 'w') as file:
                file.write('0')
            self.language = 0

    def setLanguage(self, lang):
        with open('config/language.txt', 'w') as file:
            file.write(lang)
        if lang == '1':
            self.window.languageChangeLabel.setText('Switch language')
        elif lang == '2':
            self.window.languageChangeLabel.setText('Смена языка')
        else:
            self.window.languageChangeLabel.setText('Зміна мови')

    def getClock(self):
        try:
            with open('config/clock.txt', 'r') as file:
                fr = file.read()
                if fr.isnumeric() and 0 <= int(fr) < 86400:
                    self.clock = int(fr)
                else:
                    raise FileNotFoundError
        except FileNotFoundError:
            with open('config/clock.txt', 'w') as file:
                file.write('0')
            self.clock = 0

    def updateClock(self):
        self.window.clockButton.setText((datetime.now() + timedelta(seconds=self.clock)).strftime('%H:%M:%S'))

    def saveDurAndBack(self):
        with open('config/duration.txt', 'w') as file:
            for nl in self.window.numLabels:
                file.write(nl.text())
        self.mainApp()

    def saveClockAndBack(self):
        t0 = ''
        for nl in self.window.numLabels1:
            t0 += nl.text()
        t0 = int(t0[:2]) * 3600 + int(t0[2:4]) * 60 + int(t0[4:])
        t1 = datetime.now().strftime('%H%M%S')
        t1 = int(t1[:2]) * 3600 + int(t1[2:4]) * 60 + int(t1[4:])
        self.clock = (t0 - t1) % 86400
        with open('config/clock.txt', 'w') as file:
            file.write(str(self.clock))
        self.mainApp()

    def updateStopwatch(self):
        ms = 30000 - self.timerTouch.remainingTime()
        self.window.timeLabel.setText(f'{format(ms / 1000, ".2f")}')

    def touchButtonPressed(self):
        if self.twoCupsClicked:
            self.twoCupsClick()
        if self.oneCupClicked:
            self.oneCupClick()
        self.timerTouch.start()
        self.sendSignal()
        self.timerMilliseconds.start()

    def touchButtonReleased(self):
        if self.timerTouch.isActive():
            self.timerTouch.stop()
            self.stopSendSignal()
            self.window.timeLabel.setText('0.00')
            self.timerMilliseconds.stop()

    def oneCupClick(self):
        if self.twoCupsClicked:
            self.twoCupsClick()
        self.oneCupClicked = not self.oneCupClicked
        if self.oneCupClicked:
            self.window.oneCupButton.setStyleSheet('QPushButton {'
                                                   'background-color: rgb(235, 235, 235);'
                                                   'color: rgb(0, 0, 0); border-radius:  80px;'
                                                   'border-style: solid; border-width: 15px;'
                                                   'border-color: rgb(254, 205, 84);'
                                                   '}')
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
            self.window.oneCupButton.setStyleSheet('QPushButton {'
                                                   'background-color: rgb(255, 255, 255);'
                                                   'color: rgb(0, 0, 0); border-radius:  80px;'
                                                   'border-style: solid; border-width: 15px;'
                                                   'border-color: rgb(254, 205, 84);'
                                                   '}')
            self.timerOneCup.stop()
            self.stopSendSignal()

    def twoCupsClick(self):
        if self.oneCupClicked:
            self.oneCupClick()
        self.twoCupsClicked = not self.twoCupsClicked
        if self.twoCupsClicked:
            self.window.twoCupsButton.setStyleSheet('QPushButton {'
                                                    'background-color: rgb(235, 235, 235);'
                                                    'color: rgb(0, 0, 0); border-radius:  80px;'
                                                    'border-style: solid; border-width: 15px;'
                                                    'border-color: rgb(254, 205, 84);'
                                                    '}')
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
            self.window.twoCupsButton.setStyleSheet('QPushButton {'
                                                    'background-color: rgb(255, 255, 255);'
                                                    'color: rgb(0, 0, 0); border-radius:  80px;'
                                                    'border-style: solid; border-width: 15px;'
                                                    'border-color: rgb(254, 205, 84);'
                                                    '}')
            self.timerTwoCups.stop()
            self.stopSendSignal()

    def increaseNumClock(self, num_label):
        num = int(num_label.text())
        if num_label.objectName()[-1] == '0':
            if num == 2:
                num = 0
            elif num == 1:
                num = 2
                self.window.numLabels1[1].setText('0')
            else:
                num += 1
        elif num_label.objectName()[-1] == '1':
            if int(self.window.numLabels1[0].text()) == 2 and num == 3:
                num = 0
            elif int(self.window.numLabels1[0].text()) < 2 and num == 9:
                num = 0
            else:
                num += 1
        elif num_label.objectName()[-1] == '2' or num_label.objectName()[-1] == '4':
            if num == 5:
                num = 0
            else:
                num += 1
        else:
            if num == 9:
                num = 0
            else:
                num += 1
        num_label.setText(str(num))

    def decreaseNumClock(self, num_label):
        num = int(num_label.text())
        if num_label.objectName()[-1] == '0':
            if num == 0:
                num = 2
                self.window.numLabels1[1].setText('0')
            else:
                num -= 1
        elif num_label.objectName()[-1] == '1':
            if int(self.window.numLabels1[0].text()) == 2 and num == 0:
                num = 3
            elif int(self.window.numLabels1[0].text()) < 2 and num == 0:
                num = 9
            else:
                num -= 1
        elif num_label.objectName()[-1] == '2' or num_label.objectName()[-1] == '4':
            if num == 0:
                num = 5
            else:
                num -= 1
        else:
            if num == 0:
                num = 9
            else:
                num -= 1
        num_label.setText(str(num))

    @staticmethod
    def increaseNumDur(num_label):
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
    def decreaseNumDur(num_label):
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
        # print(1)

    @staticmethod
    def stopSendSignal():
        GPIO.output(13, False)
        # print(0)


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.showFullScreen()
    app.exec_()


if __name__ == '__main__':
    main()
