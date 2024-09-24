import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from model import *
import datetime
import os
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
from flask_mail import Mail, Message
import threading
import time
import schedule

app = Flask(__name__)
app.secret_key = 'd9ddb8a50af95ba9a24052cb926e3b64ef04578fb6dc3d9b6ab9a13eec464195'

hrs_revisión = "16:46"

#CONFIGURACION NOTIFICACIONES GMAIL
app.config['MAIL_SERVER'] = 'smtp.gmail.com'    # Servidor SMTP de Gmail
app.config['MAIL_PORT'] = 587                   # Puerto para TLS
app.config['MAIL_USE_TLS'] = True               # Usar TLS
app.config['MAIL_USE_SSL'] = False              # Deshabilitar SSL si usas TLS
app.config['MAIL_USERNAME'] = 'jonathan.vr484@gmail.com'   # Tu email de Gmail
app.config['MAIL_PASSWORD'] = 'ycfs vvod evqw emwy'  # Contraseña de aplicación de Gmail
app.config['MAIL_DEFAULT_SENDER'] = 'jonathan.vr484@gmail.com'  # Email predeterminado de envío

mail = Mail(app)

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


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre_usuario = request.form['nombre_usuario']
        password = request.form['contrasena']
        user = Usuario.get_by_nombre_usuario(nombre_usuario)

        if user:
            print(f"user: {user.nombre_usuario}, psw: {user.password}")  # Esto es solo para depuración

        if user and check_password_hash(user.password, password):
            print("Contraseña correcta") 
            login_user(user)
            flash('Inicio de sesión exitoso.', 'success')
            return redirect(url_for('index'))
        else:
            print("Credenciales inválidas")
            flash('Credenciales inválidas. Por favor, inténtalo de nuevo.', 'danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesion cerrada correctamente', 'warning')
    return redirect(url_for('login'))

# BACKEND SISTEMA
@app.route('/', methods=['GET'])
@login_required
def index():
    conn = get_db_connection()
    sistema_id = request.args.get('sistema')
    search_query = request.args.get('search', '')

    sistemas = conn.execute("SELECT * FROM Sistema").fetchall()
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

    return render_template('index.html', user_pc_data=user_pc_data, sistemas=sistemas, pcs=pcs,  user=current_user, num_notificaciones_totales=num_notificaciones_totales, info_notificaciones=info_notificaciones)

@app.route('/crear_sistema', methods=['POST'])
@login_required
def crear_sistema():
    conn = get_db_connection()
    nombre_sistema = request.form['nombre_sistema']

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
    descripcion_hist= (f" agregó un nuevo sistema.  {nombre_sistema}.  {fecha_actual}")
    conn.execute('INSERT INTO Historial (usuario_historial, descripcion, fecha, id_categoria) VALUES (?,?,?, 2)', (user.nombre_usuario,descripcion_hist,fecha_actual_seg))

    conn.commit()
    conn.close()

    flash("Sistema creado exitosamente.", "success")
    return redirect(url_for('index'))


@app.route('/eliminar_sistema', methods=['POST'])
@login_required
def eliminar_sistema():
    conn = get_db_connection()
    sistema_id = request.form.get('sistema')
    
    if sistema_id:
        sistema = conn.execute('SELECT Nombre_sistema FROM Sistema WHERE Id_sistema = ?', (sistema_id,)).fetchone()
        nombre_sistema = sistema['Nombre_sistema'] 
        
        if sistema:
            conn.execute('DELETE FROM Sistema WHERE Id_sistema = ?', (sistema_id,))
            
            user = current_user
            fecha_actual_seg = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            fecha_actual = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
            descripcion_hist= (f" eliminó el sistema {nombre_sistema}.  [{fecha_actual}]")
            conn.execute('INSERT INTO Historial (usuario_historial, descripcion, fecha, id_categoria) VALUES (?,?,?, 2)', (user.nombre_usuario,descripcion_hist,fecha_actual_seg))
            
            flash(f"{nombre_sistema} ha sido eliminado.", "warning")
            
            conn.commit()
            conn.close()
    
    return redirect(url_for('index'))

@app.route('/editar_sistema/<int:id_sistema>/<int:id_usuario>/<int:id_pc>', methods=['GET', 'POST'])
@login_required
def editar_sistema(id_sistema, id_usuario, id_pc):
    conn = get_db_connection()

    try:
        if request.method == 'POST':
            nuevo_id_pc = request.form.get('nuevo_Id_pc')
            activo = request.form.get('Activo')

            conn.execute('''
                UPDATE Usuario_Sistema_PC 
                SET Activo = ?, Id_pc = ?
                WHERE Id_usuario = ? AND Id_sistema = ? AND Id_pc = ?
            ''', (activo, nuevo_id_pc, id_usuario, id_sistema, id_pc))

            nombre_user = conn.execute(
                'SELECT Nombre_user FROM Usuario WHERE Id_usuario = ?', (id_usuario,)).fetchone()
            nombre_sis = conn.execute(
                'SELECT Nombre_sistema FROM Sistema WHERE Id_sistema = ?', (id_sistema,)).fetchone()

            
            nombre_usuario = nombre_user['Nombre_user']
            nombre_sistema = nombre_sis['Nombre_sistema']

            user = current_user
            fecha_actual_seg = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            fecha_actual = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
            descripcion_hist = (f"Actualizó {nombre_sistema} de {nombre_usuario}. {fecha_actual}")
            conn.execute('INSERT INTO Historial (usuario_historial, descripcion, fecha, id_categoria) VALUES (?,?,?, 2)', 
                         (user.nombre_usuario, descripcion_hist, fecha_actual_seg))

            conn.commit()
            flash("¡El PC o el estado del sistema han sido actualizados!", "success")
            return redirect(url_for('index'))

        user_pc = conn.execute('''
            SELECT Usuario.Id_usuario, Usuario.Nombre_user, Usuario_Sistema_PC.Id_pc, Pc.Nombre_pc, 
                   Sistema.Nombre_sistema, Usuario_Sistema_PC.Activo, Usuario_Sistema_PC.Id_sistema
            FROM Usuario
            INNER JOIN Usuario_Sistema_PC ON Usuario.Id_usuario = Usuario_Sistema_PC.Id_usuario
            INNER JOIN Pc ON Pc.Id_pc = Usuario_Sistema_PC.Id_pc
            INNER JOIN Sistema ON Usuario_Sistema_PC.Id_sistema = Sistema.Id_sistema
            WHERE Usuario_Sistema_PC.Id_sistema = ? AND Usuario_Sistema_PC.Id_usuario = ? AND Usuario_Sistema_PC.Id_pc = ?
        ''', (id_sistema, id_usuario, id_pc)).fetchone()

        pcs = conn.execute("SELECT * FROM Pc").fetchall()
        

    except Exception as e:
        flash(f"Error: {str(e)}", "danger")

    finally:
        conn.close()

    user=current_user
    num_notificaciones_totales = get_total_notifications(user.id)
    info_notificaciones = get_info_notifications(user.id)

    return render_template('editar_sistema.html', user_pc=user_pc, pcs=pcs, user=user, num_notificaciones_totales=num_notificaciones_totales, info_notificaciones=info_notificaciones)

# BACKEND COMPUTADOR
@app.route('/computadores', methods=['GET'])
@login_required
def computadores():
    conn = get_db_connection()

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

    return render_template('computadores.html', filtro_pcs=filtro_pcs,  user=user, num_notificaciones_totales=num_notificaciones_totales, info_notificaciones=info_notificaciones)

@app.route('/crear_computador', methods=['POST'])
@login_required
def crear_computador():
    if request.method == 'POST':
        nombre_pc = request.form['nombre_computador']
        placa_pc = request.form['nombre_placa']
        almacenamiento = request.form.get('disco')
        ram = request.form.get('ram')
        nombre_fuente = request.form['fuente']

        conn = get_db_connection()
        conn.execute('INSERT INTO Pc ( Nombre_pc, Placa, Almacenamiento, Ram, Fuente) VALUES (?,?,?,?,?)', (nombre_pc, placa_pc, almacenamiento, ram, nombre_fuente))

        user = current_user
        fecha_actual_seg = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        fecha_actual = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
        descripcion_hist= (f" agregó un nuevo computador.  {nombre_pc}.  {fecha_actual}")
        conn.execute('INSERT INTO Historial (usuario_historial, descripcion, fecha, id_categoria) VALUES (?,?,?, 3)', (user.nombre_usuario,descripcion_hist,fecha_actual_seg))
        
        conn.commit()
        conn.close()
        
        flash("Computador agregado exitosamente.", "success")
        return redirect('computadores')
    return render_template('computadores.html')

@app.route('/editar_computador/<int:id_pc>', methods=['GET'])
@login_required
def editar_computador(id_pc):
    conn = get_db_connection()
    
    pc = conn.execute('''
        SELECT *
        FROM Pc
        WHERE Pc.Id_pc = ?
    ''', (id_pc,)).fetchone()
    conn.close()

    user=current_user
    num_notificaciones_totales = get_total_notifications(user.id)
    info_notificaciones = get_info_notifications(user.id)
    
    return render_template('editar_computador.html', pc=pc,  user=user, num_notificaciones_totales=num_notificaciones_totales, info_notificaciones=info_notificaciones)

@app.route('/editar_computador_form', methods=['POST'])
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
        descripcion_hist= (f" actualizó la información de un computador.  {nombre_pc}.  {fecha_actual}")
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
        descripcion_hist= (f" eliminó un computador.  {nombre_pc}.  {fecha_actual}")
        conn.execute('INSERT INTO Historial (usuario_historial, descripcion, fecha, id_categoria) VALUES (?,?,?, 3)', (user.nombre_usuario,descripcion_hist,fecha_actual_seg))
        flash("Computador eliminado con éxito.", "danger")

    conn.commit()
    conn.close()

    return redirect(url_for('computadores'))

# BACKEND USUARIO
@app.route('/usuarios', methods=['GET'])
@login_required
def usuarios():
    conn = get_db_connection()

    search_query = request.args.get('search', '')

    query = '''SELECT Usuario.Id_usuario, Usuario.Nombre_user, Usuario.Email FROM Usuario Where 1 = 1'''
    pcs = conn.execute("SELECT * FROM Pc").fetchall()

    params = []
    if search_query:
        query += ' AND (Usuario.Nombre_user LIKE ?  OR Usuario.Id_usuario LIKE ?)'
        params.extend(['%' + search_query + '%', '%' + search_query + '%'])

    users = conn.execute(query, params).fetchall()
    conn.close()

    user=current_user
    num_notificaciones_totales = get_total_notifications(user.id)
    info_notificaciones = get_info_notifications(user.id)

    return render_template('usuarios.html', users=users, pcs=pcs,  user=user, num_notificaciones_totales=num_notificaciones_totales, info_notificaciones=info_notificaciones)

@app.route('/crear_usuario', methods=['GET', 'POST'])
@login_required
def crear_usuario():
    if request.method == 'POST':
        nombre_user = request.form['nombre_user']
        email_user = request.form['email_user']
        psw = request.form['psw']
        id_pc = request.form.get('computador') 

        hashed_password = generate_password_hash(psw)
        conn = get_db_connection()

        try:
            conn.execute('INSERT INTO Usuario (Nombre_user, Email, Psw) VALUES (?, ?, ?)', (nombre_user, email_user, hashed_password))

            id_usuario = conn.execute(
                'SELECT Id_usuario FROM Usuario WHERE Nombre_user = ? AND Email = ?', (nombre_user, email_user)).fetchone()['Id_usuario']

            sistemas = conn.execute("SELECT Id_sistema FROM Sistema").fetchall()

            for sistema in sistemas:
                print(f"Inserción: Usuario ID: {id_usuario}, Sistema ID: {sistema['Id_sistema']}, PC ID: {id_pc}")
                conn.execute(
                    "INSERT INTO Usuario_Sistema_PC (Id_usuario, Id_sistema, Id_pc, Activo) VALUES (?, ?, ?, FALSE)",
                    (id_usuario, sistema['Id_sistema'], id_pc)
                )
                print("se agrego a sistema")

            user = current_user
            fecha_actual_seg = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            fecha_actual = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
            descripcion_hist = (f" agregó a un nuevo usuario {nombre_user}.  {fecha_actual}")
            conn.execute('INSERT INTO Historial (usuario_historial, descripcion, fecha, id_categoria) VALUES (?,?,?, 1)', (user.nombre_usuario, descripcion_hist, fecha_actual_seg))

            conn.commit()
        except Exception as e:
            print(f"Error: {e}")
        finally:
            conn.close()
        
        flash("Usuario creado exitosamente.", "success")
        return redirect(url_for('usuarios'))
    user=current_user
    num_notificaciones_totales = get_total_notifications(user.id)
    info_notificaciones = get_info_notifications(user.id)

    return render_template('usuarios.html', user=user, num_notificaciones_totales=num_notificaciones_totales, info_notificaciones=info_notificaciones)

@app.route('/editar_usuario/<int:id>', methods=['GET'])
@login_required
def editar_usuario(id):
    conn = get_db_connection()
    
    use = conn.execute('''
        SELECT *
        FROM Usuario
        WHERE Usuario.Id_usuario = ?
    ''', (id,)).fetchone()
    conn.close()

    user=current_user
    num_notificaciones_totales = get_total_notifications(user.id)
    info_notificaciones = get_info_notifications(user.id)
    
    return render_template('editar_usuario.html', use=use,  user=user, num_notificaciones_totales=num_notificaciones_totales, info_notificaciones=info_notificaciones)

@app.route('/editar_usuario_form', methods=['POST'])
@login_required
def editar_usuario_form():
    id_usuario = request.form['id_usuario']
    nombre_usuario = request.form['nombre_usuario']
    email = request.form['email']
    action = request.form['action']

    conn = get_db_connection()

    if action == 'save':
        conn.execute(
            'UPDATE Usuario SET Nombre_user = ?, Email = ? WHERE Id_usuario = ?',
            (nombre_usuario, email, id_usuario)
        )

        user = current_user
        fecha_actual_seg = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        fecha_actual = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
        descripcion_hist= (f" actualizó la información de un usuario {nombre_usuario}.  {fecha_actual}")
        conn.execute('INSERT INTO Historial (usuario_historial, descripcion, fecha, id_categoria) VALUES (?,?,?, 1)', (user.nombre_usuario,descripcion_hist,fecha_actual_seg))
        flash("Información del usuario actualizada con éxito.", "success")

    elif action == 'delete':
        conn.execute(
            'DELETE FROM Usuario WHERE Id_usuario = ?',
            (id_usuario,)
        )
        user = current_user
        fecha_actual_seg = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        fecha_actual = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
        descripcion_hist= (f" eliminó a un usuario {nombre_usuario}.  {fecha_actual}")
        conn.execute('INSERT INTO Historial (usuario_historial, descripcion, fecha, id_categoria) VALUES (?,?,?, 1)', (user.nombre_usuario,descripcion_hist,fecha_actual_seg))
        flash("Usuario eliminado con éxito.", "danger")

    

    conn.commit()
    conn.close()

    return redirect(url_for('usuarios'))

#BACKEND HISTORIAL
@app.route('/historial', methods=['GET'])
@login_required
def historial():
    conn = get_db_connection()

    user=current_user
    num_notificaciones_totales = get_total_notifications(user.id)
    info_notificaciones = get_info_notifications(user.id)

    try:
        categoria_id = request.args.get('categoria')
        categorias = conn.execute("SELECT * FROM Categoria_historial").fetchall()

        if categoria_id:
            params = []

            query = '''
            SELECT * FROM Historial 
            INNER JOIN Categoria_historial ON Categoria_historial.id_categoria = Historial.id_categoria
            WHERE 1=1
            '''
            query += ' AND Historial.id_categoria = ? ORDER BY fecha DESC'
            params.append(categoria_id)

            historial_data = conn.execute(query, params).fetchall()

            categoria_nombre = conn.execute('SELECT nombre_categoria FROM Categoria_historial WHERE id_categoria = ?', (categoria_id,)).fetchone()

            return render_template('historial.html', historial_data=historial_data, categorias=categorias, categoria_nombre=categoria_nombre,  user=user, num_notificaciones_totales=num_notificaciones_totales, info_notificaciones=info_notificaciones)
        
        
        registros = conn.execute("SELECT * FROM Historial ORDER BY fecha DESC").fetchall()

        return render_template('historial.html', registros=registros, categorias=categorias,  user=user, num_notificaciones_totales=num_notificaciones_totales, info_notificaciones=info_notificaciones)

    except Exception as e:
        flash(f"Error: {str(e)}", "danger")

    finally:
        conn.close()

#BACKEND REPORTES
@app.route('/reportes', methods=['GET', 'POST'])
@login_required
def reportes():
    conn = get_db_connection()
    
    search = request.args.get('search')
    
    if search:
        query = f"SELECT * FROM Reportes WHERE asunto LIKE ? OR usuario_id LIKE ? ORDER BY fecha DESC"
        reportes = conn.execute(query, ('%' + search + '%', '%' + search + '%')).fetchall()
    else:
        reportes = conn.execute("SELECT * FROM Reportes ORDER BY fecha DESC").fetchall()
    
    conn.close()

    user=current_user
    num_notificaciones_totales = get_total_notifications(user.id)
    info_notificaciones = get_info_notifications(user.id)

    return render_template('reportes.html', reportes=reportes,  user=user, num_notificaciones_totales=num_notificaciones_totales, info_notificaciones=info_notificaciones)

@app.route('/ver_reporte/<int:id_reporte>', methods=['GET'])
@login_required
def ver_reporte(id_reporte):
    conn = get_db_connection()
    reporte = conn.execute("SELECT * FROM Reportes WHERE id_reporte = ?", (id_reporte,)).fetchone()
    conn.close()

    user=current_user
    num_notificaciones_totales = get_total_notifications(user.id)
    info_notificaciones = get_info_notifications(user.id)

    return render_template('ver_reporte.html', reporte=reporte,  user=user, num_notificaciones_totales=num_notificaciones_totales, info_notificaciones=info_notificaciones)


@app.route('/reporte_1', methods=['GET', 'POST'])
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
@login_required
def reporte_2():
    user=current_user
    num_notificaciones_totales = get_total_notifications(user.id)
    info_notificaciones = get_info_notifications(user.id)

    if request.method == 'POST':
        nombre_sistema = request.form['nombre_sistema']
        responsable_sistema = request.form['responsable_sistema']
        direccion_unidad = request.form['direccion_unidad']
        nombre_solicitante = request.form['nombre_solicitante']
        version = request.form['version']
        descripcion = request.form['descripcion']
        responsable_ddi = request.form['responsable_ddi']
        responsable_solicitud = request.form['responsable_solicitud']
        fecha_solucion = request.form['fecha_solucion']
        num_solicitud = request.form['num_solicitud']
        fecha = datetime.datetime.now().strftime('%d-%m-%Y')

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

        output_pdf = BytesIO()
        pdf_writer.write(output_pdf)
        output_pdf.seek(0)
        
        filename = secure_filename(f'{num_solicitud}.pdf')
        file_path = os.path.join('pdf_reportes',filename)
        with open(file_path, 'wb') as f:
            f.write(output_pdf.read())
        
        conn = get_db_connection()
        
        conn.execute(
            'INSERT INTO Reportes (usuario_id, asunto, descripcion, fecha, fecha_solucion, archivo) VALUES (?, ?, ?, ?, ?, ?)',
            (user.id, nombre_sistema, descripcion ,datetime.datetime.now().strftime('%Y-%m-%d %H:%M'), fecha_solucion, filename)
        )

        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M'), " ---- ", fecha_solucion)

        fecha_actual_seg = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        fecha_actual = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
        descripcion_hist= (f" ha realizado un nuevo reporte. ASUNTO: {nombre_sistema}.  {fecha_actual}")
        conn.execute('INSERT INTO Historial (usuario_historial, descripcion, fecha, id_categoria) VALUES (?,?,?, 4)', (user.nombre_usuario,descripcion_hist,fecha_actual_seg))

        conn.commit()
        conn.close()
        
        flash("Reporte creado exitosamente.", "success")

        return redirect(url_for('reportes'))

    return render_template('reporte_2.html', user=user, num_notificaciones_totales=num_notificaciones_totales, info_notificaciones=info_notificaciones)

@app.route('/ver_reporte/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory('pdf_reportes', filename)


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
        'SELECT * FROM Notificaciones WHERE id_usuario = ? ORDER BY id_notificacion DESC LIMIT 6',
        (user_id,)
    ).fetchall()
    conn.close()

    return info_notifiaciones

@app.route('/marcar_notificaciones_leidas', methods=['POST'])
@login_required
def marcar_notificaciones_leidas():
    user_id = current_user.id
    conn = get_db_connection()

    conn.execute('UPDATE Notificaciones SET leido = true WHERE id_usuario = ? AND leido = false', (user_id,))
    conn.commit()
    conn.close()

    return '', 204

@app.route('/notificaciones', methods=['GET'])
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
        
        # conn.execute('UPDATE Notificaciones SET leido = true WHERE id_usuario = ? AND leido = false', (user_id,))
        # conn.commit()  

    num_notificaciones_totales = conn.execute(
        'SELECT COUNT(*) FROM Notificaciones WHERE id_usuario = ?',
        (user_id,)
    ).fetchone()[0]

    return render_template('prueba.html', num_notificaciones_enviadas=num_notificaciones_enviadas, num_notificaciones_totales=num_notificaciones_totales)


#NOTIFICACION POR EMAIL
def enviar_correo(destinatario, asunto, cuerpo):
    mail = Mail(app)
    msg = Message(asunto, recipients=[destinatario])
    msg.body = cuerpo
    try:
        mail.send(msg)
        print(f"Correo enviado a {destinatario}")
    except Exception as e:
        print(f"Error enviando correo: {e}")

def enviar_recordatorios():
    with app.app_context():
        conn = get_db_connection()
        print("Revisión---")

        try:
            today = datetime.datetime.now()
            fecha_15_dias = today + datetime.timedelta(days=15)

            today_str = today.strftime('%Y-%m-%d')
            fecha_15_dias_str = fecha_15_dias.strftime('%Y-%m-%d')

            reportes = conn.execute(
                'SELECT * FROM Reportes WHERE fecha_solucion BETWEEN ? AND ?',
                (today, fecha_15_dias)
            ).fetchall()

            print(reportes)
            print(f"Fecha de hoy: {today_str}")
            print(f"Fecha en 15 días: {fecha_15_dias_str}")

            for reporte in reportes:
                usuario_id = reporte['usuario_id']  
                nombre_sistema = reporte['asunto']
                fecha_solucion = reporte['fecha_solucion']


                notificacion_enviada = conn.execute(
                    'SELECT * FROM Notificaciones WHERE id_reporte = ? AND fecha_notificacion = ?',
                    (reporte['id_reporte'], today_str)
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
                        'INSERT INTO Notificaciones ( id_usuario, id_reporte, fecha_notificacion, mensaje, leido) VALUES (?, ?, ?, ?, false)',
                        (usuario_id, reporte['id_reporte'], today_str, subject) 
                    )
                    conn.commit()
        
        except Exception as e:
            print(f"Error al enviar recordatorios: {e}")
        finally:
            conn.close()



















#REVISION DIARIA NOTIFICACION
def iniciar_revisiones_periodicas():
    schedule.every(1).minutes.do(enviar_recordatorios)
    schedule.every().day.at(hrs_revisión).do(enviar_recordatorios)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    hilo_revisar_reportes = threading.Thread(target=iniciar_revisiones_periodicas)
    hilo_revisar_reportes.start()

    app.run(debug=True, use_reloader=False)


