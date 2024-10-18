from flask import Blueprint, render_template, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from forms import LoginForm
from model import Usuario

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if current_user.is_authenticated:
        return redirect(url_for('sistema.index'))

    if form.validate_on_submit():
        nombre_usuario = form.nombre_usuario.data
        password = form.contrasena.data
        user = Usuario.get_by_nombre_usuario(nombre_usuario)

        if user and check_password_hash(user.password, password):
            login_user(user)
            session['id_tipo_usuario'] = user.id_tipo_usuario
            flash('Inicio de sesión exitoso.', 'success')
            return redirect(url_for('sistema.index'))
        else:
            flash('Credenciales inválidas. Por favor, inténtalo de nuevo.', 'danger')

    return render_template('login.html', form=form)

@login_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente', 'warning')
    return redirect(url_for('login.login'))

@login_bp.errorhandler(401)
def unauthorized_error(error):
    flash("Por favor, inicia sesión para acceder a esta página.", "warning")
    return redirect(url_for('login.login'))
