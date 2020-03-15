#!./venv/bin/python
# -*- coding: utf-8 -*-

import time

from PyQt5.QtCore import QThread, pyqtSignal


class UpdateWindowThread(QThread):
    '''Thread updates a text of a text browser'''
    signal = pyqtSignal(str)
    def __init__(self):
        QThread.__init__(self)
        self.communicator = None
        
    def run(self):
        while True:
            if self.communicator.new_message():
               self.signal.emit(self.communicator.received_text())
        
            
    def __del__(self):
        self.wait()
