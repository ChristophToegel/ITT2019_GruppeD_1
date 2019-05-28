# -*- coding: utf-8 -*-
import json
import sys
import random
import math
import time
import csv
import os
from PyQt5.QtWidgets import (QApplication, QLabel, QPushButton,
                             QVBoxLayout, QWidget)
from PyQt5 import QtCore
from PyQt5.QtGui import QPainter, QColor, QFont, QCursor
from pointing_technique import AnglePointing


# http://zetcode.com/gui/pyqt5/painting/
# nur 4 conditions nah fern; poiting und notPoinitng;

class ExperimentModel():

    def __init__(self, user_id, sizes, distances, new_pointing):
        self.error_counter = 0
        self.started = False
        self.number_task = 0
        self.sizes = sizes
        self.user_id = user_id
        self.distances = distances
        self.new_poinitng = new_pointing

    def get_task_draw_para(self):
        radius = self.sizes[self.number_task]
        distance_to_mouse = self.distances[self.number_task]
        return radius, distance_to_mouse

    def get_task_mouse_para(self):
        if self.new_poinitng[self.number_task] == 'ON':
            return True
        else:
            return False

    def create_log_header(self):
        print('user_id' + ',' + 'pointer_pos' + ',' + 'errors' + ',' + 'task_completion_time' + ',' +
              'new_pointing_technique' + ',' + 'distance')

    def create_log_entry(self, timestamp, pointer_pos):
        print(str(self.user_id) + ',' + str(pointer_pos.x()) + ';' + str(pointer_pos.y()) + ',' + str(
            self.error_counter) + ',' + str(timestamp) +
              ',' + str(self.get_task_mouse_para()) + ',' + str(self.distances[self.number_task]))


class PointingExperiment(QWidget):

    def __init__(self, user_id, sizes, distances, color_target, color_noise, new_pointing):
        super(QWidget, self).__init__()
        self.pointer = AnglePointing(500)
        self.model = ExperimentModel(user_id, sizes, distances, new_pointing)
        self.setMouseTracking(True)
        self.element_numbers = 100
        self.screen_width = 1440
        self.screen_height = 850
        # self.logger = LogCSV(user_id, time)
        self.init_ui()
        self.set_color(color_target, color_noise)

    # sets the color form config file
    def set_color(self, color_target, color_noise):
        if color_target == "yellow":
            self.color_target = QtCore.Qt.yellow
        if color_target == "darkGray":
            self.color_target = QtCore.Qt.darkGray
        if color_noise == "lightGray":
            self.color_noise = QtCore.Qt.lightGray
        if color_noise == "darkBlue":
            self.color_noise = QtCore.Qt.darkBlue

    def init_ui(self):
        self.setWindowTitle('Pointing Experiment')
        self.setGeometry(0, 0, self.screen_width, self.screen_height)
        self.show()
        self.show_despription()

    def show_despription(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setStyleSheet("background-color:white;")
        self.info_text = QLabel("Try to click on the yellow marked Circle")
        self.info_text.setAlignment(QtCore.Qt.AlignCenter)
        self.info_text.setStyleSheet("color:black;")
        self.start_button = QPushButton("start Experiment")
        self.start_button.clicked.connect(self.hide_description)
        self.layout.addWidget(self.info_text)
        self.layout.addWidget(self.start_button)

    # hides the despription text
    def hide_description(self):
        self.start_button.hide()
        self.info_text.hide()
        self.model.started = True
        QCursor.setPos(self.mapToGlobal(QtCore.QPoint(self.screen_width / 2, self.screen_height / 2)))
        self.model.create_log_header()
        self.update()

    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton and self.model.started:
            timestamp = time.time()
            if self.check_target_selected(ev.x(), ev.y()):
                self.model.create_log_entry(timestamp, ev.pos())
                self.model.error_counter = 0
                # counts the task and shows a new one
                self.model.number_task += 1
                # ends the Experiment
                if self.model.number_task == len(self.model.distances):
                    exit()
                self.update()
            else:
                self.model.error_counter += 1

    def check_target_selected(self, cursor_x, cursor_y):
        if cursor_x in range(self.target_position[0], self.target_position[0] + self.target_position[2]):
            if cursor_y in range(self.target_position[1], self.target_position[1] + self.target_position[2]):
                return True
            else:
                return False
        else:
            return False

    def mouseMoveEvent(self, ev):
        if self.model.get_task_mouse_para():
            curser_pos = self.mapToGlobal(QtCore.QPoint(ev.x(), ev.y()))
            curser_pos_x = curser_pos.x()
            curser_pos_y = curser_pos.y()
            x, y = self.pointer.filter(curser_pos_x, curser_pos_y)
            QCursor.setPos(x, y)

    def paintEvent(self, event):
        if self.model.started:
            painter = QPainter()
            painter.begin(self)
            self.draw_points(painter)
            painter.end()

    def draw_points(self, painter):
        radius, distance_to_mouse = self.model.get_task_draw_para()

        # randomly place objects
        for i in range(self.element_numbers):
            y = int(random.random() * (self.screen_height - radius) + (radius / 2))
            x = int(random.random() * (self.screen_width - radius) + (radius / 2))

            # last drawn element is target
            if i == self.element_numbers - 1:
                color = self.color_target

                # calc distance to mouse
                mouse_qpoint = self.mapFromGlobal(QCursor.pos())
                mouse_y = mouse_qpoint.y()
                mouse_x = mouse_qpoint.x()

                # create list of possible target points
                tar_pos = []
                for k in range(20):
                    pi_frac = (2 * math.pi) / (20 - 1)
                    x_circ = (math.cos((k + 1) * pi_frac) * distance_to_mouse) + mouse_x
                    y_circ = (math.sin((k + 1) * pi_frac) * distance_to_mouse) + mouse_y
                    if radius < x_circ < self.width() - radius and radius < y_circ < self.height() - radius:
                        tar_pos.append((x, y))

                x, y = tar_pos[math.floor(random.random() * len(tar_pos) - 1)]
                self.target_position = (x, y, radius * 2)

            # all the noise dots
            else:
                color = self.color_noise

            # draw the circle
            painter.setPen(color)
            painter.setBrush(color)
            painter.drawEllipse(x, y, radius, radius)


# handels the Logging (implemented by Christoph)
class LogCSV():

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


def read_setup(filename):
    file = open(filename, "r")
    data = json.load(file)
    return data['USER'], data["CONF"]['SIZE'], data["CONF"]['DISTANCE'], data["CONF"]['COLOR_T'], \
           data["CONF"]['COLOR_N'], data["CONF"]['NEW_POINTING_TECHNIQUE']


def main():
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: %s <setup file>\n" % sys.argv[0])
        sys.exit(1)
    file_name = sys.argv[1]
    user_id, sizes, distance, color_target, color_noise, new_pointing = read_setup(file_name)

    app = QApplication(sys.argv)
    # TODO model heier initiieren und dann PoinitngExperiment übergeben!
    # widget is magic
    widget = PointingExperiment(user_id, sizes, distance, color_target, color_noise, new_pointing)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
