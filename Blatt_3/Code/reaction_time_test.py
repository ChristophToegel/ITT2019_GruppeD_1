import csv
import os
import sys
import random
import datetime
from time import sleep
from PyQt5.QtWidgets import (QApplication, QLabel, QPushButton,
                             QVBoxLayout, QWidget, QHBoxLayout)
from PyQt5.QtCore import Qt, QTimer
from PyQt5 import QtGui


# https://docs.python.org/3/library/csv.html
# https://www.qt.io/qt-for-python
# https://stackoverflow.com/questions/49971584/updating-pyqt5-gui-with-live-data

def read_experiment_setup(filename):
    file = open(filename, 'r')
    text = file.read()
    participant_id = None
    trials = None
    time = None
    for textline in text.splitlines():
        title, description = textline.split(':')
        if title == 'PARTICIPANT':
            participant_id = description.replace(' ', '')
        elif title == 'TRIALS':
            trials = description.replace(' ', '').split(',')
        elif title == 'TIME_BETWEEN_SIGNALS_MS':
            time = int(description) / 1000
        else:
            print('Unbekannte Eingebe!')
    return participant_id, trials, time


class LogCsv():

    def __init__(self, participant_id, time):
        self.filename = 'reaction_time_results.csv'
        self.participant_id = participant_id
        self.time = time
        self.fieldnames = ['participant_id', 'stimulus', 'mental_complexity', 'distraction', 'pressed_key',
                           'correct_key_pressed',
                           'reaction_time', 'timestamp']
        self.check_file()
        self.open_file()

    def check_file(self):
        if os.path.isfile('reaction_time_results.csv'):
            self.write_header = False
        else:
            self.write_header = True

    def open_file(self):
        with open(self.filename, 'a+', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
            if self.write_header:
                writer.writeheader()
            self.close_file(csvfile)

    def close_file(self, file):
        file.close()

    def write_row(self, stimulus, mental_complexity, distraction, pressed_key, correct_key_pressed, reaction_time,
                  timestamp):
        # entweder vorrübergehend als dict speichern oder immer file öffnen?!
        with open(self.filename, 'a+', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
            writer.writerow(
                {'participant_id': self.participant_id, 'stimulus': stimulus, 'distraction': distraction,
                 'mental_complexity': mental_complexity,
                 'pressed_key': pressed_key, 'correct_key_pressed': correct_key_pressed, 'reaction_time': reaction_time,
                 'timestamp': timestamp})
        self.close_file(csvfile)


class Experiment(QWidget):

    def __init__(self, trials, time, participant_id):
        QWidget.__init__(self)
        self.trials = trials
        self.started = False
        self.wait = False
        self.trial_number = 0
        self.waiting_time = time
        self.show_despription()
        self.logger = LogCsv(participant_id, time)

    def show_despription(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.info_text = QLabel("Willkommen drücken Sie A für attentive oder P für pre-attentive")
        self.info_text.setAlignment(Qt.AlignCenter)
        self.start_button = QPushButton("Experiment starten")
        self.start_button.clicked.connect(self.start_experiment)
        self.layout.addWidget(self.info_text)
        self.layout.addWidget(self.start_button)

    def hide_description(self):
        self.start_button.hide()
        self.info_text.hide()

    def start_experiment(self):
        self.hide_description()
        self.started = True
        self.trial_number = 0
        self.load_experiment_ui()
        self.load_experiment_data()

    def load_experiment_ui(self):
        self.test = QLabel("Title")
        self.test.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.test)

        self.image_right = QLabel(self)
        self.image_left = QLabel(self)

        hbox = QHBoxLayout()
        hbox.addWidget(self.image_right)
        hbox.addWidget(self.image_left)
        self.layout.addLayout(hbox)

        self.distraction_timer = QTimer()
        self.distraction_timer.setInterval(500)
        self.distraction_timer.timeout.connect(self.change_background)

    def load_experiment_data(self):
        print('task:' + str(self.trial_number))
        trial = self.trials[self.trial_number]
        self.mental_complexity = list(trial)[0]
        if list(trial)[1] == 'D':
            self.distraction = True
            self.distraction_timer.start()
        else:
            self.distraction = False
            self.distraction_timer.stop()
        if self.mental_complexity == "A":
            self.show_attentive_images()
        elif self.mental_complexity == "P":
            self.show_pre_attentive_images()
        # print('Experinent mit: '+self.mental_complexity+' distraction:'+str(self.distraction))

    def show_attentive_images(self):
        numbers = ['1', '2', '6', '7']
        number = random.choice(numbers)
        url_left = 'Assets/A-' + number + '-Links.jpg'
        pixmap = QtGui.QPixmap(url_left)
        self.image_left.setPixmap(pixmap)
        url_right = 'Assets/A-' + number + '-Rechts.jpg'
        pixmap = QtGui.QPixmap(url_right)
        self.image_right.setPixmap(pixmap)
        # print('Images:A' + url_right + 'und' + url_left)

    def show_pre_attentive_images(self):
        numbers = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
        number = random.choice(numbers)
        url_left = 'Assets/P-' + number + '-Links.jpg'
        pixmap = QtGui.QPixmap(url_left)
        self.image_left.setPixmap(pixmap)
        url_right = 'Assets/P-' + number + '-Rechts.jpg'
        pixmap = QtGui.QPixmap(url_right)
        self.image_right.setPixmap(pixmap)
        # print('ImagesPA:'+url_right+'und'+url_left)

    def change_background(self):
        colors = ['black', 'red', 'green', 'blue']
        self.setStyleSheet("background-color:" + random.choice(colors) + ";")

    def keyPressEvent(self, event):
        if self.started:
            if event.key() == Qt.Key_A and not self.wait:
                timestamp = datetime.datetime.now().timestamp()
                self.wait_for_next_task('A', timestamp)
            elif event.key() == Qt.Key_P and not self.wait:
                timestamp = datetime.datetime.now().timestamp()
                self.wait_for_next_task('P', timestamp)

    def wait_for_next_task(self, pressed_number, timestamp):
        self.wait = True
        # logging
        if self.mental_complexity == pressed_number:
            correct_key_pressed = True
        else:
            correct_key_pressed = False
        # rection time messen anstatt
        self.logger.write_row(self.trials[self.trial_number], self.mental_complexity, self.distraction, pressed_number,
                              correct_key_pressed, 'reactionTime', timestamp)
        self.setStyleSheet("background-color:white;")

        sleep(self.waiting_time)
        if self.trial_number + 1 != len(self.trials):
            self.trial_number += 1
            self.wait = False
            self.load_experiment_data()
        else:
            print("end Experiment")


if __name__ == "__main__":
    file = sys.argv[1]
    participant_id, trials, time = read_experiment_setup(file)
    app = QApplication(sys.argv)

    widget = Experiment(trials, time, participant_id)
    widget.resize(600, 400)
    widget.show()

    sys.exit(app.exec_())
