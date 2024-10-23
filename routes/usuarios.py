from flask import Blueprint, render_template, redirect, request, flash, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from forms import CrearUsuarioForm, EditarUsuarioForm, EditarMiCuenta
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
    rol_query = request.args.get('rol', '')

    cursor= conn.cursor()
    cursor.execute("SELECT Id_pc, Nombre_pc FROM Pc")
    pcs = cursor.fetchall()

    cursor.execute("SELECT id_tipo_usuario, nombre_tipo_usuario FROM Tipo_usuario")
    tipo_usuario = cursor.fetchall()

    form = CrearUsuarioForm()

    form.computador.choices = [(pc[0], pc[1]) for pc in pcs]
    form.tipo_usuario.choices = [(tipo[0], tipo[1]) for tipo in tipo_usuario]

    query = '''SELECT Usuario.Id_usuario, Usuario.Nombre_user, Usuario.Email, Usuario.id_tipo_usuario, Tipo_usuario.nombre_tipo_usuario
                FROM Usuario
                INNER JOIN Tipo_usuario ON Tipo_usuario.id_tipo_usuario = Usuario.id_tipo_usuario
                Where 1 = 1'''
    
    params = []
    if search_query:
        query += ' AND (Usuario.Nombre_user LIKE %s  OR Usuario.Id_usuario LIKE %s)'
        params.extend(['%' + search_query + '%', '%' + search_query + '%'])
    
    if rol_query:
        query += ' AND Usuario.id_tipo_usuario LIKE %s'
        params.extend(['%' + rol_query + '%'])
    
    cursor.execute(query, params)
    users = cursor.fetchall()
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

    cursor= conn.cursor()
    cursor.execute("SELECT Id_pc, Nombre_pc FROM Pc")
    pcs = cursor.fetchall()
    
    cursor.execute("SELECT id_tipo_usuario, nombre_tipo_usuario FROM Tipo_usuario")
    tipo_usuario = cursor.fetchall()

    form = CrearUsuarioForm()

    form.computador.choices = [(pc[0], pc[1]) for pc in pcs]
    form.tipo_usuario.choices = [(tipo[0], tipo[1]) for tipo in tipo_usuario]

    if form.validate_on_submit():
        nombre_user = form.nombre_user.data

        cursor.execute("SELECT Nombre_user FROM Usuario")
        usuarios = cursor.fetchall()

        for usuario in usuarios:
                if nombre_user == usuario[0]:
                    flash("El nombre de usuario ya existe.", "warning")
                    conn.close()
                    return redirect(url_for('usuarios.usuarios'))

        email_user = form.email_user.data
        psw = form.psw.data
        id_pc = form.computador.data
        tipo_usuario = form.tipo_usuario.data

        hashed_password = generate_password_hash(psw)
        
        try:
            cursor.execute('INSERT INTO Usuario (Nombre_user, Email, Psw, id_tipo_usuario) VALUES (%s, %s, %s, %s)', 
                         (nombre_user, email_user, hashed_password, tipo_usuario))

            cursor.execute(
                'SELECT Id_usuario FROM Usuario WHERE Nombre_user = %s AND Email = %s', 
                (nombre_user, email_user))

            id_usuario = cursor.fetchone()[0]
            
            cursor.execute("SELECT Id_sistema FROM Sistema")
            sistemas =  cursor.fetchall()

            for sistema in sistemas:
                cursor.execute(
                    "INSERT INTO Usuario_Sistema_PC (Id_usuario, Id_sistema, Id_pc, Activo) VALUES (%s, %s, %s, FALSE)",
                    (id_usuario, sistema[0], id_pc)
                )

            user = current_user
            fecha_actual_seg = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            descripcion_hist = f" agregó a un nuevo usuario {nombre_user}. "
            cursor.execute('INSERT INTO Historial (usuario_historial, descripcion, fecha, id_categoria) VALUES (%s, %s, %s, 1)', 
                         (user.nombre_usuario, descripcion_hist, fecha_actual_seg))
            
            conn.commit()
            flash("Usuario creado exitosamente.", "success")
            return redirect(url_for('usuarios.usuarios'))
        
        except Exception as e:
            print(f"Error: {e}")
        finally:
            conn.close()
        
        

    user = current_user
    num_notificaciones_totales = get_total_notifications(user.id)
    info_notificaciones = get_info_notifications(user.id)

    return render_template('usuarios.html', user=user, form=form, num_notificaciones_totales=num_notificaciones_totales, info_notificaciones=info_notificaciones)

@usuarios_bp.route('/editar_usuario/<int:id>', methods=['GET', 'POST'])
@requiere_tipo_usuario(1)
@login_required
def editar_usuario(id):
    conn = get_db_connection()
    
    cursor = conn.cursor()
    cursor.execute("SELECT id_tipo_usuario, nombre_tipo_usuario FROM Tipo_usuario")
    tipo_usuario = cursor.fetchall()
    form = EditarUsuarioForm()
    
    form.tipo_usuario.choices = [(tipo[0], tipo[1]) for tipo in tipo_usuario]

    cursor.execute('''SELECT * FROM Usuario WHERE Usuario.Id_usuario = %s''', (id,))
    user_edit = cursor.fetchone()
    if request.method == 'GET':
        form.nombre_user.data = user_edit[1]
        form.email_user.data = user_edit[2]
        form.tipo_usuario.data = user_edit[4]

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
        computador = request.form['computador']
        psw = request.form['psw'].strip()
        action = request.form['action']

        hashed_password = generate_password_hash(psw) if psw else None

        conn = get_db_connection()
        cursor = conn.cursor()
        if action == 'save':
            if psw:
                cursor.execute(
                    'UPDATE Usuario SET Nombre_user = %s, Email = %s, id_tipo_usuario = %s, Psw = %s WHERE Id_usuario = %s',
                    (nombre_usuario, email, tipo_usuario, hashed_password, id_usuario)
                )
            else:
                cursor.execute(
                    'UPDATE Usuario SET Nombre_user = %s, Email = %s, id_tipo_usuario = %s WHERE Id_usuario = %s',
                    (nombre_usuario, email, tipo_usuario, id_usuario)
                )

            if computador:
                cursor.execute('SELECT Id_pc, Nombre_pc FROM Pc')
                computadores = cursor.fetchall()

                pc_existe = False
                for compu in computadores:
                    if compu[0] == int(computador):
                        pc_existe = True
                        break

                if not pc_existe:
                    conn.close()
                    return redirect(url_for('usuarios.editar_usuario'))

                cursor.execute(
                    'UPDATE Usuario_Sistema_PC SET Id_pc = %s WHERE Id_usuario = %s',
                    (computador, id_usuario)
                )
                conn.commit()

            user = current_user
            fecha_actual_seg = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            descripcion_hist = f"actualizó la información de un usuario {nombre_usuario}."
            cursor.execute('INSERT INTO Historial (usuario_historial, descripcion, fecha, id_categoria) VALUES (%s, %s, %s, 1)', 
                         (user.nombre_usuario, descripcion_hist, fecha_actual_seg))

            flash("Información del usuario actualizada con éxito.", "success")

        elif action == 'delete':
            cursor.execute('DELETE FROM Usuario WHERE Id_usuario = %s', (id_usuario,))
            
            user = current_user
            fecha_actual_seg = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            descripcion_hist = f"eliminó a un usuario {nombre_usuario}."
            cursor.execute('INSERT INTO Historial (usuario_historial, descripcion, fecha, id_categoria) VALUES (%s, %s, %s, 1)', 
                         (user.nombre_usuario, descripcion_hist, fecha_actual_seg))
            
            flash("Usuario eliminado con éxito.", "warning")

        conn.commit()
        conn.close()

    except Exception as e:
        print(f"Error: {e}")
        flash("Ocurrió un error al procesar la solicitud.", "danger")

    return redirect(url_for('usuarios.usuarios'))


#BACKEND MI CUENTA
@usuarios_bp.route('/cuenta', methods=['GET', 'POST'])
@requiere_tipo_usuario(1, 2, 3)
@login_required
def cuenta():
    user = current_user
    num_notificaciones_totales = get_total_notifications(user.id)
    info_notificaciones = get_info_notifications(user.id)
    form = EditarMiCuenta()
    conn = get_db_connection()
    cursor = conn.cursor()

    if form.validate_on_submit():
        nuevo_email = form.email_user.data
        nueva_password = form.psw.data

        cursor.execute(
                'UPDATE Usuario SET email = %s WHERE id_usuario = %s',
                (nuevo_email, user.id)
            )
        user.email = nuevo_email
        if nueva_password:
            hashed_password = generate_password_hash(nueva_password)
            cursor.execute(
                'UPDATE Usuario SET psw = %s WHERE id_usuario = %s',
                (hashed_password, user.id)
            )
            user.password = nuevo_email
        conn.commit()
        flash('Tus datos se han actualizado correctamente', 'success')
        return redirect(url_for('usuarios.cuenta'))

    cursor.execute(
        'SELECT nombre_tipo_usuario FROM Tipo_usuario WHERE id_tipo_usuario = %s', 
        (user.id_tipo_usuario,)
    )
    tipo_usuario = cursor.fetchone()

    tipo_usuario = tipo_usuario[0] if tipo_usuario else 'Desconocido'
    try:
        cursor.execute(''' 
                        SELECT Id_pc 
                        FROM Usuario_Sistema_PC 
                        WHERE Id_usuario = %s 
                        GROUP BY Id_pc 
                        ORDER BY COUNT(*) DESC 
                        LIMIT 1 
                    ''', (user.id,))
        id_pc_mas_utilizado = cursor.fetchone()

        if id_pc_mas_utilizado:
            id_pc_mas_utilizado = id_pc_mas_utilizado[0]
            
            cursor.execute('SELECT Nombre_pc FROM Pc WHERE Id_pc = %s', (id_pc_mas_utilizado,))
            nombre = cursor.fetchone()

            if nombre:
                nombre = nombre[0]
            else:
                nombre = 'Computador no encontrado'
        else:
            nombre = 'Computador no asignado'
    except Exception as e:
        nombre = 'Computador no asignado'
        print(f"Error al obtener el nombre del PC: {e}")

    conn.close()
    data = {'user': user, 'tipo_usuario': tipo_usuario, 'nombre': nombre}
    return render_template('miCuenta.html', user=user,data=data, form=form, num_notificaciones_totales=num_notificaciones_totales,info_notificaciones=info_notificaciones)
