#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QDir, QFile, QStandardPaths, QUuid
from PyQt5.QtDBus import QDBusConnection, QDBusMessage
from PyQt5.QtWidgets import QApplication, QWidget


class QTaskbarProgress(QWidget):
    counterChanged = pyqtSignal(int)
    counterVisibleChanged = pyqtSignal(bool)
    progressChanged = pyqtSignal(float)
    progressVisibleChanged = pyqtSignal(bool)
    errorOccurred = pyqtSignal(str)

    _desktopFile = QFile()

    msgPath = '/com/ozmartians/QTaskbarProgress'
    msgInterface = 'com.canonical.Unity.LauncherEntry'
    msgName = 'Update'

    def __init__(self):
        super(QTaskbarProgress, self).__init__()
        if not sys.platform.startswith('linux'):
            self.errorOccurred.emit('QTaskbarProgress only works with KDE and Unity desktops on Linux!')
            print('QTaskbarProgress only works with KDE and Unity desktops on Linux!')
            return
        QTaskbarProgress._initDesktopFile()

    def __del__(self):
        if self._desktopFile.exists():
            self._desktopFile.remove()

    @pyqtSlot(bool)
    def setProgressVisible(self, visible: bool):
        self._sendMessageAttribute('progress-visible', visible)
        self.progressVisibleChanged.emit(visible)

    @pyqtSlot(float)
    def setProgress(self, progress: float):
        self._sendMessageAttribute('progress', progress)
        self.progressChanged.emit(progress)

    @pyqtSlot(bool)
    def setCounterVisible(self, visible: bool):
        self._sendMessageAttribute('count-visible', visible)
        self.counterVisibleChanged.emit(visible)

    @pyqtSlot(int)
    def setCounter(self, counter: int):
        QTaskbarProgress._sendMessageAttribute('count', counter)
        self.counterChanged.emit(counter)

    @staticmethod
    def _initDesktopFile():
        name = '%s.desktop' % QUuid.createUuid().toString()
        appDir = QDir(QStandardPaths.writableLocation(QStandardPaths.ApplicationsLocation))
        QTaskbarProgress._desktopFile = QFile(appDir.absoluteFilePath(name))
        if not QTaskbarProgress._desktopFile.exists():
            QTaskbarProgress._desktopFile.open(QFile.WriteOnly)
            QTaskbarProgress._desktopFile.write(b'[Desktop Entry]\n')
            QTaskbarProgress._desktopFile.write(b'Type=Application\n')
            QTaskbarProgress._desktopFile.write(b'Version=1.1\n')
            QTaskbarProgress._desktopFile.write(b'Name=' + QApplication.applicationName().encode() + b'\n')
            QTaskbarProgress._desktopFile.write(b'Exec=' + QApplication.applicationFilePath().encode() + b'\n')
            QTaskbarProgress._desktopFile.close()
        QTaskbarProgress._sendReset()

    @staticmethod
    def _sendReset():
        props = {
            'progress-visible': True,
            'progress': 0.0,
            'count-visible': False,
            'count': 0
        }
        QTaskbarProgress._sendMessage(props)

    @staticmethod
    def _sendMessage(params: dict):
        if not QTaskbarProgress._desktopFile.exists():
            QTaskbarProgress._initDesktopFile()
        message = QDBusMessage.createSignal(QTaskbarProgress.msgPath, QTaskbarProgress.msgInterface,
                                            QTaskbarProgress.msgName)
        message << 'application://%s' % QTaskbarProgress._desktopFile << params
        QDBusConnection.sessionBus().send(message)

    @staticmethod
    def _sendMessageAttribute(key: str, value: any):
        QTaskbarProgress._sendMessage({key: value})
