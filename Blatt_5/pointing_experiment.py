# -*- coding: utf-8 -*-
import json
import sys
from PyQt5.QtWidgets import (QApplication, QLabel, QPushButton,
                             QVBoxLayout, QWidget)
from PyQt5 import QtCore
from PyQt5.QtGui import QPainter, QColor, QFont, QCursor
import random


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
        self.element_numbers = 9
        self.init_ui()

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
            if self.check_target_selekted(ev.x(), ev.y()):
                print('loggen')
                if self.number_task + 2 <= len(self.distances):
                    self.number_task += 1
                    self.update()

    def check_target_selekted(self, curser_x, curser_y):
        if curser_x in range(self.target_positon[0], self.target_positon[0] + self.target_positon[2]):
            if curser_y in range(self.target_positon[1], self.target_positon[1] + self.target_positon[2]):
                return True
            else:
                return False
        else:
            return False

    def mouseMoveEvent(self, ev):
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
        width = self.sizes[self.number_task]
        distance = self.distances[self.number_task]

        for i in range(self.element_numbers):
            y = (i % self.line_numbers + 1) * distance + 50
            x = int(i / self.line_numbers) * distance + 50
            if i == self.highlighted[self.number_task]:
                color = QtCore.Qt.yellow
                self.target_positon = (x, y, width)
            else:
                color = QtCore.Qt.darkBlue
            painter.setPen(color)
            painter.setBrush(color)
            painter.drawRect(x, y, width, width)

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

    def filter(self, curser_pos):
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
