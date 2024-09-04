import sqlite3
from flask import Flask, render_template, request, redirect,url_for

app = Flask(__name__)

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

    # Consulta base
    query = '''
    SELECT Usuario.Id_usuario, Usuario.Nombre_user, Usuario.Email, Pc.Id_pc, 
        Pc.Nombre_pc, Usuario_Sistema.Id_sistema, Sistema.Nombre_sistema, Usuario_Sistema.Activo
    FROM Usuario
    INNER JOIN Usuario_PC ON Usuario.Id_usuario = Usuario_PC.Id_usuario
    INNER JOIN Pc ON Pc.Id_pc = Usuario_PC.Id_pc
    INNER JOIN Usuario_Sistema ON Usuario_Sistema.Id_usuario = Usuario.Id_usuario
    INNER JOIN Sistema ON Sistema.Id_sistema = Usuario_Sistema.Id_sistema
    WHERE 1=1
    '''

    # Agregar filtros
    params = []
    if sistema_id:
        query += ' AND Sistema.Id_sistema = ?'
        params.append(sistema_id)
    if search_query:
        query += ' AND (Usuario.Nombre_user LIKE ? OR Pc.Nombre_pc LIKE ?)'
        params.extend(['%' + search_query + '%', '%' + search_query + '%'])

    # Ejecutar la consulta con los parámetros
    user_pc_data = conn.execute(query, params).fetchall()
    conn.close()

    return render_template('index.html', user_pc_data=user_pc_data, sistemas=sistemas, pcs = pcs)

@app.route('/crear_sistema', methods=['POST'])
def crear_sistema():
    nombre_sistema = request.form['nombre_sistema']
    
    conn = get_db_connection()
    
    conn.execute('INSERT INTO Sistema (Nombre_sistema) VALUES (?)', (nombre_sistema,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

@app.route('/eliminar_sistema', methods=['POST'])
def eliminar_sistema():
    sistema_id = request.form.get('sistema')
    
    if sistema_id:
        conn = get_db_connection()
        
        # Eliminar el sistema con el ID proporcionado
        conn.execute('DELETE FROM Sistema WHERE Id_sistema = ?', (sistema_id,))
        conn.commit()
        conn.close()
    
    return redirect(url_for('index'))

@app.route('/editar_registro', methods=['POST'])
def editar_registro():
    id_usuario = request.form['Id_usuario']
    id_sistema = request.form['editar_Sistema']
    activo = request.form['Activo']
    nuevo_id_pc = request.form['nuevo_Id_pc']  
    print("----------")
    print(id_usuario)
    print(id_sistema)
    print("----------")
    conn = get_db_connection()

    conn.execute(
        'UPDATE Usuario_Sistema SET Activo = ? WHERE Id_usuario = ? AND Id_sistema = ?',
        (activo, id_usuario, id_sistema)
    )

    conn.execute(
        'DELETE FROM Usuario_PC WHERE Id_usuario = ?',
        (id_usuario,)
    )

    conn.execute(
        'INSERT INTO Usuario_PC (Id_usuario, Id_pc) VALUES (?, ?)',
        (id_usuario, nuevo_id_pc)
    )

    conn.commit()
    conn.close()

    return redirect(url_for('index'))

# Funciones de Computadores
@app.route('/computadores', methods=['GET'])
def computadores():
    conn = get_db_connection()

    search_query = request.args.get('search', '')

    query = "SELECT * FROM Pc Where 1 = 1"

    params = []
    if search_query:
        query += ' AND Pc.Nombre_pc LIKE ?'
        params.extend(['%' + search_query + '%'])

    
    pcs = conn.execute(query, params).fetchall()
    conn.close()

    return render_template('computadores.html', pcs=pcs)


# funciones de Usuario
@app.route('/usuarios', methods=['GET'])
def usuarios():
    conn = get_db_connection()

    search_query = request.args.get('search', '')

    query = '''SELECT Usuario.Id_usuario, Usuario.Nombre_user, Usuario.Email FROM Usuario Where 1 = 1 
    '''
    pcs = conn.execute("SELECT * FROM Pc").fetchall()

    params = []
    if search_query:
        query += ' AND Usuario.Nombre_user LIKE ?'
        params.extend(['%' + search_query + '%'])

    
    users = conn.execute(query, params).fetchall()
    conn.close()

    return render_template('usuarios.html', users=users, pcs = pcs)

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

        conn.execute('INSERT INTO Usuario_PC (Id_usuario, Id_pc) VALUES (?, ?)', (id_usuario, id_pc))

        sistemas = conn.execute("SELECT Id_sistema FROM Sistema").fetchall()

        for sistema in sistemas:
            conn.execute(
                "INSERT INTO Usuario_Sistema (Id_usuario, Id_sistema, Activo) VALUES (?, ?, FALSE)",
                (id_usuario, sistema['Id_sistema'])
            )

        conn.commit()
        conn.close()

        return redirect(url_for('usuarios'))


    return render_template('usuarios.html')

