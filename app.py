from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user, LoginManager
from routes.login import login_bp 
from routes.reportes import reportes_bp  
from routes.sistema import sistema_bp  
from routes.usuarios import usuarios_bp 
from routes.historial import historial_bp
from routes.computadores import computadores_bp  
from utils.decorators import requiere_tipo_usuario, get_info_notifications, get_total_notifications
from config import Config
from flask_wtf.csrf import CSRFProtect
from forms import EditarMiCuenta
from model import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
import datetime
import time
import schedule
import signal
import threading
import sys

app = Flask(__name__)
app.config.from_object(Config)

csrf = CSRFProtect(app)
mail = Mail(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login.login'

@login_manager.user_loader
def load_user(user_id):
    from model import Usuario
    user = Usuario.get_by_id(user_id)
    return user

app.register_blueprint(login_bp, url_prefix='/login')
app.register_blueprint(reportes_bp, url_prefix='/reportes') 
app.register_blueprint(computadores_bp, url_prefix='/computadores') 
app.register_blueprint(sistema_bp, url_prefix='/')
app.register_blueprint(usuarios_bp, url_prefix='/usuarios')  
app.register_blueprint(historial_bp, url_prefix='/historial') 

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


#BACKEND MI CUENTA
@app.route('/cuenta', methods=['GET', 'POST'])
@requiere_tipo_usuario(1, 2, 3)
@login_required
def cuenta():
    user = current_user
    num_notificaciones_totales = get_total_notifications(user.id)
    info_notificaciones = get_info_notifications(user.id)

    form = EditarMiCuenta()

    conn = get_db_connection()

    if form.validate_on_submit():
        nuevo_email = form.email_user.data
        nueva_password = form.psw.data

        conn.execute(
                'UPDATE Usuario SET email = ? WHERE id_usuario = ?',
                (nuevo_email, user.id)
            )
        user.email = nuevo_email

        if nueva_password:
            hashed_password = generate_password_hash(nueva_password)
            conn.execute(
                'UPDATE Usuario SET psw = ? WHERE id_usuario = ?',
                (hashed_password, user.id)
            )
            user.password = nuevo_email
        
        conn.commit()
        flash('Tus datos se han actualizado correctamente', 'success')
        return redirect(url_for('cuenta'))

    tipo_usuario = conn.execute(
        'SELECT nombre_tipo_usuario FROM Tipo_usuario WHERE id_tipo_usuario = ?', 
        (user.id_tipo_usuario,)
    ).fetchone()

    tipo_usuario = tipo_usuario['nombre_tipo_usuario'] if tipo_usuario else 'Desconocido'

    try:
        id_pc_mas_utilizado = conn.execute(''' 
                        SELECT Id_pc 
                        FROM Usuario_Sistema_PC 
                        WHERE Id_usuario = ? 
                        GROUP BY Id_pc 
                        ORDER BY COUNT(*) DESC 
                        LIMIT 1 
                    ''', (user.id,)).fetchone()

        if id_pc_mas_utilizado:
            id_pc_mas_utilizado = id_pc_mas_utilizado['Id_pc']

            nombre = conn.execute('SELECT Nombre_pc FROM Pc WHERE Id_pc = ?', (id_pc_mas_utilizado,)).fetchone()
            if nombre:
                nombre = nombre['Nombre_pc']
            else:
                nombre = 'Computador no encontrado'
        else:
            nombre = 'Computador no asignado'
    except Exception as e:
        nombre = 'Computador no asignado'
        print(f"Error al obtener el nombre del PC: {e}")


    conn.close()

    data = {'user': user, 'tipo_usuario': tipo_usuario, 'nombre': nombre}

    return render_template('miCuenta.html',
                           user=user,
                           data=data, 
                           form=form, 
                           num_notificaciones_totales=num_notificaciones_totales, 
                           info_notificaciones=info_notificaciones)
















@app.route('/notificaciones', methods=['GET'])
@requiere_tipo_usuario(1)
@login_required
def obtener_notificaciones():
    user_id = current_user.id
    conn = get_db_connection()

    num_notificaciones_enviadas = 0
    num_notificaciones_totales = 0
    
    notificaciones = conn.execute('SELECT * FROM Notificaciones WHERE id_usuario = ? AND leido = false', (user_id,)).fetchall()

    if notificaciones:
        num_notificaciones_enviadas = conn.execute(
            'SELECT COUNT(*) FROM Notificaciones WHERE id_usuario = ? AND leido = false',
            (user_id,)
        ).fetchone()[0]
        
        conn.execute('UPDATE Notificaciones SET leido = true WHERE id_usuario = ? AND leido = false', (user_id,))
        conn.commit()  

    num_notificaciones_totales = conn.execute(
        'SELECT COUNT(*) FROM Notificaciones WHERE id_usuario = ?',
        (user_id,)
    ).fetchone()[0]

    return render_template('prueba.html', num_notificaciones_enviadas=num_notificaciones_enviadas, num_notificaciones_totales=num_notificaciones_totales)

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

@app.route('/marcar_notificaciones_leidas', methods=['POST'])
@login_required
def marcar_notificaciones_leidas():
    print("Datos recibidos:", request.form)
    user_id = current_user.id
    conn = get_db_connection()

    notificaciones = conn.execute('SELECT * FROM Notificaciones WHERE id_usuario = ? AND leido = false AND enviado = true', (user_id,)).fetchall()
    
    if notificaciones:
        conn.execute('UPDATE Notificaciones SET leido = true WHERE id_usuario = ? AND leido = false AND enviado = true', (user_id,))
        print("NOTIFICACIONES ACTULIZADAS")
    else:
        print("TODAS LAS NOTIFACIONES ESTÁN LEIDAS.")
    conn.commit()
    conn.close()

    return '', 204


#NOTIFICACION POR EMAIL
def enviar_correo(destinatario, asunto, cuerpo):
    try:
        mail = Mail(app)
        msg = Message(asunto, recipients=[destinatario])
        msg.body = cuerpo
        mail.send(msg)
        print(f"Correo enviado a {destinatario}")
    except Exception as e:
        print(f"Error enviando correo: {e}")

def enviar_recordatorios():
    try:
        with app.app_context():
            conn = get_db_connection()
            print("Revisión---")

            today = datetime.datetime.now()
            fecha_15_dias = today + datetime.timedelta(days=15)

            today_str = today.strftime('%Y-%m-%d %H:%M:%S')
            today_sin_seg = today.strftime('%Y-%m-%d')
            fecha_15_dias_str = fecha_15_dias.strftime('%Y-%m-%d')

            reportes = conn.execute(
                'SELECT * FROM Reportes WHERE fecha_solucion BETWEEN ? AND ?',
                (today_str, fecha_15_dias_str)
            ).fetchall()

            print(reportes)
            print(f"Fecha de hoy: {today_str}")
            print(f"Fecha de hoy sin segundos: {today_sin_seg}")
            print(f"Fecha en 15 días: {fecha_15_dias_str}")

            for reporte in reportes:
                usuario_id = reporte['usuario_id'] 
                nombre_sistema = reporte['asunto']
                fecha_solucion = reporte['fecha_solucion']

########################## Reemplar de strftime por DATE_FORMAT    CUANDO SE CAMBIE LA BASE DE DATOS A MYSQL###########################
#DATE_FORMAT(fecha_notificacion, '%Y-%m-%d')
                notificacion_enviada = conn.execute(
                    "SELECT * FROM Notificaciones WHERE id_reporte = ? AND strftime('%Y-%m-%d', DATE(fecha_notificacion)) = ? AND enviado = true",
                    (reporte['id_reporte'], today_sin_seg)
                ).fetchone()

                usuario_reporte = conn.execute('SELECT Id_usuario, Nombre_user, Email FROM Usuario WHERE Id_usuario = ?', (usuario_id,)).fetchone()
                
                print(usuario_reporte['Email'], " ----- ", nombre_sistema)
                print("-------------------")
                print(notificacion_enviada)
                print("-------------------")

                if not notificacion_enviada:
                    subject = f"Recordatorio: El reporte '{nombre_sistema}' está cercano a su fecha de solución"
                    body = f"Estimado {usuario_reporte['Nombre_user']}, el reporte '{nombre_sistema}' tiene fecha de solución el {fecha_solucion}. Por favor tome las medidas necesarias."
                    enviar_correo(usuario_reporte['Email'], subject, body)

                    conn.execute(
                        'INSERT INTO Notificaciones ( id_usuario, id_reporte, fecha_notificacion, mensaje, leido, enviado) VALUES (?, ?, ?, ?, false, true)',
                        (usuario_id, reporte['id_reporte'], today_str, subject) 
                    )
                    conn.commit()

    except Exception as e:
        print(f"Error al enviar recordatorios: {e}")
    finally:
        conn.commit()
        conn.close()
        pass


stop_thread = False

def iniciar_revisiones_periodicas():
    schedule.every(1).minutes.do(enviar_recordatorios)
    schedule.every().day.at("08:00").do(enviar_recordatorios)

    while not stop_thread:
        schedule.run_pending()
        time.sleep(1)

def signal_handler(sig, frame):
    global stop_thread
    stop_thread = True
    print("Deteniendo revisiones periódicas...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


hilo_revisar_reportes = threading.Thread(target=iniciar_revisiones_periodicas)
hilo_revisar_reportes.start()

if __name__ == '__main__':
    app.run(debug=True)  # Cambia a False en producción
