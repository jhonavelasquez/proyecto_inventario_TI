from flask_wtf import FlaskForm
from wtforms import FileField, BooleanField, DateField, TextAreaField, StringField, PasswordField, SubmitField, SelectField, IntegerField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo
from flask_wtf.file import FileAllowed
from flask import current_app
from utils.decorators import obtener_opciones_computador

class LoginForm(FlaskForm):
    nombre_usuario = StringField('Nombre Usuario', validators=[DataRequired()])
    contrasena = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')

class CrearSistemaForm(FlaskForm):
    nombre_sistema = StringField('Nombre del Sistema', validators=[DataRequired()])

class EditarSistemaForm(FlaskForm):
    nuevo_id_pc = SelectField('Seleccionar Computador', coerce=int, validators=[DataRequired()])
    activo = BooleanField('Activar Sistema')
    submit = SubmitField('Guardar cambios')

class EliminarSistemaForm(FlaskForm):
    sistema = SelectField('Seleccionar Sistema', coerce=int, validators=[DataRequired()])

class CrearUsuarioForm(FlaskForm):
    nombre_user = StringField('Nombre de usuario', validators=[DataRequired()])
    email_user = StringField('Correo electrónico', validators=[DataRequired(), Email()])
    psw = PasswordField('Contraseña', validators=[DataRequired()])
    psw_confirmar = PasswordField('Confirmar contraseña', validators=[DataRequired(), EqualTo('psw', message='Las contraseñas deben coincidir')])
    computador = SelectField('Computador', coerce=int, validators=[DataRequired()])
    tipo_usuario = SelectField('Tipo de usuario', coerce=int, validators=[DataRequired()])

class EditarUsuarioForm(FlaskForm):
    nombre_user = StringField('Nombre de usuario', validators=[DataRequired()])
    email_user = StringField('Correo electrónico', validators=[DataRequired(), Email()])
    computador = SelectField('Computador', choices=[])
    psw = StringField('Contraseña')
    tipo_usuario = SelectField('Tipo de usuario', coerce=int, validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(EditarUsuarioForm, self).__init__(*args, **kwargs)
        with current_app.app_context():
            self.computador.choices = [("", "--- No asignar ---")] + obtener_opciones_computador()

class CrearComputadorForm(FlaskForm):
    nombre_computador = StringField('Nombre del Computador', validators=[DataRequired()])
    procesador = StringField('Procesador', validators=[DataRequired()])
    nombre_placa = StringField('Nombre de Placa Base', validators=[DataRequired()])
    almacenamiento = IntegerField('Total Almacenamiento (GB)', validators=[DataRequired()])
    ram = IntegerField('Total de Ram (GB)', validators=[DataRequired()])
    fuente = StringField('Fuente de Poder', validators=[DataRequired()])
    submit = SubmitField('Guardar')

class EditarComputadorForm(FlaskForm):
    id_pc = HiddenField('ID PC')
    nombre_computador = StringField('Nombre', validators=[DataRequired()])
    procesador = StringField('Procesador', validators=[DataRequired()])
    nombre_placa = StringField('Nombre de Placa Base', validators=[DataRequired()])
    almacenamiento = IntegerField('Almacenamiento Total (GB)', validators=[DataRequired()])
    ram = IntegerField('Ram Total (GB)', validators=[DataRequired()])
    fuente = StringField('Fuente de Poder', validators=[DataRequired()])
    action = HiddenField('Action')
    submit_guardar = SubmitField('Guardar cambios')
    submit_eliminar = SubmitField('Eliminar')

class ReporteForm(FlaskForm):
    num_solicitud = StringField('N° Solicitud', validators=[DataRequired()])
    version = StringField('Versión', validators=[DataRequired()])
    nombre_sistema = StringField('Nombre del Sistema', validators=[DataRequired()])
    responsable_sistema = StringField('Responsable del sistema', validators=[DataRequired()])
    direccion_unidad = StringField('Dirección/Unidad', validators=[DataRequired()])
    nombre_solicitante = StringField('Nombre Solicitante', validators=[DataRequired()])
    fecha_solucion = DateField('Fecha de Solución', validators=[DataRequired()])
    responsable_ddi = StringField('Responsable DDI', validators=[DataRequired()])
    responsable_solicitud = StringField('Responsable Solicitud', validators=[DataRequired()])
    descripcion = TextAreaField('Descripción', validators=[DataRequired()])
    file = FileField('Descripción', validators=[
        FileAllowed(['jpg', 'png'], 'Solo se permiten imágenes JPG y PNG')
    ])
    submit = SubmitField('Generar PDF')

class EditarMiCuenta(FlaskForm):
    email_user = StringField('Email', validators=[DataRequired(), Email()])
    psw = PasswordField('Contraseña')
    psw_confirmar = PasswordField('Confirmar contraseña', validators=[EqualTo('psw', message='Las contraseñas deben coincidir')])
    submit = SubmitField('Actualizar')
