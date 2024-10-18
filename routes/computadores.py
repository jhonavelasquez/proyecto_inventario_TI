# routes/computadores.py
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
    form = CrearComputadorForm()
    search_query = request.args.get('search', '')

    query = "SELECT * FROM Pc Where 1 = 1"
    params = []
    if search_query:
        query += ' AND Pc.Nombre_pc LIKE ?'
        params.extend(['%' + search_query + '%'])

    filtro_pcs = conn.execute(query, params).fetchall()
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
    form = CrearComputadorForm()
    if form.validate_on_submit():
        nombre_computador = form.nombre_computador.data

        pcs = conn.execute("SELECT Nombre_pc FROM Pc").fetchall()
        for pc in pcs:
            if nombre_computador == pc['Nombre_pc']:
                flash("Ya existe un computador con el mismo nombre.", "warning")
                conn.close()
                return redirect(url_for('computadores.computadores'))

        procesador = form.procesador.data
        nombre_placa = form.nombre_placa.data
        almacenamiento = form.almacenamiento.data
        ram = form.ram.data
        fuente = form.fuente.data

        try:
            conn.execute('''
                INSERT INTO Pc (Nombre_pc, procesador, Placa, Almacenamiento, Ram, Fuente)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (nombre_computador, procesador, nombre_placa, almacenamiento, ram, fuente))

            user = current_user
            fecha_actual_seg = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            descripcion_hist = f"agregó un nuevo computador. {nombre_computador}."
            conn.execute('INSERT INTO Historial (usuario_historial, descripcion, fecha, id_categoria) VALUES (?, ?, ?, 3)', (user.nombre_usuario, descripcion_hist, fecha_actual_seg))
            
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
    
    form = EditarComputadorForm()
    pc = conn.execute('''
        SELECT *
        FROM Pc
        WHERE Pc.Id_pc = ?
    ''', (id_pc,)).fetchone()

    if pc is None:
        conn.close()
        abort(404)

    if request.method == 'GET':
        form.id_pc.data = pc['Id_pc']
        form.procesador.data = pc['Procesador']
        form.nombre_computador.data = pc['Nombre_pc']
        form.nombre_placa.data = pc['Placa']
        form.almacenamiento.data = pc['Almacenamiento']
        form.ram.data = pc['Ram']
        form.fuente.data = pc['Fuente']

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

        if action == 'save':
            conn.execute(
                'UPDATE Pc SET Nombre_pc = ?, Procesador = ?, Placa = ?, Almacenamiento = ?, Ram = ?, Fuente = ? WHERE Id_pc = ?',
                (nombre_pc, procesador, placa_pc, almacenamiento, ram, nombre_fuente, id_pc)
            )

            user = current_user
            fecha_actual_seg = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            descripcion_hist = f"actualizó la información de un computador. {nombre_pc}."
            conn.execute('INSERT INTO Historial (usuario_historial, descripcion, fecha, id_categoria) VALUES (?, ?, ?, 3)', (user.nombre_usuario, descripcion_hist, fecha_actual_seg))

            flash("Información del computador actualizada con éxito.", "success")
        elif action == 'delete':
            conn.execute(
                'DELETE FROM Pc WHERE Id_pc = ?',
                (id_pc,)
            )

            user = current_user
            fecha_actual_seg = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            descripcion_hist = f"eliminó un computador. {nombre_pc}."
            conn.execute('INSERT INTO Historial (usuario_historial, descripcion, fecha, id_categoria) VALUES (?, ?, ?, 3)', (user.nombre_usuario, descripcion_hist, fecha_actual_seg))
            flash("Computador eliminado con éxito.", "danger")

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
        flash("Ocurrió un error al procesar la solicitud.", "danger")
    finally:
        conn.close()

    return redirect(url_for('computadores.computadores'))