import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 's3cr3t_k3y_12345'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/', methods=['GET'])
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

    return render_template('index.html', user_pc_data=user_pc_data, sistemas=sistemas, pcs=pcs)


    return render_template('_tabla.html', user_pc_data=user_pc_data)


@app.route('/crear_sistema', methods=['POST'])
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

@app.route('/computadores', methods=['GET'])
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


@app.route('/usuarios', methods=['GET'])
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
def crear_usuario():
    if request.method == 'POST':
        nombre_user = request.form['nombre_user']
        email_user = request.form['email_user']
        id_pc = request.form.get('computador')

        conn = get_db_connection()
        conn.execute('INSERT INTO Usuario (Nombre_user, Email) VALUES (?, ?)', (nombre_user, email_user))

        id_usuario = conn.execute(
            'SELECT Id_usuario FROM Usuario WHERE Nombre_user = ? AND Email = ?', (nombre_user, email_user)).fetchone()['Id_usuario']



        sistemas = conn.execute("SELECT Id_sistema FROM Sistema").fetchall()

        for sistema in sistemas:
            conn.execute(
                "INSERT INTO Usuario_Sistema_PC (Id_usuario, Id_sistema, Id_pc, Activo) VALUES (?, ?, ?,FALSE)",
                (id_usuario, sistema['Id_sistema'],id_pc)
            )

        conn.commit()
        conn.close()
        
        flash("Usuario creado exitosamente.", "success")
        return redirect(url_for('usuarios'))

    return render_template('usuarios.html')

@app.route('/editar_usuario/<int:id>', methods=['GET'])
def editar_usuario(id):
    conn = get_db_connection()
    
    # Obtener los detalles del usuario para el ID proporcionado
    use = conn.execute('''
        SELECT *
        FROM Usuario
        WHERE Usuario.Id_usuario = ?
    ''', (id,)).fetchone()
    conn.close()
    
    return render_template('editar_usuario.html', use=use)

@app.route('/editar_usuario_form', methods=['POST'])
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
        flash("Usuario eliminado con éxito.", "danger")

    conn.commit()
    conn.close()

    return redirect(url_for('usuarios'))
