PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;

CREATE TABLE Usuario (
    Id_usuario INT PRIMARY KEY AUTO_INCREMENT,
    Nombre_user VARCHAR(100),
    Email VARCHAR(100),
    Psw VARCHAR(100)
);
INSERT INTO Usuario VALUES(1,'JUPEREZ','juan.perez@sanantonio.cl','1234');
INSERT INTO Usuario VALUES(2,'JOVELASQUEZ','jvelasquez@sanantonio.cl','1234');
INSERT INTO Usuario VALUES(3,'pepe','jvelasquez@sanantonio.cl','1234');
INSERT INTO Usuario VALUES(4,'felipe','jvelasquez@sanantonio.cl','1234');
INSERT INTO Usuario VALUES(5,'alex','jvelasquez@sanantonio.cl','1234');

CREATE TABLE Pc (
    Id_pc INT PRIMARY KEY AUTO_INCREMENT,
    Nombre_pc VARCHAR(100),
    Placa VARCHAR(50),
    Disco INT,  -- en GB
    Ram INT,    -- en GB
    Fuente VARCHAR(100)
);

INSERT INTO Pc VALUES(1,'SA2101051','ASUS ROG STRIX',512,16,'Corsair 650W');
INSERT INTO Pc VALUES(2,'SA2000000','HP Network',512,8,'Corsair 550W');
INSERT INTO Pc VALUES(3,'SA0999999','HP',512,8,'Corsair 550W');

CREATE TABLE Sistema (
    Id_sistema INT PRIMARY KEY AUTO_INCREMENT,
    Nombre_sistema VARCHAR(100)
);
INSERT INTO Sistema VALUES(1,'Sistema de Adquisiciones');
INSERT INTO Sistema VALUES(2,'Sistema de Gestion');
CREATE TABLE Usuario_PC (
    Id_usuario INT,
    Id_pc INT,
    PRIMARY KEY (Id_usuario, Id_pc),
    FOREIGN KEY (Id_usuario) REFERENCES Usuario(Id_usuario),
    FOREIGN KEY (Id_pc) REFERENCES Pc(Id_pc)
);
INSERT INTO Usuario_PC VALUES(1,1);
INSERT INTO Usuario_PC VALUES(2,2);
INSERT INTO Usuario_PC VALUES(3,2);
INSERT INTO Usuario_PC VALUES(4,3);
INSERT INTO Usuario_PC VALUES(5,2);
CREATE TABLE Usuario_Sistema (
    Id_usuario INT,
    Id_sistema INT,
    Activo BOOLEAN,
    PRIMARY KEY (Id_usuario, Id_sistema),
    FOREIGN KEY (Id_usuario) REFERENCES Usuario(Id_usuario),
    FOREIGN KEY (Id_sistema) REFERENCES Sistema(Id_sistema)
);
INSERT INTO Usuario_Sistema VALUES(1,1,1);
INSERT INTO Usuario_Sistema VALUES(2,2,0);
INSERT INTO Usuario_Sistema VALUES(4,2,1);
INSERT INTO Usuario_Sistema VALUES(3,2,1);
INSERT INTO Usuario_Sistema VALUES(4,1,0);
DELETE FROM sqlite_sequence;
INSERT INTO sqlite_sequence VALUES('posts',2);
INSERT INTO sqlite_sequence VALUES('Usuario',5);
INSERT INTO sqlite_sequence VALUES('Pc',3);
INSERT INTO sqlite_sequence VALUES('Sistema',2);
COMMIT;
