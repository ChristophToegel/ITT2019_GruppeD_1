# -*- coding: utf-8 -*-
import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QTextEdit, QVBoxLayout
from text_input_technique import TextEditTechnique
import random

'''
Workload distribution among team:
    Christoph: Logging(class), main(method)
    Julian: Experiment(class), read_text_form_file(method)
'''


# https://doc.qt.io/qt-5/qtextedit.html

class Logging():

    def __init__(self, participant_id, completion):
        self.time_sentence = 0
        self.time_word = 0
        self.time_complete = 0
        self.typed_sentences = ""
        self.write_header()
        self.timestamp = 0
        self.last_word = ""
        self.participant_id = participant_id
        self.completion = completion

    # interprets the pressed events
    def loginput(self, text, timestamp, task_num, technique_used):
        finished = False
        reset_technique = False
        self.timestamp = timestamp
        if len(text) >= 1:
            last_input = text[len(text) - 1]
            words = text.split()
            current_word = words[len(words) - 1]

            if len(text) == 1:
                self.time_sentence = timestamp
                self.time_word = timestamp
                if self.typed_sentences == "":
                    self.time_complete = timestamp
            elif len(text) >= 2:
                second_last_input = text[len(text) - 2]
                if second_last_input.isspace():
                    self.time_word = timestamp

            # key pressed
            if not technique_used or last_input == ' ':
                self.write_log_entry('key pressed', last_input, current_word, text, task_num, "none")

            # word typed
            if last_input.isspace() or last_input == '\n':
                self.write_log_entry('word typed', last_input, current_word, text, task_num, technique_used)
                reset_technique = True

            # sentence typed
            if last_input == '\n' and second_last_input == ".":
                self.write_log_entry('sentence typed', last_input, current_word, text, task_num, "none")
                self.typed_sentences += text.replace('\n', '')
                finished = True

            self.last_word = current_word

        return finished, reset_technique

    def write_header(self):
        print(
            'event_type,current_char,timestamp,current_word,current_word_time,current_sentence,current_sentence_time,'
            'complete_text,current_complete_time,sentence_num,technique_used,autocompletion,participant_id')

    def write_log_entry(self, event_name, char, word, sentence, task_num, technique_used):
        if char == '\n':
            char = 'ENTER'

        if char.isspace():
            char = "SPACE"

        time_word = self.timestamp - self.time_word
        time_sentence = self.timestamp - self.time_sentence
        time_complete = self.timestamp - self.time_complete
        text = self.typed_sentences + sentence

        log_string = event_name + ',"' + char + '"' + ',' + str(self.timestamp)
        log_string += ',"' + str(word) + '",' + str(time_word)
        log_string += ',"' + str(sentence) + '",' + str(time_sentence)
        log_string += ',"' + str(text) + '",' + str(time_complete)
        log_string += ',' + str(task_num) + ',' + str(technique_used)
        log_string += ',' + str(self.completion) + ',' + str(self.participant_id)
        print(log_string)

        self.last_char = char

    def finished_experiment(self):
        self.write_log_entry('test finished', '', '', '', '', '')


class Experiment(QWidget):
    # trigger for changed input
    input_trigger = QtCore.pyqtSignal(str, float)

    def __init__(self, logging, sentences, filename):
        super(QWidget, self).__init__()
        self.screen_width = 700
        self.screen_height = 400
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setMouseTracking(True)
        self.setWindowTitle('Typing Experiment')
        self.setGeometry(0, 0, self.screen_width, self.screen_height)
        self.show()
        self.logging = logging
        self.sentences = sentences
        self.current_task = 0
        self.setup_elements(filename)

    # sets up the layout with the elements
    def setup_elements(self, filename):
        layout = QVBoxLayout()
        self.input_trigger.connect(self.log)
        self.show_text = QTextEdit()
        self.show_text.setReadOnly(True)

        self.input_text = TextEditTechnique(filename, self.input_trigger, self.logging.completion)
        layout.addWidget(self.show_text)
        layout.addWidget(self.input_text)
        self.setLayout(layout)
        self.show_next(True)

    # logs the input
    def log(self, text, timestamp):
        finished_sentence, reset_technique = self.logging.loginput(text, timestamp, self.current_task,
                                                                   self.input_text.technique_used)
        if reset_technique:
            self.input_text.technique_used = False
        self.show_next(finished_sentence)

    # shows next sentence, exits the application if done
    def show_next(self, finished_sentence, reset_technique=False):
        if finished_sentence:
            if len(self.sentences) == self.current_task:
                self.logging.finished_experiment()
                exit()
            self.current_task += 1
            self.show_text.setText(self.sentences[self.current_task - 1])
            self.input_text.clear_input()


# reads the senteces form file
def read_text_form_file(filename):
    sentences = []
    file = open(filename)
    for line in file:
        sentences.append(line)
    file.close()
    random.shuffle(sentences)
    return sentences


# starts the application
def main():
    app = QApplication(sys.argv)
    filename = 'text.txt'
    completion = True
    participant_id = 1
    sentences = read_text_form_file(filename)
    logging = Logging(participant_id, completion)
    # widget is magic
    widget = Experiment(logging, sentences, filename)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
