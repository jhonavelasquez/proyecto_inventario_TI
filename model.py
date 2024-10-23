import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host='127.0.0.1',
            port='3306',
            database='sistemas_computadores_ddi',
            user='root',
            password=''
        )

        if conn.is_connected():
            return conn
    except mysql.connector.Error as err:
        print(f"Error al conectar a MySQL: {err}")
        return None

class Usuario:
    def __init__(self, id_usuario, nombre_user, email, psw, id_tipo_usuario):
        self.id = id_usuario
        self.nombre_usuario = nombre_user
        self.email = email
        self.password = psw
        self.id_tipo_usuario = id_tipo_usuario

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    @staticmethod
    def get_by_id(id_usuario):
        conn = get_db_connection()

        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Usuario WHERE Id_usuario = %s', (id_usuario,))
        user = cursor.fetchone()
        conn.close()
        if user:
            return Usuario(
                user[0],  # Asumiendo que 'Id_usuario' es la primera columna
                user[1],  # 'Nombre_user'
                user[2],  # 'Email'
                user[3],  # 'Psw'
                user[4]   # 'id_tipo_usuario'
            )
        return None

    @staticmethod
    def get_by_email(email):
        conn = get_db_connection()
        user_data = conn.cursor(dictionary=True)
        user_data.execute('SELECT * FROM Usuario WHERE Email = %s', (email,))
        user = user_data.fetchone()
        conn.close()
        if user:
            return Usuario(
                user['Id_usuario'], 
                user['Nombre_user'], 
                user['Email'], 
                user['Psw'],
                user['id_tipo_usuario']
            )
        return None

    @staticmethod
    def get_by_nombre_usuario(nombre_usuario):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Usuario WHERE Nombre_user = %s", (nombre_usuario,))
        usuario = cursor.fetchone()
        conn.close()

        if usuario:
            return Usuario(
                usuario[0], 
                usuario[1], 
                usuario[2], 
                usuario[3],
                usuario[4]
            )
        
        return None

    
    @staticmethod
    def get_by_id_with_tipo_usuario(id_usuario):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)  # Usar cursor con diccionario
        query = '''
        SELECT u.*, t.nombre_tipo_usuario 
        FROM Usuario u 
        JOIN Tipo_usuario t ON u.id_tipo_usuario = t.id_tipo_usuario 
        WHERE u.Id_usuario = %s
        '''
        cursor.execute(query, (id_usuario,))
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data:
            return {
                'id_usuario': user_data['Id_usuario'],
                'nombre_usuario': user_data['Nombre_user'],
                'email': user_data['Email'],
                'id_tipo_usuario': user_data['id_tipo_usuario'],
                'nombre_tipo_usuario': user_data['nombre_tipo_usuario'] 
            }
        return None
