from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from model import get_db_connection
from utils.decorators import get_total_notifications, get_info_notifications

historial_bp = Blueprint('historial', __name__)

@historial_bp.route('/historial', methods=['GET'])
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
        return redirect(url_for('historial.historial'))  # Redirigir en caso de error

    finally:
        conn.close()
