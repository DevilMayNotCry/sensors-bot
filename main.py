import sys
from PyQt5.QtWidgets import QApplication
from .client import MainWindow, SignalThread, ClientThread


def new_signal_thread():
    signal_thread = SignalThread()
    signal_thread.start()


def new_client_thread(value):
    client_thread = ClientThread(value)
    client_thread.start()


qApp = QApplication(sys.argv)
qWin = MainWindow()
qWin.show()
sys.exit(qApp.exec_())
