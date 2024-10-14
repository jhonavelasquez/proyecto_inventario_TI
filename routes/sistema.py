# routes/sistema.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash
from forms import CrearSistemaForm, EliminarSistemaForm, EditarSistemaForm
from model import get_db_connection
from utils.decorators import requiere_tipo_usuario, get_info_notifications, get_total_notifications
import datetime
import sqlite3


sistema_bp = Blueprint('sistema', __name__)

@sistema_bp.route('/', methods=['GET', 'POST'])
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

@sistema_bp.route('/crear_sistema', methods=['POST'])
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
                    return redirect(url_for('sistema.index'))

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

    return redirect(url_for('sistema.index'))

@sistema_bp.route('/eliminar_sistema', methods=['POST'])
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

    return redirect(url_for('sistema.index'))

@sistema_bp.route('/editar_sistema/<int:id_sistema>/<int:id_usuario>/<int:id_pc>', methods=['GET', 'POST'])
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
            user_pc = None

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
            return redirect(url_for('sistema.index'))

        user_pc = conn.execute('''SELECT Usuario.Id_usuario, Usuario.Nombre_user, Usuario_Sistema_PC.Id_pc, 
                                  Pc.Nombre_pc, Sistema.Nombre_sistema, Usuario_Sistema_PC.Activo, 
                                  Usuario_Sistema_PC.Id_sistema
                                  FROM Usuario
                                  INNER JOIN Usuario_Sistema_PC ON Usuario.Id_usuario = Usuario_Sistema_PC.Id_usuario
                                  INNER JOIN Pc ON Pc.Id_pc = Usuario_Sistema_PC.Id_pc
                                  INNER JOIN Sistema ON Usuario_Sistema_PC.Id_sistema = Sistema.Id_sistema
                                  WHERE Usuario_Sistema_PC.Id_sistema = ? AND Usuario_Sistema_PC.Id_usuario = ? AND Usuario_Sistema_PC.Id_pc = ?''',
                                 (id_sistema, id_usuario, id_pc)).fetchone()

        if user_pc:
            form.nuevo_Id_pc.default = user_pc['Id_pc']
            form.activo.default = user_pc['Activo']
            form.process()
        else:
            flash("No se encontró el registro del sistema para editar.", "warning")

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
