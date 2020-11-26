import sshtunnel, mysql.connector


def ssh_connection(ssh_timeout, tunnel_timeout, ssh_address, ssh_user, ssh_password, bind_address, bind_port):
    """Создаем подключение через ssh тунель. Необходимоинтернет соединение"""
    sshtunnel.SSH_TIMEOUT = ssh_timeout
    sshtunnel.TUNNEL_TIMEOUT = tunnel_timeout

    try:
        tunnel = sshtunnel.SSHTunnelForwarder(
            (ssh_address),
            ssh_username=ssh_user, ssh_password=ssh_password,
            remote_bind_address=(bind_address, bind_port))
        tunnel.start()
    except sshtunnel.BaseSSHTunnelForwarderError as err:
        print("Ошибка при создании ssh тунеля\n" + err)
    else:
        return True, tunnel


def db_connection(db_user, db_password, db_host, local_port, db_name):
    """Подключение к удаленной базе данных"""
    try:
        connection = mysql.connector.connect(
            user=db_user, password=db_password,
            host=db_host, port=local_port,
            database=db_name)
    except mysql.connector.Error as err:
        print("Проблемы с подключением к базе двнных\n" + err)
    else:
        return connection


def db_update(connection, table_name, field, value):
    """Операция изменения таблицы"""
    cursor = connection.cursor()
    cursor.execute('update {} set {} = {}'.format(table_name, field, value))
    connection.commit()
    connection.close()


def receive_signal_value(connection, table):
    """Получение значений сигнала из таблицы"""
    cursor = connection.cursor()
    cursor.execute('select * from {}'.format(table))
    signal = cursor.fetchall()
    if signal:
        cursor.execute('delete from {}'.format(signal))
        connection.commit()
    return signal
