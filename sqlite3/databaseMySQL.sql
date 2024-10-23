
CREATE TABLE Usuario (
    Id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre_user VARCHAR(100),
    Email VARCHAR(100),
    Psw VARCHAR(100),
    id_tipo_usuario INTEGER,
    FOREIGN KEY (id_tipo_usuario) REFERENCES Tipo_usuario(id_tipo_usuario)
);
INSERT INTO Usuario VALUES(1,'ADMIN','JONATHAN.VR484@GMAIL.COM','scrypt:32768:8:1$DpxPbnNVK7GwTXKn$70be6a6c52c1e64e73a28373fe2e6c113e686724fbeee4019d988945d914643f44a173dd08f24f63e62aabc65dce3d38080058bd2a1c3a85702d8fbd0b8395b5',1);
CREATE TABLE Tipo_usuario (
    id_tipo_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_tipo_usuario VARCHAR(100)
);
INSERT INTO Tipo_usuario VALUES(1,'Administrador');
INSERT INTO Tipo_usuario VALUES(2,'Lector');
INSERT INTO Tipo_usuario VALUES(3,'Editor');
CREATE TABLE Pc (
    Id_pc INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre_pc VARCHAR(30),
    Procesador VARCHAR(50),
    Placa VARCHAR(50),
    Almacenamiento INTEGER,  -- en GB
    Ram INTEGER,    -- en GB
    Fuente VARCHAR(100)
);
INSERT INTO Pc VALUES(1,'SA2101051','INTEL I7','ASUS ROG STRIX',512,16,'Corsair 650W');
INSERT INTO Pc VALUES(2,'SA2000000','AMD RYZEN 7','HP Network',512,8,'Corsair 550W');
INSERT INTO Pc VALUES(3,'SA0999999','INTEL I5','HP',512,8,'Corsair 550W');
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
    num_solicitud VARCHAR(100) NOT NULL,
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
INSERT INTO Usuario_Sistema_PC VALUES(1,1,1,0);
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
INSERT INTO Categoria_historial VALUES(1,'Usuarios');
INSERT INTO Categoria_historial VALUES(2,'Sistemas');
INSERT INTO Categoria_historial VALUES(3,'Computadores');
INSERT INTO Categoria_historial VALUES(4,'Reportes');
CREATE TABLE Notificaciones (
    id_notificacion INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER, 
    id_reporte INTEGER, 
    fecha_notificacion TIMESTAMP, 
    mensaje VARCHAR(200),
    leido BOOLEAN,
    enviado BOOLEAN,
    FOREIGN KEY (id_usuario) REFERENCES Usuario(Id_usuario),
    FOREIGN KEY (id_reporte) REFERENCES Reportes(id_reporte)
);
DELETE FROM sqlite_sequence;
INSERT INTO sqlite_sequence VALUES('posts',2);
INSERT INTO sqlite_sequence VALUES('Usuario',1);
INSERT INTO sqlite_sequence VALUES('Tipo_usuario',3);
INSERT INTO sqlite_sequence VALUES('Pc',3);
INSERT INTO sqlite_sequence VALUES('Categoria_historial',4);
INSERT INTO sqlite_sequence VALUES('Sistema',48);
COMMIT;
