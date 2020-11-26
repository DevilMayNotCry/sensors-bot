#!/usr/bin/python3
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QAction, QComboBox,  QProgressBar
from PyQt5.QtCore import QTimer, Qt, QThread
from PyQt5.QtGui import QFont, QPainter, QColor, QPen, QIcon
from threading import Thread
import settings
from .internet import ssh_connection, db_update, db_connection, receive_signal_value
from .sensor import tcp_connection, send_data, receive_data
from .main import qWin, new_signal_thread, new_client_thread


class ClientThread(Thread):
    def __init__(self, value):
        Thread.__init__(self)
        self.value = value
        self.tunnelStatus = False

    def run(self):

        self.tunnelStatus, tunnel = ssh_connection(settings.SSH_TIMEOUT, settings.TUNNEL_TIMEOUT,
                                                   settings.SSH_ADDRESS, settings.SSH_USER,
                                                   settings.SSH_PASSWORD, settings.BIND_ADDRESS, settings.BIND_PORT)
        tcp_client = tcp_connection(settings.IP, settings.PORT)
        send_data(tcp_client, self.value)
        received_data = receive_data(tcp_client, settings.BUFFER_SIZE)
        if self.value == 1:
            qWin.lb1.setText(str(received_data))
            if self.tunnelStatus:
                connection = db_connection(settings.DB_USER, settings.DB_PASSWORD, settings.HOST, tunnel.local_bind_port, settings.DB_NAME)
                table = 'Temp'
                field = 't1'
                db_update(connection, table, field, received_data)
        elif self.value == 2:
            qWin.lb2.setText(str(received_data))
            if self.tunnelStatus:
                connection = db_connection(settings.DB_USER, settings.DB_PASSWORD, settings.HOST, settings.DB_NAME)
                table = 'Temp'
                field = 't1'
                db_update(connection, table, field, received_data)
        else:
            data = round((210 - float(received_data)) * 0.052, 1)
            qWin.lb3.setText(str(data))
            qWin.pbar.setValue(data)
            if self.tunnelStatus:
                connection = db_connection(settings.DB_USER, settings.DB_PASSWORD, settings.HOST, settings.DB_NAME)
                table = 'Temp'
                field = 'v'
                db_update(connection, table, field, data)
        tcp_client.close()
        tunnel.close()
        return


class SignalThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.tunnelStatus = False
        self.signal = None

    def run(self):
        self.tunnelStatus, tunnel = ssh_connection(settings.SSH_TIMEOUT, settings.TUNNEL_TIMEOUT,
                                                   settings.SSH_ADDRESS, settings.SSH_USER,
                                                   settings.SSH_PASSWORD, settings.BIND_ADDRESS, settings.BIND_PORT)

        if self.tunnelStatus:
            connection = db_connection(settings.DB_USER, settings.DB_PASSWORD, settings.HOST, tunnel.local_bind_port, settings.DB_NAME)
            self.signal = receive_signal_value(connection, 'signals')
            connection.close()
            tunnel.close()
        return


class MainWindow(QMainWindow):
    """Графический дизайн приложения"""
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("Water")
        self.setWindowIcon(QIcon('water.png'))
        self.lb1 = QLabel(self)
        self.lb1.setText('Sensor_1')
        self.lb1.setFont(QFont('SansSerif', 46))
        self.lb1.setGeometry(90, 50, 400, 200)
        self.lb2 = QLabel(self)
        self.lb2.setText('Sensor_2')
        self.lb3 = QLabel(self)
        self.lb3.setText('Sensor_3')
        self.lb2.setFont(QFont('SansSerif', 46))
        self.lb3.setFont(QFont('SansSerif', 46))
        self.lb2.setGeometry(90, 200, 400, 100)
        self.lb3.setGeometry(90, 350, 400, 100)
        self.lb_1 = QLabel(self)
        self.lb_2 = QLabel(self)
        self.lbl_1 = QLabel(self)
        self.lbl_2 = QLabel(self)
        self.lbl_3 = QLabel(self)
        self.lb_1.setGeometry(200, 30, 120, 50)
        self.lb_2.setGeometry(250, 300, 100, 50)
        self.lbl_1.setGeometry(250, 120, 100, 50)
        self.lbl_2.setGeometry(250, 220, 100, 50)
        self.lbl_3.setGeometry(250, 370, 100, 50)
        self.lb_1.setFont(QFont('Counter', 14))
        self.lb_2.setFont(QFont('Counter', 16))
        self.lbl_1.setFont(QFont('Arial', 16))
        self.lbl_2.setFont(QFont('Arial', 16))
        self.lbl_3.setFont(QFont('Arial', 16))
        self.lb_1.setText('Температура')
        self.lb_2.setText('Объем')
        self.lbl_1.setText('°C')
        self.lbl_2.setText('°C')
        self.lbl_3.setText('куб.м')
        self.pbar = QProgressBar(self)
        self.pbar.setGeometry(40, 470, 270, 45)
        self.pbar.setFormat("%v/%m")
        self.pbar.setRange(0, 10)

        # Кнопка выхода
        exit_btn = QPushButton('Выход', self)
        exit_btn.resize(exit_btn.sizeHint())
        exit_btn.move(150, 580)
        exit_btn.clicked.connect(QApplication.instance().quit)

        # Создаем таймер для постоянного опроса датчиков
        self.tmp = 0
        self.qTimer = QTimer()
        self.qTimer.setInterval(30000)  # 1/000 ms = 1 s
        self.qTimer.timeout.connect(self.getSensorValue)
        self.qTimer.start()

        self.setGeometry(100, 100, 340, 610)

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawRectangles(qp)
        self.drawLines(qp)
        qp.end()

    def drawRectangles(self, qp):
        col = QColor(0, 0, 0)
        col.setNamedColor('#d4d4d4')
        qp.setPen(col)
        qp.setBrush(QColor(100, 100, 100, 100))
        qp.drawRect(0, 0, 1200, 800)

    def drawLines(self, qp):
        pen = QPen(Qt.white, 2, Qt.SolidLine)
        qp.setPen(pen)
        qp.drawRect(20, 40, 300, 500)

    def getSensorValue(self):
        new_client_thread(1)
        new_client_thread(2)
        new_client_thread(3)
        new_signal_thread()

