#!./venv/bin/python
# -*- coding: utf-8 -*-

import sys

from client.main_window import MainWindow, QApplication


#Start the client app

app = QApplication(sys.argv)
window = MainWindow()
window.show()

sys.exit(app.exec_())
