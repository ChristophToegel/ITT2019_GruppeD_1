from PyQt5.QtCore import Qt, QStringListModel
from PyQt5.QtGui import QKeySequence, QTextCursor
from PyQt5.QtWidgets import QLineEdit, QCompleter, QTextEdit, QDirModel
import time

# https://stackoverflow.com/questions/28956693/pyqt5-qtextedit-auto-completion
# https://github.com/baoboa/pyqt5/blob/master/examples/tools/customcompleter/customcompleter.py
# https://doc.qt.io/qtforpython/PySide2/QtWidgets/QCompleter.html
# https://doc.qt.io/qt-5/qtwidgets-tools-customcompleter-example.html
# https://www.programcreek.com/python/example/108066/PyQt5.QtWidgets.QCompleter

class TextEditTechnique(QTextEdit):
    def __init__(self, text_file,input_trigger=None,active=True):
        super(TextEditTechnique, self).__init__()
        self._completer = None
        self.isActive = active
        word_list = self.get_suggestion_words(text_file)
        self.input_trigger = input_trigger
        self.textChanged.connect(self.handle_input)
        self.char_length = 1
        self.set_completer(word_list)
        self.eow = "~!@#$%^&*()_+{}|:\"<>?,./;'[]\\-= "


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

    def deactivate_completer(self):
        self.isActive = False

    def set_completer(self, words):
        if self._completer is not None:
            self._completer.activated.disconnect()
        self._completer= QCompleter(words, self)
        self._completer.setCaseSensitivity(Qt.CaseInsensitive)
        self._completer.setWrapAround(False)
        self._completer.setWidget(self)
        self._completer.setCompletionMode(QCompleter.PopupCompletion)
        self._completer.activated.connect(self.insert_sel_suggestion)

    #def completer(self):
    #    return self._completer

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

    def textUnderCursor(self):
        text_cursor = self.textCursor()
        text_cursor.select(QTextCursor.WordUnderCursor)
        return text_cursor.selectedText()

    def focusInEvent(self, e):
        if self._completer is not None and self.isActive:
            self._completer.setWidget(self)
        super(TextEditTechnique, self).focusInEvent(e)

    def keyPressEvent(self, e):
        # behaves like a normal input field!
        if not self.isActive or self._completer is None:
            super(TextEditTechnique, self).keyPressEvent(e)
            return

        # ignore events funktion keys if popup().isVisible() --> popup behaves default
        if self._completer.popup().isVisible():
            if e.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Escape, Qt.Key_Tab, Qt.Key_Backtab):
                e.ignore()
                return

        super(TextEditTechnique, self).keyPressEvent(e)

        ctrlOrShift = e.modifiers() & (Qt.ControlModifier | Qt.ShiftModifier)
        if self._completer is None or (ctrlOrShift and len(e.text()) == 0):
            return

        has_modifier = (e.modifiers() != Qt.NoModifier) and not ctrlOrShift
        completion_prefix = self.textUnderCursor()

        if (has_modifier or len(e.text()) == 0 or len(completion_prefix) < self.char_length or e.text()[-1] in self.eow):
            self._completer.popup().hide()
            return

        if completion_prefix != self._completer.completionPrefix():
            self._completer.setCompletionPrefix(completion_prefix)
            self._completer.popup().setCurrentIndex(self._completer.completionModel().index(0, 0))

        cursor = self.cursorRect()
        cursor.setWidth(self._completer.popup().sizeHintForColumn(
            0) + self._completer.popup().verticalScrollBar().sizeHint().width())
        self._completer.complete(cursor)

    def handle_input(self):
        timestamp = time.time()
        self.input_trigger.emit(self.toPlainText(), timestamp)

    def clear_input(self):
        self.setHtml('')
