import sqlite3


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

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
        user_data = conn.execute('SELECT * FROM Usuario WHERE Id_usuario = ?', (id_usuario,)).fetchone()
        conn.close()
        if user_data:
            return Usuario(
                user_data['Id_usuario'], 
                user_data['Nombre_user'], 
                user_data['Email'], 
                user_data['Psw'],
                user_data['id_tipo_usuario']
            )
        return None

    @staticmethod
    def get_by_email(email):
        conn = get_db_connection()
        user_data = conn.execute('SELECT * FROM Usuario WHERE Email = ?', (email,)).fetchone()
        conn.close()
        if user_data:
            return Usuario(
                user_data['Id_usuario'], 
                user_data['Nombre_user'], 
                user_data['Email'], 
                user_data['Psw'],
                user_data['id_tipo_usuario']
            )
        return None

    @staticmethod
    def get_by_nombre_usuario(nombre_usuario):
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Usuario WHERE Nombre_user = ?", (nombre_usuario,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return Usuario(
                row['Id_usuario'], 
                row['Nombre_user'], 
                row['Email'], 
                row['Psw'],
                row['id_tipo_usuario']
            )
        return None
    
    @staticmethod
    def get_by_id_with_tipo_usuario(id_usuario):
        conn = get_db_connection()
        query = '''
        SELECT u.*, t.nombre_tipo_usuario 
        FROM Usuario u 
        JOIN Tipo_usuario t ON u.id_tipo_usuario = t.id_tipo_usuario 
        WHERE u.Id_usuario = ?
        '''
        user_data = conn.execute(query, (id_usuario,)).fetchone()
        conn.close()
        if user_data:
            return {
                'id_usuario': user_data['Id_usuario'],
                'nombre_usuario': user_data['Nombre_user'],
                'email': user_data['Email'],
                'id_tipo_usuario': user_data['id_tipo_usuario'],
                'nombre_tipo_usuario': user_data['nombre_tipo_usuario']  # El nombre del tipo de usuario
            }
        return None