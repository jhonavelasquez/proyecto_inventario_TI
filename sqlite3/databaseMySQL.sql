PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    content TEXT NOT NULL
);
INSERT INTO posts VALUES(1,'2024-08-29 19:41:46','First Post','Content for the first post');
INSERT INTO posts VALUES(2,'2024-08-29 19:41:46','Second Post','Content for the second post');

CREATE TABLE Usuario (
    Id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre_user VARCHAR(100),
    Email VARCHAR(100),
    Psw VARCHAR(100)
);
INSERT INTO Usuario VALUES(1,'ADMIN','admin@sanantonio.cl','scrypt:32768:8:1$zDOrimZD5CqrcHeL$d34755da282dd6525c38fc63f3022d1df187eec50ce6ee5c19e9cd1c721360e39581a14f585f7444c13e15d864b1d9e1f8340789355dd8320f6c22eafa02dcfb');
INSERT INTO Usuario VALUES(2,'JONVELASQUEZ','JONVELASQUEZ@SANANTONIO.CL','scrypt:32768:8:1$OZfUadKq5UTQZSfT$3f0dd2d2e4450bddfe9b84ebb3cb936096f35a148ee173fd63b4fa5d143dac9ab7afabbf42313562a507bd4dc26f489dc1e506c524da5bccefc268d2e95793d6');

CREATE TABLE Pc (
    Id_pc INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre_pc VARCHAR(100),
    Placa VARCHAR(50),
    Almacenamiento INTEGER,  -- en GB
    Ram INTEGER,    -- en GB
    Fuente VARCHAR(100)
);
INSERT INTO Pc VALUES(1,'SA2101051','ASUS ROG STRIX',512,16,'Corsair 650W');
INSERT INTO Pc VALUES(2,'SA2000000','HP Network',512,8,'Corsair 550W');
INSERT INTO Pc VALUES(3,'SA0999999','HP',512,8,'Corsair 550W');

CREATE TABLE Sistema (
    Id_sistema INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre_sistema VARCHAR(100)
);
INSERT INTO Sistema VALUES(1,'SISTEMA DE GESTIÓN DOCUMENTAL (SGD)');
INSERT INTO Sistema VALUES(2,'SISTEMA DE ADQUISICIONES MUNICIPALES (AB)');
INSERT INTO Sistema VALUES(3,'SISTEMA DE VECINO DIGITAL (ONLINE) (PPO)');
INSERT INTO Sistema VALUES(4,'SISTEMA CONTABILIDAD GUBERNAMENTAL (FIN)');
INSERT INTO Sistema VALUES(5,'SISTEMA DECRETO DE PAGO WEB (DPW)');
INSERT INTO Sistema VALUES(6,'SISTEMA CONTROL PRESUPUESTARIO (FIN-SECPLA)');
INSERT INTO Sistema VALUES(7,'SISTEMA PRESUPUESTARIO (FIN-SECPLA)');
INSERT INTO Sistema VALUES(8,'SISTEMA DE VENTANILLA ÚNICA MUNICIPAL (VUM)');
INSERT INTO Sistema VALUES(9,'SISTEMA RELOJ CONTROL (RRHH)');
INSERT INTO Sistema VALUES(10,'SISTEMA CONTROL DE ASISTENCIA GENERA (RRHH)');
INSERT INTO Sistema VALUES(11,'SISTEMA DE BODEGAS (AB)');
INSERT INTO Sistema VALUES(12,'SISTEMA DE ACTIVO FIJO (AB)');
INSERT INTO Sistema VALUES(13,'SISTEMA JUZGADO DE POLICÍA LOCAL (JPL)');
INSERT INTO Sistema VALUES(14,'SISTEMA DE INSPECCIÓN (INS)');
INSERT INTO Sistema VALUES(15,'SISTEMA DE DERECHOS DE ASEO (RENT)');
INSERT INTO Sistema VALUES(16,'SISTEMA LICENCIAS DE CONDUCIR (TRANS)');
INSERT INTO Sistema VALUES(17,'SISTEMA DE PERMISOS DE CIRCULACIÓN (TRANS)');
INSERT INTO Sistema VALUES(18,'SISTEMA DE PATENTES COMERCIALES (RENT)');
INSERT INTO Sistema VALUES(19,'SISTEMA ÓRDENES DE INGRESO (FIN)');
INSERT INTO Sistema VALUES(20,'SISTEMA DE TESORERÍA MUNICIPAL (FIN)');
INSERT INTO Sistema VALUES(21,'SISTEMA CONCILIACIÓN BANCARIA (FIN)');
INSERT INTO Sistema VALUES(22,'SISTEMA CONVENIOS DE PAGO (FIN)');
INSERT INTO Sistema VALUES(23,'SISTEMA ASISTENCIA SOCIAL (DIDECO)');
INSERT INTO Sistema VALUES(24,'SISTEMA REMUNERACIONES MUNICIPALES (RRHH)');
INSERT INTO Sistema VALUES(25,'SISTEMA REMUNERACIONES SALUD (RRHH)');
INSERT INTO Sistema VALUES(26,'SISTEMA REMUNERACIONES EDUCACIÓN (RRHH)');
INSERT INTO Sistema VALUES(27,'SISTEMA REMUNERACIONES JUNJI (RRHH)');
INSERT INTO Sistema VALUES(28,'SISTEMA DE HONORARIOS (RRHH)');
INSERT INTO Sistema VALUES(29,'SISTEMA PERSONAL MUNICIPAL (RRHH)');
INSERT INTO Sistema VALUES(30,'SISTEMA PERSONAL EDUCACION (RRHH)');
INSERT INTO Sistema VALUES(31,'SISTEMA PERSONAL SALUD (RRHH)');
INSERT INTO Sistema VALUES(32,'SISTEMA PERSONAL JUNJI (RRHH)');
INSERT INTO Sistema VALUES(33,'SISTEMA GESTIÓN MUNICIPAL (GEST)');
INSERT INTO Sistema VALUES(34,'SISTEMA DE DECLARACIÓN DE RENTAS (FIN)');
INSERT INTO Sistema VALUES(35,'SISTEMA DE VENTANILLA ÚNICA (ADM)');
INSERT INTO Sistema VALUES(36,'SISTEMA DE EXÁMENES TEÓRICOS LEY 19.280 (TRANS)');
INSERT INTO Sistema VALUES(37,'SISTEMA DE MONITO WEB (TRANS-JUZ-INSP)');
INSERT INTO Sistema VALUES(38,'SISTEMA DE ENVIÓ DE SOLICITUDES (FIN-ADM-DOM-DIMAO)');
INSERT INTO Sistema VALUES(39,'SISTEMA DE FOTOGRAFÍA (TRANS)');
INSERT INTO Sistema VALUES(40,'SISTEMA INTRANET DE RECURSOS HUMANOS (RRHH)');
INSERT INTO Sistema VALUES(41,'SISTEMA ORGANIZACIONES COMUNITARIAS (DIDECO)');
INSERT INTO Sistema VALUES(42,'SISTEMA DE BIENESTAR (RRHH)');
INSERT INTO Sistema VALUES(43,'SISTEMA DE INTRANET DE RRHH (RRHH)');
INSERT INTO Sistema VALUES(44,'SMARTDOM (DOM)');
INSERT INTO Sistema VALUES(45,'PLATAFORMA MULTISERVICIO');
INSERT INTO Sistema VALUES(46,'CITYMIS');
INSERT INTO Sistema VALUES(47,'SISTEMA V-FORM BECAS MUNICIPALES');
INSERT INTO Sistema VALUES(48,'SISTEMA DE INFORMACIÓN TERRITORIAL DE SAN ANTONIO SITSA');

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

INSERT INTO Usuario_Sistema_PC VALUES(1,1,1,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,1,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,2,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,3,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,4,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,5,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,6,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,7,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,8,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,9,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,10,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,11,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,12,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,13,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,14,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,15,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,16,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,17,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,18,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,19,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,20,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,21,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,22,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,23,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,24,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,25,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,26,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,27,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,28,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,29,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,30,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,31,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,32,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,33,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,34,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,35,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,36,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,37,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,38,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,39,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,40,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,41,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,42,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,43,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,44,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,45,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,46,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,47,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,48,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,49,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,50,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,51,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,52,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,53,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,54,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,55,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,56,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,57,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,58,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,59,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,60,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,61,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,62,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,63,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,64,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,65,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,66,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,67,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,68,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,69,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,70,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,71,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,72,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,73,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,74,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,75,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,76,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,77,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,78,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,79,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,80,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,81,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,82,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,83,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,84,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,85,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,86,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,87,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,88,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,89,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,90,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,91,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,92,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,93,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,94,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,95,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,96,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,97,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,98,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,99,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,100,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,101,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,102,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,103,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,104,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,105,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,106,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,107,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,108,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,109,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,110,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,111,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,112,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,113,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,114,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,115,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,116,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,117,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,118,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,119,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,120,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,121,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,122,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,123,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,124,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,125,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,126,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,127,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,128,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,129,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,130,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,131,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,132,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,133,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,134,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,135,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,136,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,137,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,138,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,139,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,140,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,141,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,142,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,143,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,144,2,0);
INSERT INTO Usuario_Sistema_PC VALUES(1,145,1,0);
INSERT INTO Usuario_Sistema_PC VALUES(2,145,2,0);

CREATE TABLE Historial (
    Id_historial INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_historial VARCHAR(100),
    descripcion VARCHAR(100),
    fecha VARCHAR(100),
    id_categoria INTEGER,
    FOREIGN KEY (id_categoria) REFERENCES Categoria_Historial(id_categoria)
);
INSERT INTO Historial VALUES(1,'ADMIN',' agregó a un nuevo usuario JONVELASQUEZ.  13/09/2024 11:13','13/09/2024 11:13:09',1);
INSERT INTO Historial VALUES(2,'ADMIN',' agregó un nuevo sistema.  SISTEMA PRUEBA 2.  16/09/2024 08:53','16/09/2024 08:53:38',2);
INSERT INTO Historial VALUES(3,'ADMIN',' eliminó el sistema SISTEMA PRUEBA 2.  [16/09/2024 08:54]','16/09/2024 08:54:16',2);

CREATE TABLE Categoria_historial (
    id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_categoria VARCHAR(100)
);
INSERT INTO Categoria_historial VALUES(1,'Usuarios');
INSERT INTO Categoria_historial VALUES(2,'Sistemas');
INSERT INTO Categoria_historial VALUES(3,'Computadores');
INSERT INTO Categoria_historial VALUES(4,'Reportes');
DELETE FROM sqlite_sequence;
INSERT INTO sqlite_sequence VALUES('posts',2);
INSERT INTO sqlite_sequence VALUES('Usuario',2);
INSERT INTO sqlite_sequence VALUES('Pc',3);
INSERT INTO sqlite_sequence VALUES('Categoria_historial',4);
INSERT INTO sqlite_sequence VALUES('Sistema',145);
INSERT INTO sqlite_sequence VALUES('Historial',3);
COMMIT;
