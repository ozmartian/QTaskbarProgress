#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from qtaskbarprogress import QTaskbarProgress


class Widget(QWidget):
    def __init__(self, parent=None):
        super(Widget, self).__init__(parent)

        self.taskbar = QTaskbarProgress(self)

        self.progressCheckBox = QCheckBox(self)
        self.progressCheckBox.setText('Progress Bar:')
        self.progressCheckBox.setCursor(Qt.PointingHandCursor)
        self.progressSlider = QSlider(Qt.Horizontal, self)
        self.progressSlider.setRange(0, 100)
        self.progressSlider.setCursor(Qt.PointingHandCursor)

        self.counterCheckBox = QCheckBox(self)
        self.counterCheckBox.setText('Progress Counter:')
        self.counterCheckBox.setCursor(Qt.PointingHandCursor)
        self.counterSpinBox = QSpinBox(self)
        self.counterSpinBox.setWrapping(True)
        self.counterSpinBox.setButtonSymbols(QAbstractSpinBox.PlusMinus)
        self.counterSpinBox.setAccelerated(True)
        self.counterSpinBox.setCursor(Qt.PointingHandCursor)

        desktopFileLabel = QLabel('Desktop File:', self)
        self.desktopFileInput = QLineEdit(self)
        self.desktopFileInput.setReadOnly(True)
        self.desktopFileInput.setText(self.taskbar.desktopFilename())

        desktopFileLayout = QVBoxLayout()
        desktopFileLayout.setSpacing(5)
        desktopFileLayout.addWidget(desktopFileLabel)
        desktopFileLayout.addWidget(self.desktopFileInput)

        layout = QFormLayout()
        layout.setSpacing(20)
        layout.setLabelAlignment(Qt.AlignLeft)
        layout.addRow(self.progressCheckBox, self.progressSlider)
        layout.addRow(self.counterCheckBox, self.counterSpinBox)
        layout.addRow(desktopFileLayout)

        self.progressCheckBox.clicked.connect(self.taskbar.setProgressVisible)
        self.counterCheckBox.clicked.connect(self.taskbar.setCounterVisible)
        self.counterSpinBox.valueChanged.connect(self.taskbar.setCounter)
        self.progressSlider.valueChanged.connect(self.taskbar.setProgress)
        self.taskbar.errorOccurred.connect(lambda error: QMessageBox.critical(self, 'Error', error))

        self.setLayout(layout)
        self.setWindowIcon(self.style().standardIcon(QStyle.SP_TitleBarMenuButton))
        self.setMinimumWidth(600)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('QTaskbarProgressDemo')
    widget = Widget()
    widget.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
