import sqlite3
from flask import Flask, session, render_template, request, redirect, url_for, flash, send_from_directory, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from forms import *
from model import *
import datetime
import os

from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
from io import BytesIO

from flask_mail import Mail, Message

import threading
import time
import schedule
import signal
import sys

from functools import wraps

app = Flask(__name__)
app.secret_key = 'd9ddb8a50af95ba9a24052cb926e3b64ef04578fb6dc3d9b6ab9a13eec464195'

hrs_revisión = "07:00"

#CONFIGURACION NOTIFICACIONES GMAIL
app.config['MAIL_SERVER'] = 'smtp.gmail.com'    # Servidor SMTP de Gmail
app.config['MAIL_PORT'] = 587                   # Puerto para TLS
app.config['MAIL_USE_TLS'] = True               # Usar TLS
app.config['MAIL_USE_SSL'] = False              # Deshabilitar SSL si usas TLS
app.config['MAIL_USERNAME'] = 'jonathan.vr484@gmail.com'   #Gmail
app.config['MAIL_PASSWORD'] = 'ycfs vvod evqw emwy'  # Contraseña de Gmail
app.config['MAIL_DEFAULT_SENDER'] = 'jonathan.vr484@gmail.com'  # Email predeterminado de envío

app.config.update(
    SESSION_COOKIE_SECURE=True,  # Cookies solo se envían por HTTPS
    SESSION_COOKIE_HTTPONLY=True, # Evitar acceso desde JavaScript
    SESSION_COOKIE_SAMESITE='Lax' # Ayuda a prevenir CSRF
)

mail = Mail(app)
csrf = CSRFProtect(app)

hashed_password = generate_password_hash("@j0n_v3l4squ3z#")
check_password = check_password_hash(hashed_password, "contraseña_ingresada")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.get_by_id(user_id)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

from functools import wraps
from flask import session, redirect, url_for, flash

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        form = LoginForm()
        if form.validate_on_submit():
            nombre_usuario = form.nombre_usuario.data
            password = form.contrasena.data
            user = Usuario.get_by_nombre_usuario(nombre_usuario)

            if user and check_password_hash(user.password, password):
                print("Contraseña correcta")
                login_user(user)
                
                session['id_tipo_usuario'] = user.id_tipo_usuario
                flash('Inicio de sesión exitoso.', 'success')
                return redirect(url_for('index'))
            else:
                flash('Credenciales inválidas. Por favor, inténtalo de nuevo.', 'danger')

    except Exception as e:
        print(f"Error en login: {e}")
        flash('Ocurrió un error al intentar iniciar sesión. Por favor, inténtalo de nuevo.', 'danger')

    return render_template('login.html', form=form)


def requiere_tipo_usuario(*roles_permitidos):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'id_tipo_usuario' not in session:
                return redirect(url_for('login'))

            if session['id_tipo_usuario'] not in roles_permitidos:
                return redirect(url_for('index'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesion cerrada correctamente', 'warning')
    return redirect(url_for('login'))

# BACKEND SISTEMA
@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    formCrear = CrearSistemaForm()
    formEliminar = EliminarSistemaForm()
    conn = get_db_connection()
    sistema_id = request.args.get('sistema')
    search_query = request.args.get('search', '')

    sistemas = conn.execute("SELECT * FROM Sistema").fetchall()
    formEliminar.sistema.choices = [(sistema['Id_sistema'], sistema['Nombre_sistema']) for sistema in sistemas]
    pcs = conn.execute("SELECT * FROM Pc").fetchall()

    query = '''
    SELECT Usuario.Id_usuario, Usuario.Nombre_user, Usuario.Email, Pc.Id_pc, 
        Pc.Nombre_pc, Sistema.Id_sistema, Sistema.Nombre_sistema, Usuario_Sistema_PC.Activo
    FROM Usuario
    INNER JOIN Usuario_Sistema_PC ON Usuario_Sistema_PC.Id_usuario = Usuario.Id_usuario
    INNER JOIN Pc ON Pc.Id_pc = Usuario_Sistema_PC.Id_pc
    INNER JOIN Sistema ON Sistema.Id_sistema = Usuario_Sistema_PC.Id_sistema
    WHERE 1=1
    '''
    params = []
    if sistema_id:
        query += ' AND Sistema.Id_sistema = ?'
        params.append(sistema_id)
    if search_query:
        query += ' AND (Usuario.Nombre_user LIKE ? OR Pc.Nombre_pc LIKE ?)'
        params.extend(['%' + search_query + '%', '%' + search_query + '%'])

    user_pc_data = conn.execute(query, params).fetchall()
    conn.close()

    user=current_user
    num_notificaciones_totales = get_total_notifications(user.id)
    info_notificaciones = get_info_notifications(user.id)

    return render_template('index.html', formCrear=formCrear, formEliminar=formEliminar, user_pc_data=user_pc_data, sistemas=sistemas, pcs=pcs,  user=current_user, num_notificaciones_totales=num_notificaciones_totales, info_notificaciones=info_notificaciones)

@app.route('/crear_sistema', methods=['POST'])
@requiere_tipo_usuario(1, 3)
@login_required
def crear_sistema():
    try:
        formCrear = CrearSistemaForm()
        conn = get_db_connection()

        if formCrear.validate_on_submit():
            nombre_sistema = formCrear.nombre_sistema.data

            sistemas = conn.execute("SELECT Nombre_sistema FROM Sistema").fetchall()
            for sistema in sistemas:
                if nombre_sistema == sistema['Nombre_sistema']:
                    flash("El sistema ya existe y no será añadido de nuevo.", "warning")
                    conn.close()
                    return redirect(url_for('index'))

            conn.execute('INSERT INTO Sistema (Nombre_sistema) VALUES (?)', (nombre_sistema,))
            conn.commit()

            id_sistema = conn.execute(
                'SELECT Id_sistema FROM Sistema WHERE Nombre_sistema = ?', (nombre_sistema,)).fetchone()['Id_sistema']

            usuarios = conn.execute("SELECT Id_usuario FROM Usuario").fetchall()
            for usuario in usuarios:
                id_pc_mas_utilizado = conn.execute('''
                    SELECT Id_pc
                    FROM Usuario_Sistema_PC
                    WHERE Id_usuario = ?
                    GROUP BY Id_pc
                    ORDER BY COUNT(*) DESC
                    LIMIT 1
                ''', (usuario['Id_usuario'],)).fetchone()

                if id_pc_mas_utilizado:
                    conn.execute(
                        "INSERT INTO Usuario_Sistema_PC (Id_usuario, Id_sistema, Id_pc, Activo) VALUES (?, ?, ?, FALSE)",
                        (usuario['Id_usuario'], id_sistema, id_pc_mas_utilizado['Id_pc'])
                    )
                else:
                    flash(f"No se pudo encontrar un PC asignado para el usuario con ID {usuario['Id_usuario']}.", "warning")

            user = current_user
            fecha_actual_seg = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            fecha_actual = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
            descripcion_hist= (f" agregó un nuevo sistema.  {nombre_sistema}.")
            conn.execute('INSERT INTO Historial (usuario_historial, descripcion, fecha, id_categoria) VALUES (?,?,?, 2)', (user.nombre_usuario,descripcion_hist,fecha_actual_seg))

            conn.commit()
            conn.close()

            flash("Sistema creado exitosamente.", "success")
    except sqlite3.Error as db_error:
        print(f"Database error: {db_error}")
        flash("Error al crear el sistema. Por favor, inténtalo de nuevo.", "danger")
    except Exception as e:
        print(f"Error: {e}")
        flash("Ocurrió un error inesperado. Por favor, inténtalo de nuevo.", "danger")
    finally:
        conn.close()

    return redirect(url_for('index'))


@app.route('/eliminar_sistema', methods=['POST'])
@requiere_tipo_usuario(1,3)
@login_required
def eliminar_sistema():
    formEliminar = EliminarSistemaForm()
    conn = get_db_connection()

    sistemas = conn.execute("SELECT Id_sistema, Nombre_sistema FROM Sistema").fetchall()

    formEliminar.sistema.choices = [(sistema['Id_sistema'], sistema['Nombre_sistema']) for sistema in sistemas]

    if formEliminar.validate_on_submit():
        sistema_id = formEliminar.sistema.data

        try:
            sistema = conn.execute('SELECT Nombre_sistema FROM Sistema WHERE Id_sistema = ?', (sistema_id,)).fetchone()

            if sistema:
                nombre_sistema = sistema['Nombre_sistema']

                conn.execute('DELETE FROM Sistema WHERE Id_sistema = ?', (sistema_id,))

                user = current_user
                fecha_actual_seg = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                fecha_actual = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
                descripcion_hist = (f" eliminó el sistema {nombre_sistema}.")
                conn.execute('INSERT INTO Historial (usuario_historial, descripcion, fecha, id_categoria) VALUES (?, ?, ?, 2)', (user.nombre_usuario, descripcion_hist, fecha_actual_seg))

                flash(f"{nombre_sistema} ha sido eliminado.", "warning")
                conn.commit()
            else:
                flash("El sistema no existe.", "danger")

        except sqlite3.Error as db_error:
            print(f"Database error: {db_error}")
            flash("Error al eliminar el sistema. Por favor, inténtalo de nuevo.", "danger")
        except Exception as e:
            print(f"Error: {e}")
            flash("Ocurrió un error inesperado. Por favor, inténtalo de nuevo.", "danger")
        finally:
            conn.close()

    return redirect(url_for('index'))

@app.route('/editar_sistema/<int:id_sistema>/<int:id_usuario>/<int:id_pc>', methods=['GET', 'POST'])
@requiere_tipo_usuario(1,3)
@login_required
def editar_sistema(id_sistema, id_usuario, id_pc):
    conn = get_db_connection()
    form = EditarSistemaForm()

    pcs = conn.execute("SELECT * FROM Pc").fetchall()
    form.nuevo_Id_pc.choices = [(pc['Id_pc'], pc['Nombre_pc']) for pc in pcs]

    try:
        if request.method == 'POST' and form.validate_on_submit():
            nuevo_id_pc = form.nuevo_Id_pc.data
            activo = form.activo.data

            conn.execute('''UPDATE Usuario_Sistema_PC 
                            SET Activo = ?, Id_pc = ?
                            WHERE Id_usuario = ? AND Id_sistema = ? AND Id_pc = ?''',
                         (activo, nuevo_id_pc, id_usuario, id_sistema, id_pc))

            nombre_user = conn.execute(
                'SELECT Nombre_user FROM Usuario WHERE Id_usuario = ?', (id_usuario,)).fetchone()
            nombre_sis = conn.execute(
                'SELECT Nombre_sistema FROM Sistema WHERE Id_sistema = ?', (id_sistema,)).fetchone()

            
            nombre_usuario = nombre_user['Nombre_user']
            nombre_sistema = nombre_sis['Nombre_sistema']

            user = current_user
            fecha_actual_seg = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            fecha_actual = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
            descripcion_hist = (f"Actualizó {nombre_sistema} de {nombre_usuario}. ")
            conn.execute('INSERT INTO Historial (usuario_historial, descripcion, fecha, id_categoria) VALUES (?,?,?, 2)', 
                         (user.nombre_usuario, descripcion_hist, fecha_actual_seg))

            conn.commit()

            flash("¡El PC o el estado del sistema han sido actualizados!", "success")
            return redirect(url_for('index'))

        user_pc = conn.execute('''SELECT Usuario.Id_usuario, Usuario.Nombre_user, Usuario_Sistema_PC.Id_pc, 
                                  Pc.Nombre_pc, Sistema.Nombre_sistema, Usuario_Sistema_PC.Activo, 
                                  Usuario_Sistema_PC.Id_sistema
                                  FROM Usuario
                                  INNER JOIN Usuario_Sistema_PC ON Usuario.Id_usuario = Usuario_Sistema_PC.Id_usuario
                                  INNER JOIN Pc ON Pc.Id_pc = Usuario_Sistema_PC.Id_pc
                                  INNER JOIN Sistema ON Usuario_Sistema_PC.Id_sistema = Sistema.Id_sistema
                                  WHERE Usuario_Sistema_PC.Id_sistema = ? AND Usuario_Sistema_PC.Id_usuario = ? AND Usuario_Sistema_PC.Id_pc = ?''',
                                 (id_sistema, id_usuario, id_pc)).fetchone()

        form.nuevo_Id_pc.default = user_pc['Id_pc']
        form.activo.default = user_pc['Activo']
        form.process()

    except Exception as e:
        flash(f"Error: {str(e)}", "danger")

    finally:
        conn.close()

    user = current_user
    num_notificaciones_totales = get_total_notifications(user.id)
    info_notificaciones = get_info_notifications(user.id)

    return render_template('editar_sistema.html', form=form, user_pc=user_pc, user=user, 
                           num_notificaciones_totales=num_notificaciones_totales, 
                           info_notificaciones=info_notificaciones)
# BACKEND COMPUTADOR
@app.route('/computadores', methods=['GET'])
@login_required
def computadores():
    conn = get_db_connection()

    form = CrearComputadorForm()

    search_query = request.args.get('search', '')

    query = "SELECT * FROM Pc Where 1 = 1"
    params = []
    if search_query:
        query += ' AND Pc.Nombre_pc LIKE ?'
        params.extend(['%' + search_query + '%'])

    filtro_pcs = conn.execute(query, params).fetchall()
    conn.close()
    user=current_user
    num_notificaciones_totales = get_total_notifications(user.id)
    info_notificaciones = get_info_notifications(user.id)

    return render_template('computadores.html', form=form, filtro_pcs=filtro_pcs,  user=user, num_notificaciones_totales=num_notificaciones_totales, info_notificaciones=info_notificaciones)

@app.route('/crear_computador', methods=['POST'])
@requiere_tipo_usuario(1, 3)
@login_required
def crear_computador():
    form = CrearComputadorForm()
    if form.validate_on_submit():
        nombre_computador = form.nombre_computador.data
        nombre_placa = form.nombre_placa.data
        disco = form.disco.data
        ram = form.ram.data
        fuente = form.fuente.data

        conn = get_db_connection()
        conn.execute('''
            INSERT INTO Pc (Nombre_pc, Placa, Almacenamiento, Ram, Fuente)
            VALUES (?, ?, ?, ?, ?)
        ''', (nombre_computador, nombre_placa, disco, ram, fuente))

        user = current_user
        fecha_actual_seg = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        fecha_actual = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
        descripcion_hist= (f" agregó un nuevo computador.  {nombre_computador}. ")
        conn.execute('INSERT INTO Historial (usuario_historial, descripcion, fecha, id_categoria) VALUES (?,?,?, 3)', (user.nombre_usuario,descripcion_hist,fecha_actual_seg))
        
        conn.commit()
        conn.close()
        
        flash("Computador agregado exitosamente.", "success")
        return redirect('computadores')
    return render_template('computadores.html')

@app.route('/editar_computador/<int:id_pc>', methods=['GET'])
@requiere_tipo_usuario(1,3)
@login_required
def editar_computador(id_pc):
    conn = get_db_connection()

    form = EditarComputadorForm()
    pc = conn.execute('''
        SELECT *
        FROM Pc
        WHERE Pc.Id_pc = ?
    ''', (id_pc,)).fetchone()

    if request.method == 'GET':
        form.id_pc.data = pc['Id_pc']
        form.nombre_computador.data = pc['Nombre_pc']
        form.nombre_placa.data = pc['Placa']
        form.almacenamiento.data = pc['Almacenamiento']
        form.ram.data = pc['Ram']
        form.fuente.data = pc['Fuente'] 

    
    conn.close()

    user=current_user
    num_notificaciones_totales = get_total_notifications(user.id)
    info_notificaciones = get_info_notifications(user.id)
    
    return render_template('editar_computador.html', pc=pc, form=form, user=user, num_notificaciones_totales=num_notificaciones_totales, info_notificaciones=info_notificaciones)

@app.route('/editar_computador_form', methods=['POST'])
@requiere_tipo_usuario(1,3)
@login_required
def editar_computador_form():
    id_pc = request.form['id_pc']
    nombre_pc = request.form['nombre_computador']
    placa_pc = request.form['nombre_placa']
    almacenamiento = request.form.get('almacenamiento')
    ram = request.form.get('ram')
    nombre_fuente = request.form['fuente']
    action = request.form['action']

    conn = get_db_connection()

    if action == 'save':
        conn.execute(
            'UPDATE Pc SET Nombre_pc = ?, PLaca = ?, Almacenamiento = ?, Ram = ?, Fuente = ? WHERE Id_pc = ?',
            (nombre_pc, placa_pc, almacenamiento, ram, nombre_fuente, id_pc)
        )

        user = current_user
        fecha_actual_seg = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        fecha_actual = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
        descripcion_hist= (f" actualizó la información de un computador.  {nombre_pc}. ")
        conn.execute('INSERT INTO Historial (usuario_historial, descripcion, fecha, id_categoria) VALUES (?,?,?, 3)', (user.nombre_usuario,descripcion_hist,fecha_actual_seg))

        flash("Información del computador actualizada con éxito.", "success")
    elif action == 'delete':
        conn.execute(
            'DELETE FROM Pc WHERE Id_pc = ?',
            (id_pc,)
        )

        user = current_user
        fecha_actual_seg = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        fecha_actual = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
        descripcion_hist= (f" eliminó un computador.  {nombre_pc}.")
        conn.execute('INSERT INTO Historial (usuario_historial, descripcion, fecha, id_categoria) VALUES (?,?,?, 3)', (user.nombre_usuario,descripcion_hist,fecha_actual_seg))
        flash("Computador eliminado con éxito.", "danger")

    conn.commit()
    conn.close()

    return redirect(url_for('computadores'))

# BACKEND USUARIO
@app.route('/usuarios', methods=['GET'])
@requiere_tipo_usuario(1)
@login_required
def usuarios():
    conn = get_db_connection()
    search_query = request.args.get('search', '')

    pcs = conn.execute("SELECT Id_pc, Nombre_pc FROM Pc").fetchall()
    tipo_usuario = conn.execute("SELECT id_tipo_usuario, nombre_tipo_usuario FROM Tipo_usuario").fetchall()

    form = CrearUsuarioForm()

    form.computador.choices = [(pc['Id_pc'], pc['Nombre_pc']) for pc in pcs]
    form.tipo_usuario.choices = [(tipo['id_tipo_usuario'], tipo['nombre_tipo_usuario']) for tipo in tipo_usuario]

    query = '''SELECT Usuario.Id_usuario, Usuario.Nombre_user, Usuario.Email, Usuario.id_tipo_usuario, Tipo_usuario.nombre_tipo_usuario
                FROM Usuario
                INNER JOIN Tipo_usuario ON Tipo_usuario.id_tipo_usuario = Usuario.id_tipo_usuario
                Where 1 = 1'''
    
    params = []
    if search_query:
        query += ' AND (Usuario.Nombre_user LIKE ?  OR Usuario.Id_usuario LIKE ?)'
        params.extend(['%' + search_query + '%', '%' + search_query + '%'])
    
    users = conn.execute(query, params).fetchall()
    conn.close()

    user = current_user
    num_notificaciones_totales = get_total_notifications(user.id)
    info_notificaciones = get_info_notifications(user.id)

    return render_template('usuarios.html', users=users, pcs=pcs, form=form, tipo_usuario=tipo_usuario, 
                           user=user, num_notificaciones_totales=num_notificaciones_totales, 
                           info_notificaciones=info_notificaciones)

@app.route('/crear_usuario', methods=['GET', 'POST'])
@requiere_tipo_usuario(1)
@login_required
def crear_usuario():
    conn = get_db_connection()

    pcs = conn.execute("SELECT Id_pc, Nombre_pc FROM Pc").fetchall()
    tipo_usuario = conn.execute("SELECT id_tipo_usuario, nombre_tipo_usuario FROM Tipo_usuario").fetchall()

    form = CrearUsuarioForm()

    form.computador.choices = [(pc['Id_pc'], pc['Nombre_pc']) for pc in pcs]
    form.tipo_usuario.choices = [(tipo['id_tipo_usuario'], tipo['nombre_tipo_usuario']) for tipo in tipo_usuario]

    if form.validate_on_submit():
        nombre_user = form.nombre_user.data
        email_user = form.email_user.data
        psw = form.psw.data
        id_pc = form.computador.data
        tipo_usuario = form.tipo_usuario.data

        hashed_password = generate_password_hash(psw)
        
        try:
            conn.execute('INSERT INTO Usuario (Nombre_user, Email, Psw, id_tipo_usuario) VALUES (?, ?, ?, ?)', 
                         (nombre_user, email_user, hashed_password, tipo_usuario))

            id_usuario = conn.execute(
                'SELECT Id_usuario FROM Usuario WHERE Nombre_user = ? AND Email = ?', 
                (nombre_user, email_user)).fetchone()['Id_usuario']

            sistemas = conn.execute("SELECT Id_sistema FROM Sistema").fetchall()

            for sistema in sistemas:
                conn.execute(
                    "INSERT INTO Usuario_Sistema_PC (Id_usuario, Id_sistema, Id_pc, Activo) VALUES (?, ?, ?, FALSE)",
                    (id_usuario, sistema['Id_sistema'], id_pc)
                )

            user = current_user
            fecha_actual_seg = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            descripcion_hist = f" agregó a un nuevo usuario {nombre_user}. "
            conn.execute('INSERT INTO Historial (usuario_historial, descripcion, fecha, id_categoria) VALUES (?, ?, ?, 1)', 
                         (user.nombre_usuario, descripcion_hist, fecha_actual_seg))

            conn.commit()
        except Exception as e:
            print(f"Error: {e}")
        finally:
            conn.close()
        
        flash("Usuario creado exitosamente.", "success")
        return redirect(url_for('usuarios'))

    user = current_user
    num_notificaciones_totales = get_total_notifications(user.id)
    info_notificaciones = get_info_notifications(user.id)

    return render_template('usuarios.html', user=user, form=form, num_notificaciones_totales=num_notificaciones_totales, info_notificaciones=info_notificaciones)

@app.route('/editar_usuario/<int:id>', methods=['GET', 'POST'])
@requiere_tipo_usuario(1)
@login_required
def editar_usuario(id):
    conn = get_db_connection()
    
    tipo_usuario = conn.execute("SELECT id_tipo_usuario, nombre_tipo_usuario FROM Tipo_usuario").fetchall()
    form = EditarUsuarioForm()
    
    form.tipo_usuario.choices = [(tipo['id_tipo_usuario'], tipo['nombre_tipo_usuario']) for tipo in tipo_usuario]

    user_edit = conn.execute('''SELECT * FROM Usuario WHERE Usuario.Id_usuario = ?''', (id,)).fetchone()
    if request.method == 'GET':
        form.nombre_user.data = user_edit['Nombre_user']
        form.email_user.data = user_edit['Email']
        form.tipo_usuario.data = user_edit['id_tipo_usuario']

    conn.close()
    user = current_user
    num_notificaciones_totales = get_total_notifications(user.id)
    info_notificaciones = get_info_notifications(user.id)

    return render_template('editar_usuario.html', user_edit=user_edit, user=user, form=form, num_notificaciones_totales=num_notificaciones_totales, info_notificaciones=info_notificaciones)

@app.route('/editar_usuario_form', methods=['POST'])
@requiere_tipo_usuario(1)
@login_required
def editar_usuario_form():
    try:
        id_usuario = request.form['id_usuario']
        nombre_usuario = request.form['nombre_user'] 
        email = request.form['email_user']
        tipo_usuario = request.form['tipo_usuario']
        psw = request.form['psw'].strip()
        action = request.form['action']

        hashed_password = generate_password_hash(psw)

        conn = get_db_connection()

        if action == 'save':
            if psw:
                conn.execute(
                    'UPDATE Usuario SET Nombre_user = ?, Email = ?, id_tipo_usuario = ?, Psw = ? WHERE Id_usuario = ?',
                    (nombre_usuario, email, tipo_usuario, hashed_password, id_usuario)
                )
            else:
                conn.execute(
                    'UPDATE Usuario SET Nombre_user = ?, Email = ?, id_tipo_usuario = ? WHERE Id_usuario = ?',
                    (nombre_usuario, email, tipo_usuario, id_usuario)
                )
            user = current_user
            fecha_actual_seg = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            fecha_actual = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
            descripcion_hist = f"actualizó la información de un usuario {nombre_usuario}."
            conn.execute('INSERT INTO Historial (usuario_historial, descripcion, fecha, id_categoria) VALUES (?, ?, ?, 1)', (user.nombre_usuario, descripcion_hist, fecha_actual_seg))
            flash("Información del usuario actualizada con éxito.", "success")

        elif action == 'delete':
            conn.execute(
                'DELETE FROM Usuario WHERE Id_usuario = ?',
                (id_usuario,)
            )
            user = current_user
            fecha_actual_seg = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            fecha_actual = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
            descripcion_hist = f"eliminó a un usuario {nombre_usuario}."
            conn.execute('INSERT INTO Historial (usuario_historial, descripcion, fecha, id_categoria) VALUES (?, ?, ?, 1)', (user.nombre_usuario, descripcion_hist, fecha_actual_seg))
            flash("Usuario eliminado con éxito.", "danger")

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
        flash("Ocurrió un error al procesar la solicitud.", "danger")

    return redirect(url_for('usuarios'))


#BACKEND HISTORIAL
@app.route('/historial', methods=['GET'])
@login_required
def historial():
    conn = get_db_connection()

    user = current_user
    num_notificaciones_totales = get_total_notifications(user.id)
    info_notificaciones = get_info_notifications(user.id)

    page = request.args.get('page', 1, type=int)
    per_page = 10

    try:
        categoria_id = request.args.get('categoria')
        categorias = conn.execute("SELECT * FROM Categoria_historial").fetchall()

        historial_data = []
        total_records = 0

        if categoria_id:
            params = []

            query = '''
            SELECT Historial.*, Categoria_historial.nombre_categoria 
            FROM Historial 
            INNER JOIN Categoria_historial ON Categoria_historial.id_categoria = Historial.id_categoria
            WHERE 1=1
            '''
            query += ' AND Historial.id_categoria = ? ORDER BY fecha DESC'
            params.append(categoria_id)

            total_records = conn.execute(query, params).fetchall()
            total_records = len(total_records)

            offset = (page - 1) * per_page
            query += " LIMIT ? OFFSET ?"
            params += [per_page, offset]

            historial_data = conn.execute(query, params).fetchall()

            categoria_nombre = conn.execute('SELECT nombre_categoria FROM Categoria_historial WHERE id_categoria = ?', (categoria_id,)).fetchone()

        else:
            historial_data = conn.execute("SELECT * FROM Historial ORDER BY fecha DESC LIMIT ? OFFSET ?", (per_page, (page - 1) * per_page)).fetchall()
            total_records = conn.execute("SELECT COUNT(*) FROM Historial").fetchone()[0]

        total_pages = (total_records // per_page) + (1 if total_records % per_page > 0 else 0)

        start_page = max(1, page - 1)
        end_page = min(total_pages, page + 1)

        return render_template('historial.html', 
                                historial_data=historial_data, 
                                categorias=categorias, 
                                categoria_nombre=categoria_nombre if categoria_id else None,
                                user=user, 
                                num_notificaciones_totales=num_notificaciones_totales, 
                                info_notificaciones=info_notificaciones, 
                                total=total_records, 
                                per_page=per_page, 
                                page=page,
                                start_page=start_page,
                                end_page=end_page,
                                total_pages=total_pages)

    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('historial'))  # Redirigir en caso de error

    finally:
        conn.close()

@app.route('/reportes', methods=['GET', 'POST'])
@requiere_tipo_usuario(1)
@login_required
def reportes():
    conn = get_db_connection()

    search = request.args.get('search')
    date_from = request.args.get('date-from')
    date_to = request.args.get('date-to')
    page = request.args.get('page', 1, type=int) 
    per_page = 10 

    try:
        query_params = []
        total_records_params = []

        base_query = '''
            SELECT Reportes.id_reporte, Reportes.num_solicitud, Reportes.asunto, Reportes.fecha, Reportes.fecha_solucion, 
                   Reportes.descripcion, Usuario.Nombre_user 
            FROM Reportes 
            INNER JOIN Usuario ON Usuario.id_usuario = Reportes.usuario_id
            WHERE 1=1
        '''
        total_records_query = '''
            SELECT COUNT(*) 
            FROM Reportes 
            INNER JOIN Usuario ON Usuario.id_usuario = Reportes.usuario_id
            WHERE 1=1
        '''

        if search:
            base_query += '''
                AND (asunto LIKE ? OR Usuario.Nombre_user LIKE ? OR Reportes.num_solicitud LIKE ?)
            '''
            total_records_query += '''
                AND (asunto LIKE ? OR Usuario.Nombre_user LIKE ? OR Reportes.num_solicitud LIKE ?)
            '''
            search_term = '%' + search + '%'
            query_params.extend([search_term, search_term, search_term])
            total_records_params.extend([search_term, search_term, search_term])

        if date_from:
            base_query += " AND Reportes.fecha >= ?"
            total_records_query += " AND Reportes.fecha >= ?"
            query_params.append(date_from)
            total_records_params.append(date_from)

        if date_to:
            base_query += " AND Reportes.fecha <= ?"
            total_records_query += " AND Reportes.fecha <= ?"
            query_params.append(date_to)
            total_records_params.append(date_to)
        
        
        base_query += " ORDER BY fecha DESC LIMIT ? OFFSET ?"
        query_params.extend([per_page, (page - 1) * per_page])

        reportes = conn.execute(base_query, query_params).fetchall()
        total_records = conn.execute(total_records_query, total_records_params).fetchone()[0]

        total_pages = (total_records // per_page) + (1 if total_records % per_page > 0 else 0)
        start_page = max(1, page - 1)
        end_page = min(total_pages, page + 1)

        user = current_user
        num_notificaciones_totales = get_total_notifications(user.id)
        info_notificaciones = get_info_notifications(user.id)

        return render_template('reportes.html', 
                               reportes=reportes,  
                               user=user, 
                               num_notificaciones_totales=num_notificaciones_totales, 
                               info_notificaciones=info_notificaciones, 
                               total=total_records, 
                               per_page=per_page, 
                               page=page,
                               start_page=start_page,
                               end_page=end_page,
                               total_pages=total_pages)
    
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('reportes'))  # Redirigir en caso de error

    finally:
        conn.close()


@app.route('/ver_reporte/<int:id_reporte>', methods=['GET'])
@requiere_tipo_usuario(1)
@login_required
def ver_reporte(id_reporte):
    conn = get_db_connection()
    reporte = conn.execute('''
                           SELECT Reportes.id_reporte, Reportes.num_solicitud, Reportes.asunto, Reportes.fecha, Reportes.fecha_solucion, Reportes.descripcion, Reportes.archivo, Usuario.Nombre_user 
                           FROM Reportes 
                           INNER JOIN Usuario ON Usuario.id_usuario = Reportes.usuario_id
                           WHERE id_reporte = ?
                           ORDER BY Reportes.fecha DESC
                           ''', (id_reporte,)).fetchone()
    conn.close()


    user=current_user
    num_notificaciones_totales = get_total_notifications(user.id)
    info_notificaciones = get_info_notifications(user.id)

    return render_template('ver_reporte.html', reporte=reporte,  user=user, num_notificaciones_totales=num_notificaciones_totales, info_notificaciones=info_notificaciones)


@app.route('/reporte_1', methods=['GET', 'POST'])
@requiere_tipo_usuario(1)
@login_required
def reporte_1():
    if request.method == 'POST':
        nombre_sistema = request.form['nombre_sistema']
        responsable_sistema = request.form['responsable_sistema']
        direccion_unidad = request.form['direccion_unidad']
        nombre_solicitante = request.form['nombre_solicitante']
        version = request.form['version']
        descripcion = request.form['descripcion']
        responsable_ddi = request.form['responsable_ddi']
        responsable_solicitud = request.form['responsable_solicitud']
        num_implementacion = request.form['num_implementacion']
        fecha = datetime.datetime.now().strftime('%d-%m-%Y')

        pdf_template_path = 'static/pdf_plantillas/reporte_1.2.pdf'
        
        pdf_reader = PdfReader(pdf_template_path)
        pdf_writer = PdfWriter()

        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            pdf_writer.add_page(page)

        pdf_writer.update_page_form_field_values(
            pdf_writer.pages[0],
            {
                'Text2': nombre_sistema,
                'Text3': responsable_sistema,
                'Text4': direccion_unidad,
                'Text5': nombre_solicitante,
                'Text6': num_implementacion,
                'Text7': fecha,
                'Text8': version,
                'Text9': descripcion,
                'Text10': responsable_ddi,
                'Text11': responsable_solicitud
            }
        )

        output_pdf = BytesIO()
        pdf_writer.write(output_pdf)
        output_pdf.seek(0)

        return send_file(output_pdf, as_attachment=True, download_name=num_implementacion + '.pdf', mimetype='application/pdf')

    return render_template('reporte_1.html')


@app.route('/reporte_2', methods=['GET', 'POST'])
@requiere_tipo_usuario(1)
@login_required
def reporte_2():
    user = current_user
    num_notificaciones_totales = get_total_notifications(user.id)
    info_notificaciones = get_info_notifications(user.id)

    conn = get_db_connection()

    form = ReporteForm()

    if form.validate_on_submit():
        print("Datos del formulario:", request.form)
        nombre_sistema = request.form['nombre_sistema']
        responsable_sistema = request.form['responsable_sistema']
        direccion_unidad = request.form['direccion_unidad']
        nombre_solicitante = request.form['nombre_solicitante']
        version = request.form['version']
        descripcion = request.form['descripcion']
        responsable_ddi = request.form['responsable_ddi']
        responsable_solicitud = request.form['responsable_solicitud']
        fecha_solucion = request.form['fecha_solucion']
        num_solicitud = request.form['num_solicitud'].upper()
        fecha = datetime.datetime.now().strftime('%d-%m-%Y')

        existing_report = conn.execute(
            'SELECT COUNT(*) FROM Reportes WHERE num_solicitud = ?',
            (num_solicitud,)
        ).fetchone()[0]

        if existing_report > 0:
            flash("El número de solicitud ya existe.", "warning")
        else:
            fecha_solucion_str = datetime.datetime.strptime(fecha_solucion, '%Y-%m-%d').strftime('%d-%m-%Y')
            pdf_template_path = 'static/pdf_plantillas/reporte_2.pdf'

            pdf_reader = PdfReader(pdf_template_path)
            pdf_writer = PdfWriter()

            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                pdf_writer.add_page(page)

            pdf_writer.update_page_form_field_values(
                pdf_writer.pages[0],
                {
                    'Text1': nombre_sistema,
                    'Text2': responsable_sistema,
                    'Text3': direccion_unidad,
                    'Text4': nombre_solicitante,
                    'Text5': num_solicitud,
                    'Text6': fecha,
                    'Text7': version,
                    'Text8': fecha_solucion_str,
                    'Text9': descripcion
                },
            )
            pdf_writer.update_page_form_field_values(
                pdf_writer.pages[1],
                {
                    'Text10': responsable_ddi,
                    'Text11': responsable_solicitud
                }
            )

            image_file = form.file.data
            if image_file:

                image_path = os.path.join('uploads', secure_filename(image_file.filename))
                image_file.save(image_path)

                img = Image.open(image_path)

                img_pdf = BytesIO()
                img.convert('RGB').save(img_pdf, format='PDF')
                img_pdf.seek(0)

                image_reader = PdfReader(img_pdf)
                pdf_writer.add_page(image_reader.pages[0])

            output_pdf = BytesIO()
            pdf_writer.write(output_pdf)
            output_pdf.seek(0)
            
            filename = secure_filename(f'{num_solicitud}.pdf')
            file_path = os.path.join('pdf_reportes', filename)
            with open(file_path, 'wb') as f:
                f.write(output_pdf.read())
            
            conn.execute(
                'INSERT INTO Reportes (usuario_id, num_solicitud, asunto, descripcion, fecha, fecha_solucion, archivo) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (user.id, num_solicitud, nombre_sistema, descripcion, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), fecha_solucion, filename)
            )

            fecha_actual_seg = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            descripcion_hist = f" ha realizado un nuevo reporte. ASUNTO: {nombre_sistema}."
            conn.execute('INSERT INTO Historial (usuario_historial, descripcion, fecha, id_categoria) VALUES (?, ?, ?, 4)', (user.nombre_usuario, descripcion_hist, fecha_actual_seg))

            conn.commit()
            conn.close()
            
            flash("Reporte creado exitosamente.", "success")
            return redirect(url_for('reportes'))

    else:
        print("Errores de validación:", form.errors)
        
    return render_template('reporte_2.html', form=form, user=user, num_notificaciones_totales=num_notificaciones_totales, info_notificaciones=info_notificaciones)

@app.route('/ver_reporte/<filename>')
@requiere_tipo_usuario(1)
@login_required
def uploaded_file(filename):
    return send_from_directory('pdf_reportes', filename)

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

