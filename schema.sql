DROP TABLE IF EXISTS Usuario;
DROP TABLE IF EXISTS Pc;
DROP TABLE IF EXISTS Sistema;
DROP TABLE IF EXISTS Usuario_PC;
DROP TABLE IF EXISTS Usuario_Sistema;

CREATE TABLE Usuario (
    Id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre_user VARCHAR(100),
    Email VARCHAR(100)
);

CREATE TABLE Pc (
    Id_pc INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre_pc VARCHAR(100),
    Placa VARCHAR(50),
    Disco INTEGER,  -- en GB
    Ram INTEGER,    -- en GB
    Fuente VARCHAR(100)
);

CREATE TABLE Sistema (
    Id_sistema INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre_sistema VARCHAR(100)
);

CREATE TABLE Usuario_PC (
    Id_usuario INTEGER,
    Id_pc INTEGER,
    PRIMARY KEY (Id_usuario, Id_pc),
    FOREIGN KEY (Id_usuario) REFERENCES Usuario(Id_usuario),
    FOREIGN KEY (Id_pc) REFERENCES Pc(Id_pc)
);

CREATE TABLE Usuario_Sistema (
    Id_usuario INTEGER,
    Id_sistema INTEGER,
    Activo BOOLEAN,
    PRIMARY KEY (Id_usuario, Id_sistema),
    FOREIGN KEY (Id_usuario) REFERENCES Usuario(Id_usuario),
    FOREIGN KEY (Id_sistema) REFERENCES Sistema(Id_sistema)
);
