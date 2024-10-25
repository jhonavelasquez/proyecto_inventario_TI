from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from forms import CrearComputadorForm, EditarComputadorForm
from model import get_db_connection
from utils.decorators import requiere_tipo_usuario, get_info_notifications, get_total_notifications
import datetime

computadores_bp = Blueprint('computadores', __name__)

@computadores_bp.route('/computadores', methods=['GET'])
@login_required
def computadores():
    conn = get_db_connection()
    cursor = conn.cursor()
    form = CrearComputadorForm()
    search_query = request.args.get('search', '')

    query = "SELECT * FROM pc WHERE 1 = 1"
    params = []
    if search_query:
        query += ' AND pc.nombre_pc LIKE %s'
        params.extend(['%' + search_query + '%'])

    cursor.execute(query, params)
    filtro_pcs = cursor.fetchall()
    conn.commit()
    conn.close()

    user = current_user
    num_notificaciones_totales = get_total_notifications(user.id)
    info_notificaciones = get_info_notifications(user.id)

    return render_template('computadores.html', form=form, filtro_pcs=filtro_pcs, user=user, num_notificaciones_totales=num_notificaciones_totales, info_notificaciones=info_notificaciones)


@computadores_bp.route('/crear_computador', methods=['POST'])
@requiere_tipo_usuario(1, 3)
@login_required
def crear_computador():
    conn = get_db_connection()
    cursor = conn.cursor()
    form = CrearComputadorForm()
    if form.validate_on_submit():
        nombre_computador = form.nombre_computador.data

        cursor.execute("SELECT nombre_pc FROM pc")
        pcs = cursor.fetchall()

        for pc in pcs:
            if nombre_computador == pc[0]:
                flash("Ya existe un computador con el mismo nombre.", "warning")
                conn.close()
                return redirect(url_for('computadores.computadores'))

        procesador = form.procesador.data
        nombre_placa = form.nombre_placa.data
        almacenamiento = form.almacenamiento.data
        ram = form.ram.data
        fuente = form.fuente.data

        try:
            cursor.execute('''INSERT INTO pc (nombre_pc, procesador, placa, almacenamiento, ram, fuente)
                              VALUES (%s, %s, %s, %s, %s, %s)''',
                           (nombre_computador, procesador, nombre_placa, almacenamiento, ram, fuente))

            user = current_user
            today = datetime.datetime.now()

            today_str = today.strftime('%Y-%m-%d %H:%M:%S')
            descripcion_hist = f"agregó un nuevo computador. {nombre_computador}."
            cursor.execute('INSERT INTO historial (usuario_historial, descripcion, fecha, id_categoria) VALUES (%s, %s, %s, 3)', 
                           (user.nombre_usuario, descripcion_hist, today_str))
            
            conn.commit()
            conn.close()

            flash("Computador agregado exitosamente.", "success")
            return redirect(url_for('computadores.computadores'))
        
        except Exception as e:
            print(f"Error: {e}")
            flash("Ocurrió un error al procesar la solicitud.", "danger")
        finally:
            conn.close()

    return render_template('computadores.html')


@computadores_bp.route('/editar_computador/<int:id_pc>', methods=['GET'])
@requiere_tipo_usuario(1, 3)
@login_required
def editar_computador(id_pc):
    conn = get_db_connection()
    cursor = conn.cursor()
    form = EditarComputadorForm()
    cursor.execute('''SELECT * FROM pc WHERE pc.id_pc = %s''', (id_pc,))
    pc = cursor.fetchone()

    if pc is None:
        conn.commit()
        conn.close()
        abort(404)

    if request.method == 'GET':
        form.id_pc.data = pc[0]
        form.procesador.data = pc[2]
        form.nombre_computador.data = pc[1]
        form.nombre_placa.data = pc[3]
        form.almacenamiento.data = pc[4]
        form.ram.data = pc[5]
        form.fuente.data = pc[6]

    conn.close()

    user = current_user
    num_notificaciones_totales = get_total_notifications(user.id)
    info_notificaciones = get_info_notifications(user.id)

    return render_template('editar_computador.html', pc=pc, form=form, user=user, num_notificaciones_totales=num_notificaciones_totales, info_notificaciones=info_notificaciones)


@computadores_bp.route('/editar_computador_form', methods=['POST'])
@requiere_tipo_usuario(1, 3)
@login_required
def editar_computador_form():
    try:
        id_pc = request.form['id_pc']
        nombre_pc = request.form['nombre_computador']
        procesador = request.form['procesador']
        placa_pc = request.form['nombre_placa']
        almacenamiento = request.form.get('almacenamiento')
        ram = request.form.get('ram')
        nombre_fuente = request.form['fuente']
        action = request.form['action']

        conn = get_db_connection()
        cursor = conn.cursor()

        if action == 'save':
            cursor.execute(
                'UPDATE pc SET nombre_pc = %s, procesador = %s, placa = %s, almacenamiento = %s, ram = %s, fuente = %s WHERE id_pc = %s',
                (nombre_pc, procesador, placa_pc, almacenamiento, ram, nombre_fuente, id_pc)
            )

            user = current_user
            today = datetime.datetime.now()

            today_str = today.strftime('%Y-%m-%d %H:%M:%S')
            descripcion_hist = f"actualizó la información de un computador. {nombre_pc}."
            cursor.execute('INSERT INTO historial (usuario_historial, descripcion, fecha, id_categoria) VALUES (%s, %s, %s, 3)', 
                           (user.nombre_usuario, descripcion_hist, today_str))

            flash("Información del computador actualizada con éxito.", "success")
        elif action == 'delete':
            cursor.execute(
                'DELETE FROM pc WHERE id_pc = %s',
                (id_pc,)
            )

            user = current_user
            today = datetime.datetime.now()

            today_str = today.strftime('%Y-%m-%d %H:%M:%S')
            descripcion_hist = f"eliminó un computador. {nombre_pc}."
            cursor.execute('INSERT INTO historial (usuario_historial, descripcion, fecha, id_categoria) VALUES (%s, %s, %s, 3)', 
                           (user.nombre_usuario, descripcion_hist, today_str))
            flash("Computador eliminado con éxito.", "danger")

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
        flash("Ocurrió un error al procesar la solicitud.", "danger")
    finally:
        conn.close()

    return redirect(url_for('computadores.computadores'))
