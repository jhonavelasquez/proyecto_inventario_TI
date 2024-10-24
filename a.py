import mysql.connector

print("Iniciando la conexión a la base de datos...")
try:
    conn = mysql.connector.connect(
        host='127.0.0.1',
        port='3306',
        database='sistemas_computadores_ddi',
        user='root',
        password=''
    )
    if conn.is_connected():
        print("Conectado a la base de datos.")
    else:
        print("No se pudo conectar a la base de datos.")
except mysql.connector.Error as err:
    print(f"Error al conectar a MySQL: {err}")
except Exception as e:
    print(f"Se produjo un error inesperado: {e}")
finally:
    if conn and conn.is_connected():
        conn.close()
