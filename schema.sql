DROP TABLE IF EXISTS Usuario;
DROP TABLE IF EXISTS Pc;
DROP TABLE IF EXISTS Sistema;
DROP TABLE IF EXISTS Usuario_Sistema_PC;
DROP TABLE IF EXISTS Reportes;
DROP TABLE IF EXISTS Historial;


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
    fecha VARCHAR(100)
);