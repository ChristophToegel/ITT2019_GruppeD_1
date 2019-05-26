# -*- coding: utf-8 -*-
import json
import sys
import random
import math
from PyQt5.QtWidgets import (QApplication, QLabel, QPushButton,
                             QVBoxLayout, QWidget)
from PyQt5 import QtCore
from PyQt5.QtGui import QPainter, QColor, QFont, QCursor


# http://zetcode.com/gui/pyqt5/painting/
# SIZE< Distance ; 3 size+distance max 150

class PointingExperiment(QWidget):

    def __init__(self, user_id, sizes, distances, highlighted):
        super(QWidget, self).__init__()
        self.started = False
        self.setMouseTracking(True)
        self.line_height = 200
        self.line_numbers = 3
        self.number_task = 0
        self.sizes = sizes
        self.distances = distances
        self.highlighted = highlighted
        self.element_numbers = 100
        self.init_ui()
        self.screen_width = 600
        self.screen_height = 600

    def init_ui(self):
        self.setWindowTitle('Poinitng Experiment')
        self.text = "Please click on the target"
        self.setGeometry(0, 0, 600, 600)
        # self.setGeometry(0, 0, 1920, 900)
        # QtGui.QCursor.setPos(self.mapToGlobal(QtCore.QPoint(self.start_pos[0], self.start_pos[1])))
        self.show()
        self.show_despription()

    def show_despription(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setStyleSheet("background-color:white;")
        self.info_text = QLabel(
            " Versuchen Sie auf das farbige Rechteck zu klicken.")
        self.info_text.setAlignment(QtCore.Qt.AlignCenter)
        self.info_text.setStyleSheet("color:black;")
        self.start_button = QPushButton("Experiment starten")
        self.start_button.clicked.connect(self.hide_description)
        self.layout.addWidget(self.info_text)
        self.layout.addWidget(self.start_button)

    # hides the despription text
    def hide_description(self):
        self.start_button.hide()
        self.info_text.hide()
        self.started = True
        self.update()

    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton and self.started:
            if self.check_target_selected(ev.x(), ev.y()):
                print('loggen')
                if self.number_task + 2 <= len(self.distances):
                    self.number_task += 1
                    self.update()

    def check_target_selected(self, cursor_x, cursor_y):
        if cursor_x in range(self.target_positon[0], self.target_positon[0] + self.target_positon[2]):
            if cursor_y in range(self.target_positon[1], self.target_positon[1] + self.target_positon[2]):
                return True
            else:
                return False
        else:
            return False

    def mouseMoveEvent(self, ev):
        # self.filter()
        pass
        # print('mouse moved')
        # print(ev)
        # self.filter(ev.pos())

    def paintEvent(self, event):
        if self.started:
            painter = QPainter()
            painter.begin(self)
            self.draw_points(painter)
            # self.drawText(event,painter)
            painter.end()

    def draw_points(self, painter):
        radius = self.sizes[self.number_task]
        distance_to_mouse = self.distances[self.number_task]

        # randomly place objects
        for i in range(self.element_numbers):
            y = int(random.random() * (self.screen_height - radius) + (radius / 2))
            x = int(random.random() * (self.screen_width - radius) + (radius / 2))

            # last drawn element is target
            if i == self.element_numbers - 1:
                color = QtCore.Qt.yellow
                print(self.target_positon)

                # calc distance to mouse
                mouse_qpoint = self.mapFromGlobal(QCursor.pos())
                mouse_y = mouse_qpoint.y()
                mouse_x = mouse_qpoint.x()

                # create list of all possible traget points
                for k in range(20):
                    pi_frac = (2 * math.pi) / (20 - 1)
                    x_circ = (math.cos((k + 1) * pi_frac) * radius) + mouse_x
                    y_circ = (math.sin((k + 1) * pi_frac) * radius) + mouse_y
                    tar_pos = []
                    if radius > x_circ < self.width() - radius and radius > y_circ < self.height() - radius:
                        tar_pos.append((x, y))

                x, y = tar_pos[math.floor(random.random()*len(tar_pos)-1)]

            else:
                color = QtCore.Qt.lightGray

            painter.setPen(color)
            painter.setBrush(color)
            painter.drawEllipse(x, y, radius, radius)

    def drawText(self, event, painter):
        painter.setPen(QColor(168, 34, 3))
        painter.setFont(QFont('Decorative', 10))
        painter.drawText(event.rect(), QtCore.Qt.AlignCenter, 'HAllO')

    def drawBackground(self, event, qp):
        if self.model.mouse_moving:
            qp.setBrush(QColor(220, 190, 190))
        else:
            qp.setBrush(QColor(200, 200, 200))
        qp.drawRect(event.rect())

    def filter(self):
        size = self.size()
        x = random.randint(1, size.width() - 1)
        y = random.randint(1, size.height() - 1)
        # self.setCursor(QtCore.Qt.OpenHandCursor)
        # pos = QCursor.pos()
        # QCursor()
        QCursor.setPos(200, 200)
        # QCursor.setPos(pos)
        print(QCursor.pos())
        print('filetr')


def read_setup(filename):
    file = open(filename, "r")
    data = json.load(file)
    return data['USER'], data['SIZE'], data['DISTANCES'], data['HIGHLIGHTED']


def main():
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: %s <setup file>\n" % sys.argv[0])
        sys.exit(1)
    file_name = sys.argv[1]
    user_id, sizes, distances, highlighted = read_setup(file_name)

    app = QApplication(sys.argv)
    # widget is magic
    widget = PointingExperiment(user_id, sizes, distances, highlighted)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
