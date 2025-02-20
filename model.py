
import sqlite3


def get_db_connection():
    try:
        print("Intentando conectar...")
        conn = sqlite3.connect('database.db')
        print("conectado")
        return conn
    except sqlite3.Error as err:
        print(f"Error al conectar a MySQL: {err}")
    print("Conexión fallida.")
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
        cursor.execute('SELECT * FROM usuario WHERE Id_usuario = ?', (id_usuario,))
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
        user_data.execute('SELECT * FROM usuario WHERE email = ?', (email,))
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
        if conn is None:
            print("No se pudo establecer conexión con la base de datos.")
            return None

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuario WHERE nombre_user = ?", (nombre_usuario,))
            usuario = cursor.fetchone()
        except sqlite3.Error as err:
            print(f"Error al ejecutar la consulta: {err}")
            return None
        finally:
            conn.close()  # Asegúrate de cerrar la conexión

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
        FROM usuario u 
        JOIN tipo_usuario t ON u.id_tipo_usuario = t.id_tipo_usuario 
        WHERE u.id_usuario = ?
        '''
        cursor.execute(query, (id_usuario,))
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data:
            return {
                'id_usuario': user_data['id_usuario'],
                'nombre_usuario': user_data['nombre_user'],
                'email': user_data['email'],
                'id_tipo_usuario': user_data['id_tipo_usuario'],
                'nombre_tipo_usuario': user_data['nombre_tipo_usuario'] 
            }
        return None
