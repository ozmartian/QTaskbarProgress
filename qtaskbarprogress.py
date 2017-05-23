#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QDir, QFile, QProcess, QProcessEnvironment, QStandardPaths, QUuid
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtDBus import QDBusConnection, QDBusMessage
from PyQt5.QtWidgets import QApplication, QWidget


class QTaskbarProgress(QWidget):
    counterChanged = pyqtSignal(int)
    counterVisibleChanged = pyqtSignal(bool)
    progressChanged = pyqtSignal(float)
    progressVisibleChanged = pyqtSignal(bool)
    errorOccurred = pyqtSignal(str)

    _desktopFile = QFile()

    msgPath = '/'
    msgInterface = 'com.canonical.Unity.LauncherEntry'
    msgName = 'Update'

    errorTxt = 'QTaskbarProgress only works with KDE and Unity desktops on Linux!'

    def __init__(self, parent=None):
        super(QTaskbarProgress, self).__init__(parent)
        if not sys.platform.startswith('linux'):
            self.errorOccurred.emit(QTaskbarProgress.errorTxt)
            sys.stderr.write(QTaskbarProgress.errorTxt)
            return
        if self.checkEnvironment() and self.checkDBus():
            self._initDesktopFile()
        else:
            self.errorOccurred.emit(QTaskbarProgress.errorTxt)
            sys.stderr.write(QTaskbarProgress.errorTxt)
            return

    def __del__(self):
        if self._desktopFile.exists():
            self._desktopFile.remove()

    def checkEnvironment(self):
        proc = QProcess(self)
        proc.setProcessEnvironment(QProcessEnvironment.systemEnvironment())
        proc.setWorkingDirectory(QDir.homePath())
        if hasattr(proc, 'errorOccurred'):
            self.errorOccurred.emit(proc.errorString())
            sys.stderr.write(proc.errorString())
            return False
        if proc.state() == QProcess.NotRunning:
            proc.setProcessChannelMode(QProcess.MergedChannels)
            results = {'unity': None, 'ksmserver': None}
            for de in ('unity', 'ksmserver'):
                proc.start('pidof', [de])
                proc.waitForFinished(-1)
                results[de] = str(proc.readAllStandardOutput().data(), 'utf-8').replace('\n', '')
            for key in results:
                if results.get(key).isdigit():
                    return True
        return False

    def checkDBus(self):
        if not QDBusConnection.sessionBus().isConnected():
            sys.stderr.write("Cannot connect to the D-Bus session bus.\n"
                             "To start it, run:\n"
                             "\teval `dbus-launch --auto-syntax`\n");

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

    def desktopFilename(self):
        return self._desktopFile.fileName()

    def _initDesktopFile(self):
        name = '%s.desktop' % QUuid.createUuid().toString()
        appDir = QDir(QStandardPaths.writableLocation(QStandardPaths.ApplicationsLocation))
        self._desktopFile = QFile(appDir.absoluteFilePath(name))
        if not self._desktopFile.exists():
            self._desktopFile.open(QFile.WriteOnly)
            self._desktopFile.write(b'[Desktop Entry]\n')
            self._desktopFile.write(b'Type=Application\n')
            self._desktopFile.write(b'Version=1.1\n')
            self._desktopFile.write(b'Name=' + QApplication.applicationName().encode() + b'\n')
            self._desktopFile.write(b'Exec=' + QApplication.applicationFilePath().encode() + b'\n')
            self._desktopFile.close()
        self._sendReset()

    def _sendReset(self):
        props = {
            'progress-visible': True,
            'progress': 0.0,
            'count-visible': False,
            'count': 0
        }
        self._sendMessage(props)

    def _sendMessage(self, params: dict):
        if not self._desktopFile.exists():
            self._initDesktopFile()
        message = QDBusMessage.createSignal(QTaskbarProgress.msgPath, QTaskbarProgress.msgInterface,
                                            QTaskbarProgress.msgName)
        message << 'application://%s' % self._desktopFile << params
        print(message)
        QDBusConnection.sessionBus().send(message)

    def _sendMessageAttribute(self, key: str, value: any):
        self._sendMessage({key: value})
