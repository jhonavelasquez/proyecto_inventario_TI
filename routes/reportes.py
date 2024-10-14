from flask import Blueprint, render_template, redirect, request, flash, send_from_directory, url_for
from flask_login import login_required, current_user
import datetime
import os
from werkzeug.utils import secure_filename
from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
from forms import ReporteForm 
from utils.decorators import get_db_connection, get_total_notifications, get_info_notifications 

reportes_bp = Blueprint('reportes', __name__)

@reportes_bp.route('/reportes', methods=['GET', 'POST'])
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
        return redirect(url_for('reportes.reportes'))  # Redirigir en caso de error

    finally:
        conn.close()


@reportes_bp.route('/ver_reporte/<int:id_reporte>', methods=['GET'])
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

    user = current_user
    num_notificaciones_totales = get_total_notifications(user.id)
    info_notificaciones = get_info_notifications(user.id)

    return render_template('ver_reporte.html', reporte=reporte, user=user, num_notificaciones_totales=num_notificaciones_totales, info_notificaciones=info_notificaciones)


@reportes_bp.route('/reporte_2', methods=['GET', 'POST'])
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
            return redirect(url_for('reportes.reportes'))

    else:
        print("Errores de validación:", form.errors)

    return render_template('reporte_2.html', form=form, user=user, num_notificaciones_totales=num_notificaciones_totales, info_notificaciones=info_notificaciones)


@reportes_bp.route('/ver_reporte/<filename>', methods=['GET'])
@login_required
def uploaded_file(filename):
    return send_from_directory('pdf_reportes', filename)
