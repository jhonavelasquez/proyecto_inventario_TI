# app/utils/decorators.py
from functools import wraps
from flask import session, redirect, url_for
from model import get_db_connection

def requiere_tipo_usuario(*roles_permitidos):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'id_tipo_usuario' not in session:
                return redirect(url_for('auth.login'))
            if session['id_tipo_usuario'] not in roles_permitidos:
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

#NOTIFICACIONES EN EL SISTEMA
def get_total_notifications(user_id):
    conn = get_db_connection()
    total_notifications = conn.execute(
        'SELECT COUNT(*) FROM Notificaciones WHERE id_usuario = ?  AND leido = false',
        (user_id,)
    ).fetchone()[0]
    conn.close()

    return total_notifications

def get_info_notifications(user_id):
    conn = get_db_connection()
    info_notifiaciones= conn.execute(
        'SELECT * FROM Notificaciones WHERE id_usuario = ? ORDER BY id_notificacion DESC LIMIT 8',
        (user_id,)
    ).fetchall()
    conn.close()

    return info_notifiaciones