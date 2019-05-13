import csv
import os
import sys
import random
import datetime
import time
from time import sleep
from PyQt5.QtWidgets import (QApplication, QLabel, QPushButton,
                             QVBoxLayout, QWidget, QHBoxLayout)
from PyQt5.QtCore import Qt, QTimer
from PyQt5 import QtGui

IMAGE_SEQUENCE = [1, 2, 1, 1, 2, 1, 1, 2, 1, 2, 2, 2, 1, 1, 2, 2, 1, 2, 1, 1, 2, 1, 2, 2, 2, 1, 2, 1, 2, 2, 1, 1, 1,
                  2, 2, 1, 2, 2, 1, 1]


# https://docs.python.org/3/library/csv.html
# https://www.qt.io/qt-for-python
# https://stackoverflow.com/questions/49971584/updating-pyqt5-gui-with-live-data

def read_experiment_setup(filename):
    file = open(filename, 'r')
    text = file.read()
    participant_id = None
    trials = None
    time_between_signals = None
    for textline in text.splitlines():
        title, description = textline.split(':')
        if title == 'PARTICIPANT':
            participant_id = description.replace(' ', '')
        elif title == 'TRIALS':
            trials = description.replace(' ', '').split(',')
        elif title == 'TIME_BETWEEN_SIGNALS_MS':
            time_between_signals = int(description) / 1000
        else:
            print('Unbekannte Eingabe!' + textline)
    return participant_id, trials, time_between_signals


# handels the Logging
class LogCsv():

    # inits csv colums
    def __init__(self, participant_id, time):
        self.filename = 'Participant_' + participant_id + '_log.csv'
        self.participant_id = participant_id
        self.time = time
        self.fieldnames = ['participant_id', 'stimulus', 'mental_complexity', 'distraction', 'pressed_key',
                           'correct_key_pressed',
                           'reaction_time', 'timestamp']
        self.check_file()
        self.open_file()

    # checks if file exists
    def check_file(self):
        if os.path.isfile(self.filename):
            self.write_header = False
        else:
            self.write_header = True

    # opens the file and wirites the header
    def open_file(self):
        with open(self.filename, 'a+', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
            if self.write_header:
                writer.writeheader()
            self.close_file(csvfile)

    # closes the file
    def close_file(self, file):
        file.close()

    # adds a log entry
    def write_row(self, stimulus, mental_complexity, distraction, pressed_key, correct_key_pressed, reaction_time,
                  timestamp):
        with open(self.filename, 'a+', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
            writer.writerow(
                {'participant_id': self.participant_id, 'stimulus': stimulus, 'distraction': distraction,
                 'mental_complexity': mental_complexity,
                 'pressed_key': pressed_key, 'correct_key_pressed': correct_key_pressed, 'reaction_time': reaction_time,
                 'timestamp': timestamp})
        self.close_file(csvfile)


class Experiment(QWidget):

    # inits the variables
    def __init__(self, trials, time_between_signals, participant_id):
        QWidget.__init__(self)
        self.trials = trials
        self.started = False
        self.wait = False
        self.trial_number = 0
        self.trial_number_pre_attentive = 0
        self.trial_number_attentive = 0
        self.waiting_time = time_between_signals
        self.show_despription()
        self.logger = LogCsv(participant_id, time)

    # shows the description text
    def show_despription(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.info_text = QLabel(
            " Im folgenden Experiment siehst du Bildpaare. Diese können optisch unterschieden werden. \n"
            " Als unser Teilnehmer sollst du so schnell wie möglich die Seite mit dem roten Quadrat oder \n"
            " den ungeraden auswählen.  Mit den Tasten ‚D‘ und ‚K‘ wählst du dann die linke oder rechte \n"
            " Seite aus. Die Bilder werden dann nacheinander angezeigt. Wie bei jedem Experiment kannst du \n"
            " als Proband nichts falsch machen. ")
        self.info_text.setAlignment(Qt.AlignCenter)
        self.start_button = QPushButton("Experiment starten")
        self.start_button.clicked.connect(self.start_experiment)
        self.layout.addWidget(self.info_text)
        self.layout.addWidget(self.start_button)

    # hides the despription text
    def hide_description(self):
        self.start_button.hide()
        self.info_text.hide()

    # user presses the start button
    def start_experiment(self):
        self.hide_description()
        self.started = True
        self.trial_number = 0
        self.load_experiment_ui()
        self.load_experiment_data()

    # loads the Ui for the Experiment
    def load_experiment_ui(self):
        self.text_trial_number = QLabel(str(self.trial_number))
        self.text_trial_number.setAlignment(Qt.AlignCenter)
        self.text_trial_number.setStyleSheet('color: black')
        self.layout.addWidget(self.text_trial_number)
        self.setStyleSheet("background-color:white;")
        self.image_right = QLabel(self)
        self.image_left = QLabel(self)

        hbox = QHBoxLayout()
        hbox.addWidget(self.image_left)
        hbox.addWidget(self.image_right)
        self.layout.addLayout(hbox)

        self.distraction_timer = QTimer()
        self.distraction_timer.setInterval(200)
        self.distraction_timer.timeout.connect(self.change_background)
        sleep(self.waiting_time)
        

    # loads the experiment data and sets up the task
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
            self.reaction_time = time.time()
        elif self.mental_complexity == "P":
            self.show_pre_attentive_images()
            self.reaction_time = time.time()

    # sets the displayed image for attentive task
    def show_attentive_images(self):
        variants = ['A-1', 'A-2']
        if IMAGE_SEQUENCE[self.trial_number_attentive] == 1:
            url_left = 'Assets/' + variants[0] + '.jpg'
            url_right = 'Assets/' + variants[1] + '.jpg'
        else:
            url_left = 'Assets/' + variants[1] + '.jpg'
            url_right = 'Assets/' + variants[0] + '.jpg'
        self.trial_number_attentive += 1
        pixmap = QtGui.QPixmap(url_left)
        self.image_left.setPixmap(pixmap)

        pixmap = QtGui.QPixmap(url_right)
        self.image_right.setPixmap(pixmap)
        self.text_trial_number.setText(str(self.trial_number))

    # sets the displayed image for preattentive task rot
    def show_pre_attentive_images(self):
        variants = ['P-1', 'P-2']
        if IMAGE_SEQUENCE[self.trial_number_pre_attentive] == 1:
            url_left = 'Assets/' + variants[1] + '.jpg'
            url_right = 'Assets/' + variants[0] + '.jpg'
        else:
            url_left = 'Assets/' + variants[0] + '.jpg'
            url_right = 'Assets/' + variants[1] + '.jpg'
        self.trial_number_pre_attentive += 1

        pixmap = QtGui.QPixmap(url_left)
        self.image_left.setPixmap(pixmap)

        pixmap = QtGui.QPixmap(url_right)
        self.image_right.setPixmap(pixmap)
        self.text_trial_number.setText(str(self.trial_number))

    # changes the background for distraction ungerade
    def change_background(self):
        colors = ['black', 'red', 'green', 'blue', 'orange', 'grey']
        self.setStyleSheet("background-color:" + random.choice(colors) + ";")

    # handels the user input
    def keyPressEvent(self, event):
        if self.started:
            # gesuchtes Item links
            if event.key() == Qt.Key_D and not self.wait:
                self.reaction_time = time.time() - self.reaction_time
                timestamp = time.time()
                self.wait_for_next_task('D', timestamp)
            # gesuchtes Item rechts
            elif event.key() == Qt.Key_K and not self.wait:
                self.reaction_time = time.time() - self.reaction_time
                timestamp = time.time()
                self.wait_for_next_task('K', timestamp)

    # creates the log entry
    def create_log_entry(self, pressed_number, timestamp):
        if self.mental_complexity == 'P':
            if (IMAGE_SEQUENCE[self.trial_number_pre_attentive - 1] == 1 and pressed_number == 'D') or (
                    IMAGE_SEQUENCE[self.trial_number_pre_attentive - 1] == 2 and pressed_number == 'K'):
                correct_key_pressed = True
            else:
                correct_key_pressed = False
        elif self.mental_complexity == 'A':
            if (IMAGE_SEQUENCE[self.trial_number_attentive - 1] == 1 and pressed_number == 'D') or (
                    IMAGE_SEQUENCE[self.trial_number_attentive - 1] == 2 and pressed_number == 'K'):
                correct_key_pressed = True
            else:
                correct_key_pressed = False
        else:
            correct_key_pressed = False

        self.logger.write_row(self.trials[self.trial_number], self.mental_complexity, self.distraction, pressed_number,
                              correct_key_pressed, self.reaction_time, timestamp)

    # waits and starts new task
    def wait_for_next_task(self, pressed_number, timestamp):
        self.wait = True
        self.create_log_entry(pressed_number, timestamp)
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
    participant_id, trials, time_between_signals = read_experiment_setup(file)
    app = QApplication(sys.argv)
    widget = Experiment(trials, time_between_signals, participant_id)
    widget.resize(600, 400)
    widget.show()

    sys.exit(app.exec_())
