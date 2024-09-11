import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from model import *
import datetime
import os
from bs4 import BeautifulSoup


from PyPDF2 import PdfReader, PdfWriter,PdfFileMerger
from io import BytesIO


app = Flask(__name__)
app.secret_key = 's3cr3t_k3y_12345'
app.config['UPLOAD_FOLDER'] = 'uploads'  # Carpeta para almacenar archivos subidos
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}  # Tipos de archivos permitidos

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


@app.route('/', methods=['GET', 'POST'])
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
@app.route('/index', methods=['GET'])
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

    return render_template('index.html', user_pc_data=user_pc_data, sistemas=sistemas, pcs=pcs,  user=current_user)

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
            flash(f"{nombre_sistema} ha sido eliminado.", "warning")
            conn.commit()
            conn.close()
    
    return redirect(url_for('index'))

@app.route('/editar_sistema/<int:id_sistema>/<int:id_usuario>/<int:id_pc>', methods=['GET', 'POST'])
@login_required
def editar_sistema(id_sistema, id_usuario, id_pc):
    conn = get_db_connection()

    if request.method == 'POST':
        nuevo_id_pc = request.form.get('nuevo_Id_pc')
        activo = request.form.get('Activo')

        conn.execute('''
            UPDATE Usuario_Sistema_PC 
            SET Activo = ?, Id_pc = ?
            WHERE Id_usuario = ? AND Id_sistema = ? AND Id_pc = ?
        ''', (activo, nuevo_id_pc, id_usuario, id_sistema, id_pc))

        conn.commit()
        conn.close()

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
    conn.close()
    
    return render_template('editar_sistema.html', user_pc=user_pc, pcs=pcs)

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

    return render_template('computadores.html', filtro_pcs=filtro_pcs)

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

        conn.commit()
        conn.close()
        
        flash("Computador creado exitosamente.", "success")
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
    
    return render_template('editar_computador.html', pc=pc)

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
        flash("Información del computador actualizada con éxito.", "success")
    elif action == 'delete':
        conn.execute(
            'DELETE FROM Pc WHERE Id_pc = ?',
            (id_pc,)
        )
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

    return render_template('usuarios.html', users=users, pcs=pcs)

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
            fecha_actual = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
            descripcion_hist = (f" agregó a un nuevo usuario {nombre_user}.  {fecha_actual}")
            conn.execute('INSERT INTO Historial (usuario_historial, descripcion, fecha) VALUES (?,?,?)', (user.nombre_usuario, descripcion_hist, fecha_actual))

            conn.commit()
        except Exception as e:
            print(f"Error: {e}")
        finally:
            conn.close()
        
        flash("Usuario creado exitosamente.", "success")
        return redirect(url_for('usuarios'))

    return render_template('usuarios.html')

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
    
    return render_template('editar_usuario.html', use=use)

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
        flash("Información del usuario actualizada con éxito.", "success")
    elif action == 'delete':
        conn.execute(
            'DELETE FROM Usuario WHERE Id_usuario = ?',
            (id_usuario,)
        )
        user = current_user
        fecha_actual = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        descripcion_hist= (f" eliminó a un usuario {nombre_usuario}.  {fecha_actual}")
        conn.execute('INSERT INTO Historial (usuario_historial, descripcion, fecha) VALUES (?,?,?)', (user.nombre_usuario,descripcion_hist,fecha_actual))
        flash("Usuario eliminado con éxito.", "danger")

    

    conn.commit()
    conn.close()

    return redirect(url_for('usuarios'))

@app.route('/historial', methods=['GET'])
@login_required
def historial():
    conn = get_db_connection()

    registros = conn.execute("SELECT * FROM Historial ORDER BY fecha DESC").fetchall()
    conn.close()

    return render_template('historial.html', registros=registros)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/reportes', methods=['GET', 'POST'])
@login_required
def reportes():
    # Conexión a la base de datos
    conn = get_db_connection()
    
    # Obtener filtros de búsqueda (si existen)
    search = request.args.get('search')
    
    if search:
        # Buscar reportes por asunto o ID de usuario
        query = f"SELECT * FROM Reportes WHERE asunto LIKE ? OR usuario_id LIKE ? ORDER BY fecha DESC"
        reportes = conn.execute(query, ('%' + search + '%', '%' + search + '%')).fetchall()
    else:
        # Obtener todos los reportes
        reportes = conn.execute("SELECT * FROM Reportes ORDER BY fecha DESC").fetchall()
    
    conn.close()
    return render_template('reportes.html', reportes=reportes)

@app.route('/crear_reporte', methods=['POST'])
@login_required
def crear_reporte():
    # Recopilar datos del formulario
    asunto = request.form['asunto']
    descripcion = request.form['descripcion']
    user = current_user
    
    file = request.files.get('file')
    file_path = None
    
    if file and file.filename:
        filename = secure_filename(file.filename)
        file_path = os.path.join(filename)
        file.save(file_path)
    
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO Reportes (usuario_id, asunto, descripcion, fecha, archivo) VALUES (?, ?, ?, ?, ?)',
        (user.nombre_usuario, asunto, descripcion, datetime.datetime.now().strftime('%Y-%m-%d %H:%M'), file_path)
    )
    conn.commit()
    conn.close()
    
    flash("Reporte creado exitosamente.", "success")
    return redirect(url_for('reportes'))

@app.route('/ver_reporte/<int:id_reporte>', methods=['GET'])
@login_required
def ver_reporte(id_reporte):
    conn = get_db_connection()
    reporte = conn.execute("SELECT * FROM Reportes WHERE id_reporte = ?", (id_reporte,)).fetchone()
    conn.close()
    return render_template('ver_reporte.html', reporte=reporte)

@app.route('/ver_reporte/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory('uploads', filename)


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

        pdf_template_path = 'static/pdf/reporte_1.2.pdf'
        
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

        pdf_template_path = 'static/pdf/reporte_2.pdf'
        
        # Leer el PDF base
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
                'Text8': fecha_solucion,
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

        return send_file(output_pdf, as_attachment=True, download_name=num_solicitud + '.pdf', mimetype='application/pdf')

    return render_template('reporte_2.html')