# app/utils/decorators.py
from functools import wraps
from flask import session, redirect, url_for, render_template
from model import get_db_connection

def obtener_opciones_computador():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT Id_pc, Nombre_pc FROM Pc')
    computadores = cursor.fetchall()
    conn.close()
    opciones = [(computador[0], computador[1]) for computador in computadores]
    return opciones

def requiere_tipo_usuario(*roles_permitidos):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'id_tipo_usuario' not in session:
                return redirect(url_for('auth.login'))
            if session['id_tipo_usuario'] not in roles_permitidos:
                return render_template('acceso-denegado.html')
            return f(*args, **kwargs)
        return decorated_function
    return decorator

#NOTIFICACIONES EN EL SISTEMA
def get_total_notifications(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT COUNT(*) FROM Notificaciones WHERE id_usuario = %s AND leido = false',
        (user_id,))
    total_notifications = cursor.fetchone()[0]
    conn.close()

    return total_notifications

def get_info_notifications(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM Notificaciones WHERE id_usuario = %s ORDER BY id_notificacion DESC LIMIT 8',
        (user_id,)
    )
    info_notificaciones = cursor.fetchall()
    conn.close()

    return info_notificaciones
