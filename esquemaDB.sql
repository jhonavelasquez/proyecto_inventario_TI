CREATE TABLE `categoria_historial` (
  `id_categoria` int(11) NOT NULL,
  `nombre_categoria` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


INSERT INTO `categoria_historial` (`id_categoria`, `nombre_categoria`) VALUES
(1, 'Usuarios'),
(2, 'Sistemas'),
(3, 'Computadores'),
(4, 'Reportes');

CREATE TABLE `historial` (
  `id_historial` int(11) NOT NULL,
  `usuario_historial` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `descripcion` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `fecha` timestamp NULL DEFAULT NULL,
  `id_categoria` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


CREATE TABLE `notificaciones` (
  `id_notificacion` int(11) NOT NULL,
  `id_usuario` int(11) DEFAULT NULL,
  `id_reporte` int(11) DEFAULT NULL,
  `fecha_notificacion` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `mensaje` varchar(200) COLLATE utf8_unicode_ci DEFAULT NULL,
  `leido` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE `pc` (
  `id_pc` int(11) NOT NULL,
  `nombre_pc` varchar(30) COLLATE utf8_unicode_ci DEFAULT NULL,
  `procesador` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `placa` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `almacenamiento` int(11) DEFAULT NULL,
  `ram` int(11) DEFAULT NULL,
  `fuente` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


INSERT INTO `pc` (`Id_pc`, `Nombre_pc`, `Procesador`, `Placa`, `Almacenamiento`, `Ram`, `Fuente`) VALUES
(1, 'SA2101051', 'INTEL I7', 'ASUS ROG STRIX', 512, 16, 'Corsair 650W');

CREATE TABLE `reportes` (
  `id_reporte` int(11) NOT NULL,
  `usuario_id` int(11) DEFAULT NULL,
  `num_solicitud` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `asunto` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `descripcion` varchar(300) COLLATE utf8_unicode_ci NOT NULL,
  `fecha` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_solucion` timestamp NULL DEFAULT NULL,
  `archivo` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `enviado` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE `sistema` (
  `id_sistema` int(11) NOT NULL,
  `nombre_sistema` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

INSERT INTO `sistema` (`id_sistema`, `nombre_sistema`) VALUES
(1, 'SISTEMA DE GESTIÓN DOCUMENTAL (SGD)'),
(2, 'SISTEMA DE ADQUISICIONES MUNICIPALES (AB)'),
(3, 'SISTEMA DE VECINO DIGITAL (ONLINE) (PPO)'),
(4, 'SISTEMA CONTABILIDAD GUBERNAMENTAL (FIN)'),
(5, 'SISTEMA DECRETO DE PAGO WEB (DPW)'),
(6, 'SISTEMA CONTROL PRESUPUESTARIO (FIN-SECPLA)'),
(7, 'SISTEMA PRESUPUESTARIO (FIN-SECPLA)'),
(8, 'SISTEMA DE VENTANILLA ÚNICA MUNICIPAL (VUM)'),
(9, 'SISTEMA RELOJ CONTROL (RRHH)'),
(10, 'SISTEMA CONTROL DE ASISTENCIA GENERA (RRHH)'),
(11, 'SISTEMA DE BODEGAS (AB)'),
(12, 'SISTEMA DE ACTIVO FIJO (AB)'),
(13, 'SISTEMA JUZGADO DE POLICÍA LOCAL (JPL)'),
(14, 'SISTEMA DE INSPECCIÓN (INS)'),
(15, 'SISTEMA DE DERECHOS DE ASEO (RENT)'),
(16, 'SISTEMA LICENCIAS DE CONDUCIR (TRANS)'),
(17, 'SISTEMA DE PERMISOS DE CIRCULACIÓN (TRANS)'),
(18, 'SISTEMA DE PATENTES COMERCIALES (RENT)'),
(19, 'SISTEMA ÓRDENES DE INGRESO (FIN)'),
(20, 'SISTEMA DE TESORERÍA MUNICIPAL (FIN)'),
(21, 'SISTEMA CONCILIACIÓN BANCARIA (FIN)'),
(22, 'SISTEMA CONVENIOS DE PAGO (FIN)'),
(23, 'SISTEMA ASISTENCIA SOCIAL (DIDECO)'),
(24, 'SISTEMA REMUNERACIONES MUNICIPALES (RRHH)'),
(25, 'SISTEMA REMUNERACIONES SALUD (RRHH)'),
(26, 'SISTEMA REMUNERACIONES EDUCACIÓN (RRHH)'),
(27, 'SISTEMA REMUNERACIONES JUNJI (RRHH)'),
(28, 'SISTEMA DE HONORARIOS (RRHH)'),
(29, 'SISTEMA PERSONAL MUNICIPAL (RRHH)'),
(30, 'SISTEMA PERSONAL EDUCACION (RRHH)'),
(31, 'SISTEMA PERSONAL SALUD (RRHH)'),
(32, 'SISTEMA PERSONAL JUNJI (RRHH)'),
(33, 'SISTEMA GESTIÓN MUNICIPAL (GEST)'),
(34, 'SISTEMA DE DECLARACIÓN DE RENTAS (FIN)'),
(35, 'SISTEMA DE VENTANILLA ÚNICA (ADM)'),
(36, 'SISTEMA DE EXÁMENES TEÓRICOS LEY 19.280 (TRANS)'),
(37, 'SISTEMA DE MONITO WEB (TRANS-JUZ-INSP)'),
(38, 'SISTEMA DE ENVIÓ DE SOLICITUDES (FIN-ADM-DOM-DIMAO)'),
(39, 'SISTEMA DE FOTOGRAFÍA (TRANS)'),
(40, 'SISTEMA INTRANET DE RECURSOS HUMANOS (RRHH)'),
(41, 'SISTEMA ORGANIZACIONES COMUNITARIAS (DIDECO)'),
(42, 'SISTEMA DE BIENESTAR (RRHH)'),
(43, 'SISTEMA DE INTRANET DE RRHH (RRHH)'),
(44, 'SMARTDOM (DOM)'),
(45, 'PLATAFORMA MULTISERVICIO'),
(46, 'CITYMIS'),
(47, 'SISTEMA V-FORM BECAS MUNICIPALES'),
(48, 'SISTEMA DE INFORMACIÓN TERRITORIAL DE SAN ANTONIO SITSA');

CREATE TABLE `tipo_usuario` (
  `id_tipo_usuario` int(11) NOT NULL,
  `nombre_tipo_usuario` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


INSERT INTO `tipo_usuario` (`id_tipo_usuario`, `nombre_tipo_usuario`) VALUES
(1, 'Administrador'),
(2, 'Lector'),
(3, 'Editor');

CREATE TABLE `usuario` (
  `id_usuario` int(11) NOT NULL,
  `nombre_user` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `email` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `psw` varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  `id_tipo_usuario` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


INSERT INTO `usuario` (`Id_usuario`, `Nombre_user`, `Email`, `Psw`, `id_tipo_usuario`) VALUES
(1, 'ADMIN', 'JONATHAN.VR484@GMAIL.COM', 'scrypt:32768:8:1$zlTTrxQEIFrn4ATh$3bd289cb158c23e594fa118311062f0fe2f7fd333f36b6f2764f86b80160be7f32bb80a30ba7b336378ba7b5f8394e24a6b061900048788c54d385d0a3891e0c', 1);

CREATE TABLE `usuario_sistema_pc` (
  `Id_usuario` int(11) NOT NULL,
  `Id_sistema` int(11) NOT NULL,
  `Id_pc` int(11) NOT NULL,
  `Activo` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

INSERT INTO `usuario_sistema_pc` (`Id_usuario`, `Id_sistema`, `Id_pc`, `Activo`) VALUES
(1, 1, 1, 1);

ALTER TABLE `categoria_historial`
  ADD PRIMARY KEY (`id_categoria`);

ALTER TABLE `historial`
  ADD PRIMARY KEY (`Id_historial`),
  ADD KEY `id_categoria` (`id_categoria`);

ALTER TABLE `notificaciones`
  ADD PRIMARY KEY (`id_notificacion`),
  ADD KEY `id_usuario` (`id_usuario`),
  ADD KEY `id_reporte` (`id_reporte`);

ALTER TABLE `pc`
  ADD PRIMARY KEY (`Id_pc`);

ALTER TABLE `reportes`
  ADD PRIMARY KEY (`id_reporte`),
  ADD KEY `usuario_id` (`usuario_id`);

ALTER TABLE `sistema`
  ADD PRIMARY KEY (`Id_sistema`);

ALTER TABLE `tipo_usuario`
  ADD PRIMARY KEY (`id_tipo_usuario`);

ALTER TABLE `usuario`
  ADD PRIMARY KEY (`Id_usuario`),
  ADD KEY `id_tipo_usuario` (`id_tipo_usuario`);

ALTER TABLE `usuario_sistema_pc`
  ADD PRIMARY KEY (`Id_usuario`,`Id_sistema`,`Id_pc`),
  ADD KEY `Id_sistema` (`Id_sistema`),
  ADD KEY `Id_pc` (`Id_pc`);

ALTER TABLE `categoria_historial`
  MODIFY `id_categoria` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

ALTER TABLE `historial`
  MODIFY `Id_historial` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=102;

ALTER TABLE `notificaciones`
  MODIFY `id_notificacion` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

ALTER TABLE `pc`
  MODIFY `Id_pc` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

ALTER TABLE `reportes`
  MODIFY `id_reporte` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

ALTER TABLE `sistema`
  MODIFY `Id_sistema` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=62;

ALTER TABLE `tipo_usuario`
  MODIFY `id_tipo_usuario` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

ALTER TABLE `usuario`
  MODIFY `Id_usuario` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

ALTER TABLE `historial`
  ADD CONSTRAINT `historial_ibfk_1` FOREIGN KEY (`id_categoria`) REFERENCES `categoria_historial` (`id_categoria`) ON DELETE CASCADE;

ALTER TABLE `notificaciones`
  ADD CONSTRAINT `notificaciones_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`Id_usuario`) ON DELETE CASCADE,
  ADD CONSTRAINT `notificaciones_ibfk_2` FOREIGN KEY (`id_reporte`) REFERENCES `reportes` (`id_reporte`) ON DELETE CASCADE;

ALTER TABLE `reportes`
  ADD CONSTRAINT `reportes_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuario` (`Id_usuario`) ON DELETE CASCADE;

ALTER TABLE `usuario`
  ADD CONSTRAINT `usuario_ibfk_1` FOREIGN KEY (`id_tipo_usuario`) REFERENCES `tipo_usuario` (`id_tipo_usuario`) ON DELETE CASCADE;

ALTER TABLE `usuario_sistema_pc`
  ADD CONSTRAINT `usuario_sistema_pc_ibfk_1` FOREIGN KEY (`Id_usuario`) REFERENCES `usuario` (`Id_usuario`) ON DELETE CASCADE,
  ADD CONSTRAINT `usuario_sistema_pc_ibfk_2` FOREIGN KEY (`Id_sistema`) REFERENCES `sistema` (`Id_sistema`) ON DELETE CASCADE,
  ADD CONSTRAINT `usuario_sistema_pc_ibfk_3` FOREIGN KEY (`Id_pc`) REFERENCES `pc` (`Id_pc`) ON DELETE CASCADE;
COMMIT;

