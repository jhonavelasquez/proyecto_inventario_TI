from flask import Blueprint, render_template, redirect, request, flash, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from forms import CrearUsuarioForm, EditarUsuarioForm
from model import get_db_connection
from utils.decorators import requiere_tipo_usuario, get_info_notifications, get_total_notifications
import datetime



usuarios_bp = Blueprint('usuarios', __name__)

@usuarios_bp.route('/usuarios', methods=['GET'])
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

@usuarios_bp.route('/crear_usuario', methods=['GET', 'POST'])
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
        return redirect(url_for('usuarios.usuarios'))

    user = current_user
    num_notificaciones_totales = get_total_notifications(user.id)
    info_notificaciones = get_info_notifications(user.id)

    return render_template('usuarios.html', user=user, form=form, num_notificaciones_totales=num_notificaciones_totales, info_notificaciones=info_notificaciones)

@usuarios_bp.route('/editar_usuario/<int:id>', methods=['GET', 'POST'])
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

@usuarios_bp.route('/editar_usuario_form', methods=['POST'])
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

    return redirect(url_for('usuarios.usuarios'))
