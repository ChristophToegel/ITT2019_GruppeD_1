from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QCompleter, QTextEdit
import time

'''
Workload distribution among team:
    Christoph: get_suggestion_words, set_completer, deactivate_completer,activate_completer
    Julian: insert_sel_suggestion,text_under_cursor,focusInEvent,keyPressEvent,clear_input,handle_input
'''


# https://stackoverflow.com/questions/28956693/pyqt5-qtextedit-auto-completion
# https://github.com/baoboa/pyqt5/blob/master/examples/tools/customcompleter/customcompleter.py
# https://doc.qt.io/qtforpython/PySide2/QtWidgets/QCompleter.html
# https://doc.qt.io/qt-5/qtwidgets-tools-customcompleter-example.html
# https://www.programcreek.com/python/example/108066/PyQt5.QtWidgets.QCompleter

class TextEditTechnique(QTextEdit):

    def __init__(self, text_file, input_trigger=None, active=True):
        super(TextEditTechnique, self).__init__()
        self._completer = None
        self.isActive = active
        word_list = self.get_suggestion_words(text_file)
        self.input_trigger = input_trigger
        # connects the text textChanged event
        self.textChanged.connect(self.handle_input)
        self.char_length = 1
        self.set_completer(word_list)
        self.technique_used = False
        self.no_suggestion_input = "~!@#$%^&*()_+{}|:\"<>?,./;'[]\\-= "

    # gets words for suggestion
    def get_suggestion_words(self, text_file):
        words = []
        file = open(text_file)
        for line in file:
            for word in line.split(' '):
                word = word.strip().lower().replace('.', '').replace(',', '').replace('.', '').replace('?', '')
                if word and word not in words:
                    words.append(word)
        file.close()
        return words

    # initializes the completer
    def set_completer(self, words):
        if self._completer is not None:
            self._completer.activated.disconnect()
        self._completer = QCompleter(words, self)
        self._completer.setCaseSensitivity(Qt.CaseInsensitive)
        self._completer.setWrapAround(False)
        self._completer.setWidget(self)
        self._completer.setCompletionMode(QCompleter.PopupCompletion)
        self._completer.activated.connect(self.insert_sel_suggestion)

    # insert the selected suggestion and moves the text cursor
    def insert_sel_suggestion(self, suggestion):
        if self._completer.widget() is not self:
            return
        text_cursor = self.textCursor()
        extra = len(suggestion) - len(self._completer.completionPrefix())
        text_cursor.movePosition(QTextCursor.Left)
        text_cursor.movePosition(QTextCursor.EndOfWord)
        text_cursor.insertText(suggestion[-extra:])
        self.setTextCursor(text_cursor)

    # returns the current typed word
    def text_under_cursor(self):
        text_cursor = self.textCursor()
        text_cursor.select(QTextCursor.WordUnderCursor)
        return text_cursor.selectedText()

    # sets the widget
    def focusInEvent(self, e):
        if self._completer is not None and self.isActive:
            self._completer.setWidget(self)
        super(TextEditTechnique, self).focusInEvent(e)

    def keyPressEvent(self, e):

        # behaves like a normal input field!
        if not self.isActive or self._completer is None:
            super(TextEditTechnique, self).keyPressEvent(e)
            return

        # ignore events funktion keys on Textedit if popup is visible --> popup behaves default
        if self._completer.popup().isVisible():
            if e.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Escape, Qt.Key_Tab, Qt.Key_Backtab):
                e.ignore()
                self.technique_used = True
                return
        # wirtes text in the editfield
        super(TextEditTechnique, self).keyPressEvent(e)

        ctrl_or_shift = e.modifiers() & (Qt.ControlModifier | Qt.ShiftModifier)
        if self._completer is None or (ctrl_or_shift and len(e.text()) == 0):
            return

        has_modifier = (e.modifiers() != Qt.NoModifier) and not ctrl_or_shift
        completion_prefix = self.text_under_cursor()
        # hide the popup for no chars, modifiers, shift and no text
        if (has_modifier or len(e.text()) == 0 or len(completion_prefix) < self.char_length
                or e.text()[-1] in self.no_suggestion_input):
            self._completer.popup().hide()
            return

        # shows the popup with the suggested words
        if completion_prefix != self._completer.completionPrefix():
            self._completer.setCompletionPrefix(completion_prefix)
            self._completer.popup().setCurrentIndex(self._completer.completionModel().index(0, 0))

        cursor = self.cursorRect()
        cursor.setWidth(self._completer.popup().sizeHintForColumn(
            0) + self._completer.popup().verticalScrollBar().sizeHint().width())
        self._completer.complete(cursor)

    # event called if textedit input has changed
    def handle_input(self):
        timestamp = time.time()
        self.input_trigger.emit(self.toPlainText(), timestamp)

    # clears the text input
    def clear_input(self):
        self.setHtml('')

    # deactivates the completer
    def deactivate_completer(self):
        self.isActive = False

    # activates the completer
    def activate_completer(self):
        self.isActive = True
