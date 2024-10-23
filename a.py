import mysql.connector
from mysql.connector import Error

try:
    conn = mysql.connector.connect(
        host='127.0.0.1',
        port='3306',
        database='sistemas_computadores_ddi',
        user='root',
        password=''
    )
    if conn.is_connected():
        print('Conectado a MySQL')
    conn.close()
except Error as e:
    print(f"Error al conectar: {e}")
