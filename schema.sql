DROP TABLE IF EXISTS usuario;
DROP TABLE IF EXISTS pc;
DROP TABLE IF EXISTS sistema;
DROP TABLE IF EXISTS usuario_sistema_pc;
DROP TABLE IF EXISTS reportes;
DROP TABLE IF EXISTS historial;
DROP TABLE IF EXISTS categoria_historial;
DROP TABLE IF EXISTS notificaciones;
DROP TABLE IF EXISTS tipo_usuario;

CREATE TABLE usuario (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_user VARCHAR(100),
    email VARCHAR(100),
    psw VARCHAR(100),
    id_tipo_usuario INTEGER,
    FOREIGN KEY (id_tipo_usuario) REFERENCES tipo_usuario(id_tipo_usuario)
);


CREATE TABLE tipo_usuario (
    id_tipo_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_tipo_usuario VARCHAR(100)
);


CREATE TABLE pc (
    id_pc INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_pc VARCHAR(30),
    procesador VARCHAR(50),
    placa VARCHAR(50),
    almacenamiento INTEGER,  -- en GB
    ram INTEGER,    -- en GB
    fuente VARCHAR(100)
);

CREATE TABLE sistema (
    id_sistema INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre_sistema VARCHAR(100)
);

CREATE TABLE reportes (
    id_reporte INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    num_solicitud VARCHAR(100) NOT NULL,
    asunto VARCHAR(100) NOT NULL,
    descripcion VARCHAR(300) NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_solucion TIMESTAMP,
    archivo VARCHAR,
    enviado BOOLEAN,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id_usuario)
);

CREATE TABLE usuario_sistema_pc (
    id_usuario INTEGER,
    id_sistema INTEGER,
    id_pc INTEGER,
    activo BOOLEAN,
    PRIMARY KEY (id_usuario, id_sistema, id_pc),
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario),
    FOREIGN KEY (id_sistema) REFERENCES sistema(id_sistema),
    FOREIGN KEY (id_pc) REFERENCES pc(id_pc)
);

CREATE TABLE historial (
    id_historial INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_historial VARCHAR(100),
    descripcion VARCHAR(100),
    fecha VARCHAR(100),
    id_categoria INTEGER,
    FOREIGN KEY (id_categoria) REFERENCES categoria_historial(id_categoria)
);

CREATE TABLE categoria_historial (
    id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_categoria VARCHAR(100)
);

CREATE TABLE notificaciones (
    id_notificacion INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER, 
    id_reporte INTEGER, 
    fecha_notificacion TIMESTAMP, 
    mensaje VARCHAR(200),
    leido BOOLEAN,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario),
    FOREIGN KEY (id_reporte) REFERENCES reportes(id_reporte)
);