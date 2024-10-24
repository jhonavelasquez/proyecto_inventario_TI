# routes/sistema.py
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from model import get_db_connection
from utils.decorators import requiere_tipo_usuario, get_info_notifications, get_total_notifications

notificaciones_bp = Blueprint('notificaciones', __name__)

@notificaciones_bp.route('/notificaciones', methods=['GET'])
@requiere_tipo_usuario(1)
@login_required
def obtener_notificaciones():
    user_id = current_user.id
    conn = get_db_connection()
    cursor = conn.cursor()

    num_notificaciones_enviadas = 0
    num_notificaciones_totales = 0

    cursor.execute('SELECT * FROM Notificaciones WHERE id_usuario = %s AND leido = false', (user_id,))
    notificaciones = cursor.fetchall()

    if notificaciones:
        cursor.execute(
            'SELECT COUNT(*) FROM Notificaciones WHERE id_usuario = %s AND leido = false',
            (user_id,)
        )
        num_notificaciones_enviadas = cursor.fetchone()[0]

        cursor.execute('UPDATE Notificaciones SET leido = true WHERE id_usuario = %s AND leido = false', (user_id,))
        conn.commit()  

    cursor.execute(
        'SELECT COUNT(*) FROM Notificaciones WHERE id_usuario = %s',
        (user_id,)
    )
    num_notificaciones_totales = cursor.fetchone()[0]
    return render_template('prueba.html', num_notificaciones_enviadas=num_notificaciones_enviadas, num_notificaciones_totales=num_notificaciones_totales)

#NOTIFICACIONES EN EL SISTEMA
def get_total_notifications(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT COUNT(*) FROM Notificaciones WHERE id_usuario = %s  AND leido = false',
        (user_id,)
    )
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
    info_notifiaciones = cursor.fetchall()

    conn.close()
    return info_notifiaciones

@notificaciones_bp.route('/marcar_notificaciones_leidas', methods=['POST'])
@login_required
def marcar_notificaciones_leidas():
    user_id = current_user.id
    conn = get_db_connection()
    cursor= conn.cursor()

    cursor.execute('SELECT * FROM Notificaciones WHERE id_usuario = %s AND leido = false', (user_id,))
    notificaciones = cursor.fetchall()

    if notificaciones:
        cursor.execute('UPDATE Notificaciones SET leido = true WHERE id_usuario = %s AND leido = false', (user_id,))
        print("NOTIFICACIONES ACTULIZADAS")
    else:
        print("TODAS LAS NOTIFACIONES ESTÁN LEIDAS.")
    conn.commit()
    conn.close()
    return '', 204

@notificaciones_bp.route('/marcar_notificacion_leida', methods=['POST'])
@login_required
def marcar_notificacion_leida():
    user_id = current_user.id
    id_reporte = request.form.get('id_reporte')

    if id_reporte:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('UPDATE Notificaciones SET leido = true WHERE id_usuario = %s AND id_reporte = %s', (user_id, id_reporte))

        conn.commit()
        conn.close()

        return '', 204

