import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

hashed_password = generate_password_hash("admin#.123")
# Insertar el valor usando parámetros
cur.execute("INSERT INTO `usuario` (`id_usuario`, `nombre_user`, `email`, `psw`, `id_tipo_usuario`) VALUES (?, ?, ?, ?, ?)", 
            (1, 'ADMIN', 'JONATHAN.VR484@GMAIL.COM', hashed_password, 1))

cur.execute('''INSERT INTO `tipo_usuario` (`id_tipo_usuario`, `nombre_tipo_usuario`) VALUES
(1, 'Administrador'),
(2, 'Lector'),
(3, 'Editor');''')

cur.execute('''INSERT INTO pc (id_pc, nombre_pc, procesador, placa, almacenamiento, ram, fuente) VALUES
(1, 'SA2101051', 'INTEL I7', 'ASUS ROG STRIX', 512, 16, 'Corsair 650W');''')

#CATEGORIA DE HISTORIAL
cur.execute('''INSERT INTO categoria_historial (id_categoria, nombre_categoria) VALUES
(1, 'Usuarios'),
(2, 'Sistemas'),
(3, 'Computadores'),
(4, 'Reportes');''')

#SISTEMAS
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA DE ADQUISICIONES MUNICIPALES (AB)');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA DE GESTIÓN DOCUMENTAL (SGD)');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA DE VECINO DIGITAL (ONLINE) (PPO)');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA CONTABILIDAD GUBERNAMENTAL (FIN)');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA DECRETO DE PAGO WEB (DPW)');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA CONTROL PRESUPUESTARIO (FIN-SECPLA)');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA PRESUPUESTARIO (FIN-SECPLA)');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA DE VENTANILLA ÚNICA MUNICIPAL (VUM)');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA RELOJ CONTROL (RRHH)');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA CONTROL DE ASISTENCIA GENERA (RRHH)');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA DE BODEGAS (AB)');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA DE ACTIVO FIJO (AB)');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA JUZGADO DE POLICÍA LOCAL (JPL)');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA DE INSPECCIÓN (INS)');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA DE DERECHOS DE ASEO (RENT)');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA LICENCIAS DE CONDUCIR (TRANS)');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA DE PERMISOS DE CIRCULACIÓN (TRANS)');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA DE PATENTES COMERCIALES (RENT)');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA ÓRDENES DE INGRESO (FIN)');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA DE TESORERÍA MUNICIPAL (FIN)');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA CONCILIACIÓN BANCARIA (FIN)');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA CONVENIOS DE PAGO (FIN)');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA ASISTENCIA SOCIAL (DIDECO)');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA REMUNERACIONES MUNICIPALES (RRHH)');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA REMUNERACIONES SALUD (RRHH)');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA REMUNERACIONES EDUCACIÓN (RRHH)');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA REMUNERACIONES JUNJI (RRHH)');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA DE HONORARIOS (RRHH)');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA PERSONAL MUNICIPAL (RRHH)');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA PERSONAL EDUCACION (RRHH)');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA PERSONAL SALUD (RRHH)');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA PERSONAL JUNJI (RRHH)');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA GESTIÓN MUNICIPAL (GEST)');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA DE DECLARACIÓN DE RENTAS (FIN)');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA DE VENTANILLA ÚNICA (ADM)');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA DE EXÁMENES TEÓRICOS LEY 19.280 (TRANS)');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA DE MONITO WEB (TRANS-JUZ-INSP)');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA DE ENVIÓ DE SOLICITUDES (FIN-ADM-DOM-DIMAO)');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA DE FOTOGRAFÍA (TRANS)');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA INTRANET DE RECURSOS HUMANOS (RRHH)');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA ORGANIZACIONES COMUNITARIAS (DIDECO)');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA DE BIENESTAR (RRHH)');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA DE INTRANET DE RRHH (RRHH)');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SMARTDOM (DOM)');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('PLATAFORMA MULTISERVICIO');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('CITYMIS');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA V-FORM BECAS MUNICIPALES');")
cur.execute("INSERT INTO sistema (nombre_sistema) VALUES ('SISTEMA DE INFORMACIÓN TERRITORIAL DE SAN ANTONIO SITSA');")
connection.commit()
connection.close()