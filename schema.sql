DROP TABLE IF EXISTS Usuario;
DROP TABLE IF EXISTS Pc;
DROP TABLE IF EXISTS Sistema;
DROP TABLE IF EXISTS Usuario_Sistema_PC;
DROP TABLE IF EXISTS Reportes;
DROP TABLE IF EXISTS Historial;
DROP TABLE IF EXISTS Categoria_historial;
DROP TABLE IF EXISTS Notificaciones;

CREATE TABLE Usuario (
    Id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre_user VARCHAR(100),
    Email VARCHAR(100),
    Psw VARCHAR(100)
);

CREATE TABLE Pc (
    Id_pc INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre_pc VARCHAR(100),
    Placa VARCHAR(50),
    Almacenamiento INTEGER,  -- en GB
    Ram INTEGER,    -- en GB
    Fuente VARCHAR(100)
);

CREATE TABLE Sistema (
    Id_sistema INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre_sistema VARCHAR(100)
);

CREATE TABLE Reportes (
    id_reporte INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    asunto VARCHAR(100) NOT NULL,
    descripcion VARCHAR(300) NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_solucion TIMESTAMP,
    archivo VARCHAR,
    FOREIGN KEY (usuario_id) REFERENCES Usuario(Id_usuario)
);

CREATE TABLE Usuario_Sistema_PC (
    Id_usuario INTEGER,
    Id_sistema INTEGER,
    Id_pc INTEGER,
    Activo BOOLEAN,
    PRIMARY KEY (Id_usuario, Id_sistema, Id_pc),
    FOREIGN KEY (Id_usuario) REFERENCES Usuario(Id_usuario),
    FOREIGN KEY (Id_sistema) REFERENCES Sistema(Id_sistema),
    FOREIGN KEY (Id_pc) REFERENCES Pc(Id_pc)
);

CREATE TABLE Historial (
    Id_historial INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_historial VARCHAR(100),
    descripcion VARCHAR(100),
    fecha VARCHAR(100),
    id_categoria INTEGER,
    FOREIGN KEY (id_categoria) REFERENCES Categoria_Historial(id_categoria)
);

CREATE TABLE Categoria_historial (
    id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_categoria VARCHAR(100)
);

CREATE TABLE Notificaciones (
    id_notificacion INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER, 
    id_reporte INTEGER, 
    fecha_notificacion TIMESTAMP, 
    mensaje VARCHAR(200),
    leido BOOLEAN,
    FOREIGN KEY (id_usuario) REFERENCES Usuario(Id_usuario),
    FOREIGN KEY (id_reporte) REFERENCES Reportes(id_reporte)
);