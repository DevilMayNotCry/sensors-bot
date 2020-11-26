import socket


def tcp_connection(ip, port):
    """Процесс соединения с платой"""
    tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_client.connect((ip, port))
    return tcp_client


def send_data(tcp_client, value):
    """Отправление сигнала на плату"""
    tcp_client.send(bytes(str(value), 'utf-8'))


def receive_data(tcp_client, buffer_size):
    """Получение значений датчиков от платы"""
    data = True
    string = ''
    while data:
        data = tcp_client.recv(buffer_size)
        if data == b'\r\n':
            return string
        string += data.decode("utf-8")
