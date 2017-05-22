#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from PyQt5.QtWidgets import QApplication

from qtaskbarprogress import QTaskbarProgress


app = QApplication(sys.argv)
app.setApplicationName('QTaskbarProgress Demo')
taskbar = QTaskbarProgress()
taskbar.setProgressVisible(True)
taskbar.setProgress(50.0)
