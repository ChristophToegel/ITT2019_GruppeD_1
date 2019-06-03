from PyQt5.QtCore import Qt, QStringListModel
from PyQt5.QtGui import QKeySequence, QTextCursor
from PyQt5.QtWidgets import QLineEdit, QCompleter, QTextEdit, QDirModel


# https://stackoverflow.com/questions/28956693/pyqt5-qtextedit-auto-completion
# https://github.com/baoboa/pyqt5/blob/master/examples/tools/customcompleter/customcompleter.py
# https://doc.qt.io/qtforpython/PySide2/QtWidgets/QCompleter.html
# https://doc.qt.io/qt-5/qtwidgets-tools-customcompleter-example.html
# https://www.programcreek.com/python/example/108066/PyQt5.QtWidgets.QCompleter

class TextEditCom(QTextEdit):
    def __init__(self, text_file):
        super(TextEditCom, self).__init__()
        self._completer = None
        self.isActive = True
        word_list = self.get_suggestion_words(text_file)
        self.char_length = 0
        self.initCompletor(word_list)

    def initCompletor(self, words):
        completer = QCompleter(words, self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setWrapAround(False)
        self.setCompleter(completer)

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

    def setCompleter(self, c):
        if self._completer is not None:
            self._completer.activated.disconnect()

        self._completer = c
        c.setWidget(self)
        c.setCompletionMode(QCompleter.PopupCompletion)
        c.setCaseSensitivity(Qt.CaseInsensitive)
        c.activated.connect(self.insertCompletion)

    def completer(self):
        return self._completer

    def insertCompletion(self, completion):
        if self._completer.widget() is not self:
            return
        tc = self.textCursor()
        extra = len(completion) - len(self._completer.completionPrefix())
        tc.movePosition(QTextCursor.Left)
        tc.movePosition(QTextCursor.EndOfWord)
        tc.insertText(completion[-extra:])
        self.setTextCursor(tc)

    def textUnderCursor(self):
        tc = self.textCursor()
        tc.select(QTextCursor.WordUnderCursor)
        return tc.selectedText()

    def focusInEvent(self, e):
        if self._completer is not None:
            self._completer.setWidget(self)
        super(TextEditCom, self).focusInEvent(e)

    def keyPressEvent(self, e):
        if self._completer is not None and self._completer.popup().isVisible():
            # The following keys are forwarded by the completer to the widget.
            if e.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Escape, Qt.Key_Tab, Qt.Key_Backtab):
                e.ignore()
                # Let the completer do default behavior.
                return

        if self._completer is None or self.isActive:
            # Do not process the shortcut when we have a completer.
            super(TextEditCom, self).keyPressEvent(e)

        ctrlOrShift = e.modifiers() & (Qt.ControlModifier | Qt.ShiftModifier)
        if self._completer is None or (ctrlOrShift and len(e.text()) == 0):
            return

        eow = "~!@#$%^&*()_+{}|:\"<>?,./;'[]\\-="
        hasModifier = (e.modifiers() != Qt.NoModifier) and not ctrlOrShift
        completionPrefix = self.textUnderCursor()

        if self.isActive and (
                hasModifier or len(e.text()) == 0 or len(completionPrefix) < self.char_length or e.text()[-1] in eow):
            self._completer.popup().hide()
            return

        if completionPrefix != self._completer.completionPrefix():
            self._completer.setCompletionPrefix(completionPrefix)
            self._completer.popup().setCurrentIndex(
                self._completer.completionModel().index(0, 0))

        cr = self.cursorRect()
        cr.setWidth(self._completer.popup().sizeHintForColumn(
            0) + self._completer.popup().verticalScrollBar().sizeHint().width())
        self._completer.complete(cr)
