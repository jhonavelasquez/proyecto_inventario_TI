from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user, LoginManager
from routes.login import login_bp 
from routes.reportes import reportes_bp  
from routes.sistema import sistema_bp  
from routes.usuarios import usuarios_bp 
from routes.historial import historial_bp
from routes.computadores import computadores_bp  
from routes.notificaciones import notificaciones_bp  
from utils.decorators import requiere_tipo_usuario, get_info_notifications, get_total_notifications
from config import Config
from flask_wtf.csrf import CSRFProtect
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
app.register_blueprint(notificaciones_bp, url_prefix='/notificaciones')  

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

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
            cursor = conn.cursor()

            today = datetime.datetime.now()
            fecha_15_dias = today + datetime.timedelta(days=15)

            today_str = today.strftime('%Y-%m-%d %H:%M:%S')
            today_sin_seg = today.strftime('%Y-%m-%d')
            fecha_15_dias_str = fecha_15_dias.strftime('%Y-%m-%d')

            cursor.execute(
                'SELECT * FROM reportes WHERE (fecha_solucion BETWEEN %s AND %s) AND (enviado = false)',
                (today_str, fecha_15_dias_str)
            )
            reportes = cursor.fetchall()

            for reporte in reportes:
                id_reporte = reporte[0] 
                usuario_id = reporte[1] 
                nombre_sistema = reporte[3]
                fecha_solucion = reporte[6]
                enviado = reporte[8]

                cursor.execute('SELECT id_usuario, nombre_user, email FROM usuario WHERE id_usuario = %s', (usuario_id,))
                usuario_reporte = cursor.fetchone()
                print("-------------------")
                print("Enviando correo")
                print("-------------------")

                if enviado == False:
                    subject = f"Recordatorio: El reporte {nombre_sistema} está cercano a su fecha de solución"
                    body = f"Estimado {usuario_reporte[1]}, el reporte {nombre_sistema} tiene fecha de solución el {fecha_solucion}. Por favor tome las medidas necesarias."
                    enviar_correo(usuario_reporte[2], subject, body)

                    cursor.execute('''
                        UPDATE reportes SET enviado = true WHERE id_reporte = %s
                    ''', (id_reporte,))

                    cursor.execute(
                        'INSERT INTO notificaciones ( id_usuario, id_reporte, fecha_notificacion, mensaje, leido) VALUES (%s, %s, %s, %s, false)',
                        (usuario_id, reporte[0], today_str, subject) 
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
    app.run(debug=True) 