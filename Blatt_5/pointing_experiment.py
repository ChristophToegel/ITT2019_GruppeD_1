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

    # inits all variabeles
    def __init__(self, user_id, sizes, distances, new_pointing):
        self.error_counter = 0
        self.started = False
        self.number_task = 0
        self.sizes = sizes
        self.user_id = user_id
        self.distances = distances
        self.new_poinitng = new_pointing
        self.task_timer = 0
        self.target_position = (0, 0, 0)

    # return the radius and distance for the current task
    def get_task_draw_para(self):
        radius = self.sizes[self.number_task]
        distance_to_mouse = self.distances[self.number_task]
        return radius, distance_to_mouse

    # return if the new_ponting technique is used
    def get_task_mouse_para(self):
        if self.new_poinitng[self.number_task] == 'ON':
            return True
        else:
            return False

    def create_log_header(self):
        print('user_id' + ',' + 'pointer_pos' + ',' + 'errors' + ',' + 'timestamp' + ',' + 'task_completion_time' + ','
                                                                                                                    'new_pointing_technique' + ',' + 'distance')

    def create_log_entry(self, timestamp, pointer_pos):
        task_completion_time = timestamp - self.task_timer
        print(str(self.user_id) + ',' + str(pointer_pos.x()) + ';' + str(pointer_pos.y()) + ',' + str(
            self.error_counter) + ',' + str(timestamp) + ',' + str(task_completion_time) +
              ',' + str(self.get_task_mouse_para()) + ',' + str(self.distances[self.number_task]))
        self.reset_error_counter()

    def start_task_time(self):
        self.task_timer = time.time()

    def start_experiment(self):
        self.create_log_header()
        self.started = True

    def check_target_selected(self, cursor_x, cursor_y):
        if cursor_x in range(self.target_position[0], self.target_position[0] + self.target_position[2]):
            if cursor_y in range(self.target_position[1], self.target_position[1] + self.target_position[2]):
                return True
            else:
                return False
        else:
            return False

    # returns the target position
    def calculate_target_dest(self, mouse_qpoint, radius, distance_to_mouse, height, width):
        mouse_y = mouse_qpoint.y()
        mouse_x = mouse_qpoint.x()
        # create list of possible target points
        tar_pos = []
        for k in range(20):
            pi_frac = (2 * math.pi) / (20 - 1)
            x_circ = (math.cos((k + 1) * pi_frac) * distance_to_mouse) + mouse_x
            y_circ = (math.sin((k + 1) * pi_frac) * distance_to_mouse) + mouse_y
            if radius < x_circ < width - radius and radius < y_circ < height - radius:
                tar_pos.append((int(x_circ), int(y_circ)))
        x, y = tar_pos[math.floor(random.random() * len(tar_pos) - 1)]
        self.target_position = (x, y, radius * 2)
        return x, y

    def reset_error_counter(self):
        self.error_counter = 0

    # increases the task or ends the program if tasks are done
    def increase_task(self):
        self.number_task += 1
        if self.number_task == len(self.distances):
            exit()

    def increase_error(self):
        self.error_counter += 1


class PointingExperiment(QWidget):

    def __init__(self, color_target, color_noise, model):
        super(QWidget, self).__init__()
        self.pointer = AnglePointing()
        self.model = model
        self.setMouseTracking(True)
        self.element_numbers = 100
        self.screen_width = 1440
        self.screen_height = 850
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
        self.start_experiment()

    # starts the experiment
    def start_experiment(self):
        self.model.start_experiment()
        QCursor.setPos(self.mapToGlobal(QtCore.QPoint(self.screen_width / 2, self.screen_height / 2)))
        self.update()

    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton and self.model.started:
            timestamp = time.time()
            if self.model.check_target_selected(ev.x(), ev.y()):
                self.model.create_log_entry(timestamp, ev.pos())
                # counts the task or ends if last one
                self.model.increase_task()
                self.update()
            else:
                # increases the error counter
                self.model.increase_error()

    # changes the poinitng if selected
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
            self.model.start_task_time()
            self.draw_points(painter)
            painter.end()

    # draws the experiment presentation
    def draw_points(self, painter):
        radius, distance_to_mouse = self.model.get_task_draw_para()

        # randomly place objects
        for i in range(self.element_numbers):
            y = int(random.random() * (self.screen_height - radius * 2) + (radius / 2))
            x = int(random.random() * (self.screen_width - radius * 2) + (radius / 2))

            # last drawn element is target
            if i == self.element_numbers - 1:
                color = self.color_target
                mouse_qpoint = self.mapFromGlobal(QCursor.pos())
                x, y = self.model.calculate_target_dest(mouse_qpoint, radius, distance_to_mouse, self.height(),
                                                        self.width())

            # all the noise dots
            else:
                color = self.color_noise

            # draw the circle
            painter.setPen(color)
            painter.setBrush(color)
            painter.drawEllipse(x, y, radius, radius)


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
    # widget is magic
    model = ExperimentModel(user_id, sizes, distance, new_pointing)
    widget = PointingExperiment(color_target, color_noise, model)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
