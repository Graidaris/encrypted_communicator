#!./venv/bin/python
# -*- coding: utf-8 -*-

import os
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow

from client.thread_uw import UpdateWindowThread
from client.ui.main_window import Ui_MainWindow
from communicator.communicator import Communicator


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.communicator = None
        self.__connect_buttons()
        self.__update_thred = UpdateWindowThread()
        self.__update_thred.signal.connect(self.__update)
        
        
    def __connect_buttons(self):
        self.ui.pushButtonStart.clicked.connect(self._start)
        self.ui.pushButtonConnect.clicked.connect(self._connect)
        self.ui.sendButton.clicked.connect(self._send_message)
        self.ui.browsButton.clicked.connect(self.open_dialog)

    def _start(self):
        port = self.ui.textEditMyPort.toPlainText()
        self.communicator = Communicator(int(port))
        self.communicator.start_listen()
        
        self.__update_thred.communicator = self.communicator
        self.__update_thred.start()
        
    def _connect(self):
        ip = self.ui.textEditConnectAdress.toPlainText()
        port = self.ui.textEditConnectPort.toPlainText()
        self.communicator.connect(ip, int(port))    
        
    def _send_message(self):
        text = self.ui.messageBoxEd.toPlainText()
        self.communicator.send_message(text.strip())
        
    def open_dialog(self):
        pass
        
    def __update(self, text):
        '''Update the text browser UI'''
        self.ui.textBrowser.append(text)
        
    def closeEvent(self, event):
        '''Method was called when X is clicked '''
        self.communicator.stop_listen()
        event.accept()
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
