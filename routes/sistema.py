# routes/sistema.py
from flask import abort, Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash
from forms import CrearSistemaForm, EliminarSistemaForm, EditarSistemaForm
from model import get_db_connection
from utils.decorators import requiere_tipo_usuario, get_info_notifications, get_total_notifications
import datetime
import mysql.connector
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

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Sistema")
    sistemas = cursor.fetchall()
    formEliminar.sistema.choices = [(sistema[0], sistema[1]) for sistema in sistemas]

    cursor.execute("SELECT * FROM Pc")
    pcs = cursor.fetchall()

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
        query += ' AND Sistema.Id_sistema = %s'
        params.append(sistema_id)
    if search_query:
        query += ' AND (Usuario.Nombre_user LIKE %s OR Pc.Nombre_pc LIKE %s)'
        params.extend(['%' + search_query + '%', '%' + search_query + '%'])

    cursor.execute(query, params)
    user_pc_data = cursor.fetchall()
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
        print("El formulario ha sido enviado.")
        if formCrear.validate_on_submit():
            nombre_sistema = formCrear.nombre_sistema.data

            cursor = conn.cursor()
            cursor.execute("SELECT Nombre_sistema FROM Sistema")
            sistemas = cursor.fetchall()
            for sistema in sistemas:
                if nombre_sistema == sistema[0]:
                    flash("El sistema ya existe y no será añadido de nuevo.", "warning")
                    conn.close()
                    return redirect(url_for('sistema.index'))

            cursor.execute('INSERT INTO Sistema (Nombre_sistema) VALUES (%s)', (nombre_sistema,))
            conn.commit()

            cursor.execute(
                'SELECT Id_sistema FROM Sistema WHERE Nombre_sistema = %s', (nombre_sistema,)
            )
            result = cursor.fetchone()
            if result:
                id_sistema = result[0]
            else:
                flash("Error al obtener el ID del sistema.", "danger")
                return redirect(url_for('sistema.index'))

            cursor.execute("SELECT Id_usuario FROM Usuario")
            usuarios = cursor.fetchall()
            for usuario in usuarios:
                cursor.execute('''
                    SELECT Id_pc
                    FROM Usuario_Sistema_PC
                    WHERE Id_usuario = %s
                    GROUP BY Id_pc
                    ORDER BY COUNT(*) DESC
                    LIMIT 1
                ''', (usuario[0],))
                id_pc_mas_utilizado = cursor.fetchone()

                if id_pc_mas_utilizado:
                    cursor.execute(
                        "INSERT INTO Usuario_Sistema_PC (Id_usuario, Id_sistema, Id_pc, Activo) VALUES (%s, %s, %s, FALSE)",
                        (usuario[0], id_sistema, id_pc_mas_utilizado[0])
                    )
                else:
                    flash(f"No se pudo encontrar un PC asignado para el usuario con ID {usuario[0]}.", "warning")

            user = current_user
            fecha_actual_seg = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            fecha_actual = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
            descripcion_hist = (f" agregó un nuevo sistema.  {nombre_sistema}.")
            cursor.execute('INSERT INTO Historial (usuario_historial, descripcion, fecha, id_categoria) VALUES (%s,%s,%s, 2)', (user.nombre_usuario, descripcion_hist, fecha_actual_seg))

            conn.commit()
            conn.close()

            flash("Sistema creado exitosamente.", "success")
        else:
            print("Error de validación del formulario")
            flash("Por favor, corrige los errores en el formulario.", "danger")
    except mysql.connector.Error as db_error:
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

    cursor= conn.cursor()
    cursor.execute("SELECT Id_sistema, Nombre_sistema FROM Sistema")
    sistemas = cursor.fetchall()
    formEliminar.sistema.choices = [(sistema[0], sistema[1]) for sistema in sistemas]

    if formEliminar.validate_on_submit():
        sistema_id = formEliminar.sistema.data

        try:
            cursor.execute('SELECT Nombre_sistema FROM Sistema WHERE Id_sistema = %s', (sistema_id,))
            sistema = cursor.fetchone()
            if sistema:
                nombre_sistema = sistema[0]


                cursor.execute('DELETE FROM Sistema WHERE Id_sistema = %s', (sistema_id,))

                user = current_user
                fecha_actual_seg = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                fecha_actual = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
                descripcion_hist = (f" eliminó el sistema {nombre_sistema}.")

                cursor.execute('INSERT INTO Historial (usuario_historial, descripcion, fecha, id_categoria) VALUES (%s, %s, %s, 2)', (user.nombre_usuario, descripcion_hist, fecha_actual_seg))

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
    
    if not id_sistema:
        conn.close()
        abort(404)

    if not id_usuario:
        conn.close()
        abort(404)

    if not id_pc:
        conn.close()
        abort(404)
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Pc")
    pcs = cursor.fetchall()
    form.nuevo_Id_pc.choices = [(pc[0], pc[1]) for pc in pcs]
    
    try:
        if request.method == 'POST' and form.validate_on_submit():
            nuevo_id_pc = form.nuevo_Id_pc.data
            activo = form.activo.data
            user_pc = None

            cursor.execute('''UPDATE Usuario_Sistema_PC 
                            SET Activo = %s, Id_pc = %s
                            WHERE Id_usuario = %s AND Id_sistema = %s AND Id_pc = %s''',
                         (activo, nuevo_id_pc, id_usuario, id_sistema, id_pc))

            cursor.execute(
                'SELECT Nombre_user FROM Usuario WHERE Id_usuario = %s', (id_usuario,))
            nombre_user = cursor.fetchone()

            
            cursor.execute(
                'SELECT Nombre_sistema FROM Sistema WHERE Id_sistema = %s', (id_sistema,))
            nombre_sis = cursor.fetchone() 

            
            nombre_usuario = nombre_user[0]
            nombre_sistema = nombre_sis[0]

            user = current_user
            fecha_actual_seg = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            fecha_actual = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
            descripcion_hist = (f"Actualizó {nombre_sistema} de {nombre_usuario}. ")

            cursor.execute('INSERT INTO Historial (usuario_historial, descripcion, fecha, id_categoria) VALUES (%s,%s,%s, 2)', 
                         (user.nombre_usuario, descripcion_hist, fecha_actual_seg))

            conn.commit()

            flash("¡El PC o el estado del sistema han sido actualizados!", "success")
            return redirect(url_for('sistema.index'))

        cursor.execute('''SELECT Usuario.Id_usuario, Usuario.Nombre_user, Usuario_Sistema_PC.Id_pc, 
                                  Pc.Nombre_pc, Sistema.Nombre_sistema, Usuario_Sistema_PC.Activo, 
                                  Usuario_Sistema_PC.Id_sistema
                                  FROM Usuario
                                  INNER JOIN Usuario_Sistema_PC ON Usuario.Id_usuario = Usuario_Sistema_PC.Id_usuario
                                  INNER JOIN Pc ON Pc.Id_pc = Usuario_Sistema_PC.Id_pc
                                  INNER JOIN Sistema ON Usuario_Sistema_PC.Id_sistema = Sistema.Id_sistema
                                  WHERE Usuario_Sistema_PC.Id_sistema = %s AND Usuario_Sistema_PC.Id_usuario = %s AND Usuario_Sistema_PC.Id_pc = %s''',
                                 (id_sistema, id_usuario, id_pc))
        user_pc = cursor.fetchone()

        if user_pc:
            form.nuevo_Id_pc.default = user_pc[2]
            form.activo.default = user_pc[5]
            form.process()
        else:
            conn.close()
            abort(404)

    except Exception as e:
        print(f"Error: {str(e)}", "danger")
        flash("Ocurrió un error al procesar la solicitud.", "danger")

    finally:
        conn.close()

    user = current_user
    num_notificaciones_totales = get_total_notifications(user.id)
    info_notificaciones = get_info_notifications(user.id)

    return render_template('editar_sistema.html', form=form, user_pc=user_pc, user=user, 
                           num_notificaciones_totales=num_notificaciones_totales, 
                           info_notificaciones=info_notificaciones)
