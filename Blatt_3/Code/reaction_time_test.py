import csv
import os
import sys
import random
import time
from time import sleep
from PyQt5.QtWidgets import (QApplication, QLabel, QPushButton,
                             QVBoxLayout, QWidget, QHBoxLayout)
from PyQt5.QtCore import Qt, QTimer
from PyQt5 import QtGui

# For the Task Informations use creator.py (creates the Participant_X.txt)
# Sources
# https://docs.python.org/3/library/csv.html
# https://www.qt.io/qt-for-python
# https://stackoverflow.com/questions/49971584/updating-pyqt5-gui-with-live-data

# reads and returns the data from the file (implemented by Christoph)
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
            time_between_signals = int(description)
        else:
            print('Unbekannte Eingabe!' + textline)
    return participant_id, trials, time_between_signals


# handels the Logging (implemented by Christoph)
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

# main Class for the Experiment (implemented by Julian)
class Experiment(QWidget):

    # inits the variables
    def __init__(self, trials, time_between_signals, participant_id):
        QWidget.__init__(self)
        self.trials = trials
        self.started = False
        self.wait = False
        self.trial_number = 0
        self.waiting_time = time_between_signals
        self.show_despription()
        self.logger = LogCsv(participant_id, time)

    # shows the description text
    def show_despription(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setStyleSheet("background-color:white;")
        self.info_text = QLabel(
            " Im folgenden Experiment siehst du einzelne Bilder. Diese können optisch unterschieden werden.\n"
            " Als unser Teilnehmer sollst du so schnell wie die Tasten „R“ oder „U“ abhängig vom gezeigten Bild\n"
            " drücken. Siehst du ein rotes Quadrat oder eine gerade Zahl, so drückst du „R“, siehst du ein blaues\n"
            " Quadrat oder eine ungerade Zahl, drücke die „U“ Taste. Die Bilder werden dann nacheinander angezeigt.\n"
            " Versuche deine Arme während des Experiments auf dem Tisch liegen zu lassen und nur mit den Fingern \n"
            " zu arbeiten. Wie bei jedem Experiment kannst du als Proband aber nichts falsch machen.\n"
            " Bitte nimm nun deine Position ein, der Versuchsleiter wird das Programm starten. ")
        self.info_text.setAlignment(Qt.AlignCenter)
        self.info_text.setStyleSheet("color:black;")
        self.start_button = QPushButton("Experiment starten")
        self.start_button.clicked.connect(self.start_experiment)
        # self.start_button.setStyleSheet("background-color:black;")
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
        self.image = QLabel(self)
        self.image.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.image)
        self.distraction_timer = QTimer()
        self.distraction_timer.setInterval(200)
        self.distraction_timer.timeout.connect(self.change_background)
        sleep(self.waiting_time / 1000)
        self.next_task_timer = QTimer(self)
        self.next_task_timer.setSingleShot(True)
        self.next_task_timer.timeout.connect(self.next_task)

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
        variants = ['A_Gerade', 'A_Gerade2', 'A_Gerade4', 'A_Gerade6', 'A_Gerade8', 'A_Ungerade1', 'A_Ungerade3',
                    'A_Ungerade5', 'A_Ungerade7']
        self.variant = random.choice(variants)
        if 'Gerade' in self.variant.split('_')[1]:
            self.correct_key = 'R'
        else:
            self.correct_key = 'U'
        url = 'Assets/' + self.variant + '.png'
        pixmap = QtGui.QPixmap(url)
        self.image.setPixmap(pixmap)
        self.image.show()
        self.text_trial_number.setText(str(self.trial_number))

    # sets the displayed image for preattentive task rot
    def show_pre_attentive_images(self):
        variants = ['P_Rot', 'P_Blau']
        self.variant = random.choice(variants)
        if self.variant.split('_')[1] == 'Rot':
            self.correct_key = 'R'
        else:
            self.correct_key = 'U'
        url = 'Assets/' + self.variant + '.jpg'
        pixmap = QtGui.QPixmap(url)
        self.image.setPixmap(pixmap)
        self.image.show()
        self.text_trial_number.setText(str(self.trial_number))

    # changes the background for distraction ungerade
    def change_background(self):
        colors = ['black', 'red', 'green', 'blue', 'orange', 'grey']
        self.setStyleSheet("background-color:" + random.choice(colors) + ";")

    # handels the user input
    def keyPressEvent(self, event):
        if self.started:
            # red and odd
            if event.key() == Qt.Key_R and not self.wait:
                self.wait = True
                self.image.hide()
                self.reaction_time = time.time() - self.reaction_time
                timestamp = time.time()
                self.wait_for_next_task('R', timestamp)
            # blue and even
            elif event.key() == Qt.Key_U and not self.wait:
                self.wait = True
                self.image.hide()
                self.reaction_time = time.time() - self.reaction_time
                timestamp = time.time()
                self.wait_for_next_task('U', timestamp)

    # creates the log entry
    def create_log_entry(self, pressed_number, timestamp):
        if self.correct_key == pressed_number:
            correct_key_pressed = True
        else:
            correct_key_pressed = False
        self.logger.write_row(self.trials[self.trial_number], self.variant, self.distraction, pressed_number,
                              correct_key_pressed, self.reaction_time, timestamp)

    # waits and starts new task
    def wait_for_next_task(self, pressed_number, timestamp):
        self.create_log_entry(pressed_number, timestamp)
        self.setStyleSheet("background-color:white;")
        self.next_task_timer.start(self.waiting_time)

    # starts a new task
    def next_task(self):
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
