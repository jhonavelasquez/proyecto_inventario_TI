-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 24-10-2024 a las 13:44:59
-- Versión del servidor: 10.4.27-MariaDB
-- Versión de PHP: 7.4.33

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `sistemas_computadores_ddi`
--
CREATE DATABASE IF NOT EXISTS `sistemas_computadores_ddi` DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci;
USE `sistemas_computadores_ddi`;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `categoria_historial`
--

CREATE TABLE `categoria_historial` (
  `id_categoria` int(11) NOT NULL,
  `nombre_categoria` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- RELACIONES PARA LA TABLA `categoria_historial`:
--

--
-- Volcado de datos para la tabla `categoria_historial`
--

INSERT INTO `categoria_historial` (`id_categoria`, `nombre_categoria`) VALUES
(1, 'Usuarios'),
(2, 'Sistemas'),
(3, 'Computadores'),
(4, 'Reportes');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `historial`
--

CREATE TABLE `historial` (
  `Id_historial` int(11) NOT NULL,
  `usuario_historial` varchar(100) DEFAULT NULL,
  `descripcion` varchar(100) DEFAULT NULL,
  `fecha` varchar(100) DEFAULT NULL,
  `id_categoria` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- RELACIONES PARA LA TABLA `historial`:
--   `id_categoria`
--       `categoria_historial` -> `id_categoria`
--

--
-- Volcado de datos para la tabla `historial`
--

INSERT INTO `historial` (`Id_historial`, `usuario_historial`, `descripcion`, `fecha`, `id_categoria`) VALUES
(1, 'ADMIN', ' agregó un nuevo sistema.  SISTEMA PRUEBA 3.', '23/10/2024 10:01:13', 2),
(2, 'ADMIN', ' eliminó el sistema SISTEMA PRUEBA 3.', '23/10/2024 10:21:20', 2),
(3, 'ADMIN', ' eliminó el sistema SISTEMA PRUEBA 2.', '23/10/2024 10:21:29', 2),
(4, 'ADMIN', ' eliminó el sistema SISTEMA PRUEBA.', '23/10/2024 10:21:35', 2),
(5, 'ADMIN', ' agregó un nuevo sistema.  SISTEMA PRUEBA.', '23/10/2024 10:21:45', 2),
(6, 'ADMIN', ' agregó un nuevo sistema.  SISTEMA PRUEBA 2.', '23/10/2024 10:21:47', 2),
(7, 'ADMIN', 'Actualizó SISTEMA DE GESTIÓN DOCUMENTAL (SGD) de ADMIN. ', '23/10/2024 10:40:35', 2),
(8, 'ADMIN', 'Actualizó SISTEMA DE GESTIÓN DOCUMENTAL (SGD) de ADMIN. ', '23/10/2024 10:40:41', 2),
(9, 'ADMIN', 'Actualizó SISTEMA PRUEBA 2 de ADMIN. ', '23/10/2024 10:40:57', 2),
(10, 'ADMIN', ' agregó a un nuevo usuario JONVELASQUEZ. ', '23/10/2024 10:56:36', 1),
(11, 'ADMIN', ' agregó a un nuevo usuario PEPE. ', '23/10/2024 10:57:01', 1),
(12, 'ADMIN', 'actualizó la información de un usuario JONVELASQUEZ.', '23/10/2024 11:12:32', 1),
(13, 'ADMIN', 'actualizó la información de un usuario JONVELASQUEZ.', '23/10/2024 11:12:38', 1),
(14, 'ADMIN', 'actualizó la información de un usuario JONVELASQUEZ.', '23/10/2024 11:12:46', 1),
(15, 'ADMIN', 'actualizó la información de un usuario JONVELASQUEZ.', '23/10/2024 11:13:16', 1),
(16, 'ADMIN', 'actualizó la información de un usuario JONVELASQUEZ.', '23/10/2024 11:13:30', 1),
(17, 'ADMIN', 'actualizó la información de un usuario JONVELASQUEZ.', '23/10/2024 11:13:44', 1),
(18, 'ADMIN', 'eliminó a un usuario PEPE.', '23/10/2024 11:14:29', 1),
(19, 'ADMIN', 'actualizó la información de un usuario JONVELASQUEZ.', '23/10/2024 11:14:38', 1),
(20, 'ADMIN', 'agregó un nuevo computador. SA25101052.', '23/10/2024 11:22:07', 3),
(21, 'ADMIN', 'actualizó la información de un computador. SA2000000.', '23/10/2024 11:35:31', 3),
(22, 'ADMIN', 'actualizó la información de un computador. SA2032050.', '23/10/2024 11:35:56', 3),
(23, 'ADMIN', 'eliminó un computador. SA25101052.', '23/10/2024 11:36:15', 3),
(24, 'ADMIN', 'eliminó un computador. SA0999999.', '23/10/2024 11:36:36', 3),
(25, 'ADMIN', 'actualizó la información de un usuario JONVELASQUEZ.', '23/10/2024 11:36:47', 1),
(26, 'ADMIN', ' ha realizado un nuevo reporte. ASUNTO: Sistema de Vecino Digital.', '23/10/2024 12:16:22', 4),
(27, 'ADMIN', ' ha realizado un nuevo reporte. ASUNTO: Honorarios.', '23/10/2024 12:27:27', 4),
(28, 'ADMIN', 'eliminó a un usuario JONVELASQUEZ.', '23/10/2024 12:57:12', 1),
(29, 'ADMIN', ' agregó a un nuevo usuario JONVELASQUEZ. ', '23/10/2024 12:57:24', 1),
(30, 'ADMIN', 'actualizó la información de un usuario JONVELASQUEZ.', '23/10/2024 12:59:12', 1),
(31, 'ADMIN', 'actualizó la información de un usuario JONVELASQUEZ.', '23/10/2024 13:14:03', 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `notificaciones`
--

CREATE TABLE `notificaciones` (
  `id_notificacion` int(11) NOT NULL,
  `id_usuario` int(11) DEFAULT NULL,
  `id_reporte` int(11) DEFAULT NULL,
  `fecha_notificacion` timestamp NOT NULL DEFAULT current_timestamp(),
  `mensaje` varchar(200) DEFAULT NULL,
  `leido` tinyint(1) DEFAULT NULL,
  `enviado` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- RELACIONES PARA LA TABLA `notificaciones`:
--   `id_usuario`
--       `usuario` -> `Id_usuario`
--   `id_reporte`
--       `reportes` -> `id_reporte`
--

--
-- Volcado de datos para la tabla `notificaciones`
--

INSERT INTO `notificaciones` (`id_notificacion`, `id_usuario`, `id_reporte`, `fecha_notificacion`, `mensaje`, `leido`, `enviado`) VALUES
(1, 1, 1, '2024-10-23 19:37:04', 'Recordatorio: El reporte \'Sistema de Vecino Digital\' está cercano a su fecha de solución', 1, 1),
(2, 1, 2, '2024-10-23 19:37:04', 'Recordatorio: El reporte \'Honorarios\' está cercano a su fecha de solución', 1, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pc`
--

CREATE TABLE `pc` (
  `Id_pc` int(11) NOT NULL,
  `Nombre_pc` varchar(30) DEFAULT NULL,
  `Procesador` varchar(50) DEFAULT NULL,
  `Placa` varchar(50) DEFAULT NULL,
  `Almacenamiento` int(11) DEFAULT NULL,
  `Ram` int(11) DEFAULT NULL,
  `Fuente` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- RELACIONES PARA LA TABLA `pc`:
--

--
-- Volcado de datos para la tabla `pc`
--

INSERT INTO `pc` (`Id_pc`, `Nombre_pc`, `Procesador`, `Placa`, `Almacenamiento`, `Ram`, `Fuente`) VALUES
(1, 'SA2101051', 'INTEL I7', 'ASUS ROG STRIX', 512, 16, 'Corsair 650W'),
(2, 'SA2032050', 'AMD RYZEN 7', 'HP Network', 2000, 24, 'Corsair 650W');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `reportes`
--

CREATE TABLE `reportes` (
  `id_reporte` int(11) NOT NULL,
  `usuario_id` int(11) DEFAULT NULL,
  `num_solicitud` varchar(100) NOT NULL,
  `asunto` varchar(100) NOT NULL,
  `descripcion` varchar(300) NOT NULL,
  `fecha` timestamp NOT NULL DEFAULT current_timestamp(),
  `fecha_solucion` timestamp NULL DEFAULT NULL,
  `archivo` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- RELACIONES PARA LA TABLA `reportes`:
--   `usuario_id`
--       `usuario` -> `Id_usuario`
--

--
-- Volcado de datos para la tabla `reportes`
--

INSERT INTO `reportes` (`id_reporte`, `usuario_id`, `num_solicitud`, `asunto`, `descripcion`, `fecha`, `fecha_solucion`, `archivo`) VALUES
(1, 1, '28SP/2024', 'Sistema de Vecino Digital', 'asdasd\r\n', '2024-10-23 15:16:22', '2024-10-24 03:00:00', '28SP_2024.pdf'),
(2, 1, '28SP/2024AA', 'Honorarios', 'AAAAAAAAAAAAAAAAAAAAA\r\n', '2024-10-13 15:27:27', '2024-11-07 03:00:00', '28SP_2024AA.pdf');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `sistema`
--

CREATE TABLE `sistema` (
  `Id_sistema` int(11) NOT NULL,
  `Nombre_sistema` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- RELACIONES PARA LA TABLA `sistema`:
--

--
-- Volcado de datos para la tabla `sistema`
--

INSERT INTO `sistema` (`Id_sistema`, `Nombre_sistema`) VALUES
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
(48, 'SISTEMA DE INFORMACIÓN TERRITORIAL DE SAN ANTONIO SITSA'),
(52, 'SISTEMA PRUEBA'),
(53, 'SISTEMA PRUEBA 2');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tipo_usuario`
--

CREATE TABLE `tipo_usuario` (
  `id_tipo_usuario` int(11) NOT NULL,
  `nombre_tipo_usuario` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- RELACIONES PARA LA TABLA `tipo_usuario`:
--

--
-- Volcado de datos para la tabla `tipo_usuario`
--

INSERT INTO `tipo_usuario` (`id_tipo_usuario`, `nombre_tipo_usuario`) VALUES
(1, 'Administrador'),
(2, 'Lector'),
(3, 'Editor');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuario`
--

CREATE TABLE `usuario` (
  `Id_usuario` int(11) NOT NULL,
  `Nombre_user` varchar(100) DEFAULT NULL,
  `Email` varchar(100) DEFAULT NULL,
  `Psw` varchar(250) DEFAULT NULL,
  `id_tipo_usuario` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- RELACIONES PARA LA TABLA `usuario`:
--   `id_tipo_usuario`
--       `tipo_usuario` -> `id_tipo_usuario`
--

--
-- Volcado de datos para la tabla `usuario`
--

INSERT INTO `usuario` (`Id_usuario`, `Nombre_user`, `Email`, `Psw`, `id_tipo_usuario`) VALUES
(1, 'ADMIN', 'JONATHAN.VR484@GMAIL.COM', 'scrypt:32768:8:1$vT63miRJIgnOxEUN$f48c8337b2d086579e116622c931225afe244979996cfba4a8cd2d04468d09571cc64f0e44af669bfbda56bdf1bad7749c8b83e2fed8bf306a7278bbfb3c9724', 1),
(7, 'JONVELASQUEZ', 'JONATHAN.VR484@GMAIL.COM', 'scrypt:32768:8:1$WHXXezlBAcoEEbVL$22927997ceaaae1bf7ae2289c7cce54ec93c999dfad9a04f5bf248cd9d1aa3aa735adb3b5e06f38a28b4e807b5c59e3f546bb810c1a795f6de5ea5bd8ae14ca1', 2);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuario_sistema_pc`
--

CREATE TABLE `usuario_sistema_pc` (
  `Id_usuario` int(11) NOT NULL,
  `Id_sistema` int(11) NOT NULL,
  `Id_pc` int(11) NOT NULL,
  `Activo` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- RELACIONES PARA LA TABLA `usuario_sistema_pc`:
--   `Id_usuario`
--       `usuario` -> `Id_usuario`
--   `Id_sistema`
--       `sistema` -> `Id_sistema`
--   `Id_pc`
--       `pc` -> `Id_pc`
--

--
-- Volcado de datos para la tabla `usuario_sistema_pc`
--

INSERT INTO `usuario_sistema_pc` (`Id_usuario`, `Id_sistema`, `Id_pc`, `Activo`) VALUES
(1, 1, 1, 1),
(1, 52, 1, 0),
(1, 53, 1, 1),
(7, 1, 2, 0),
(7, 2, 2, 0),
(7, 3, 2, 0),
(7, 4, 2, 0),
(7, 5, 2, 0),
(7, 6, 2, 0),
(7, 7, 2, 0),
(7, 8, 2, 0),
(7, 9, 2, 0),
(7, 10, 2, 0),
(7, 11, 2, 0),
(7, 12, 2, 0),
(7, 13, 2, 0),
(7, 14, 2, 0),
(7, 15, 2, 0),
(7, 16, 2, 0),
(7, 17, 2, 0),
(7, 18, 2, 0),
(7, 19, 2, 0),
(7, 20, 2, 0),
(7, 21, 2, 0),
(7, 22, 2, 0),
(7, 23, 2, 0),
(7, 24, 2, 0),
(7, 25, 2, 0),
(7, 26, 2, 0),
(7, 27, 2, 0),
(7, 28, 2, 0),
(7, 29, 2, 0),
(7, 30, 2, 0),
(7, 31, 2, 0),
(7, 32, 2, 0),
(7, 33, 2, 0),
(7, 34, 2, 0),
(7, 35, 2, 0),
(7, 36, 2, 0),
(7, 37, 2, 0),
(7, 38, 2, 0),
(7, 39, 2, 0),
(7, 40, 2, 0),
(7, 41, 2, 0),
(7, 42, 2, 0),
(7, 43, 2, 0),
(7, 44, 2, 0),
(7, 45, 2, 0),
(7, 46, 2, 0),
(7, 47, 2, 0),
(7, 48, 2, 0),
(7, 52, 2, 0),
(7, 53, 2, 0);

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `categoria_historial`
--
ALTER TABLE `categoria_historial`
  ADD PRIMARY KEY (`id_categoria`);

--
-- Indices de la tabla `historial`
--
ALTER TABLE `historial`
  ADD PRIMARY KEY (`Id_historial`),
  ADD KEY `id_categoria` (`id_categoria`);

--
-- Indices de la tabla `notificaciones`
--
ALTER TABLE `notificaciones`
  ADD PRIMARY KEY (`id_notificacion`),
  ADD KEY `id_usuario` (`id_usuario`),
  ADD KEY `id_reporte` (`id_reporte`);

--
-- Indices de la tabla `pc`
--
ALTER TABLE `pc`
  ADD PRIMARY KEY (`Id_pc`);

--
-- Indices de la tabla `reportes`
--
ALTER TABLE `reportes`
  ADD PRIMARY KEY (`id_reporte`),
  ADD KEY `usuario_id` (`usuario_id`);

--
-- Indices de la tabla `sistema`
--
ALTER TABLE `sistema`
  ADD PRIMARY KEY (`Id_sistema`);

--
-- Indices de la tabla `tipo_usuario`
--
ALTER TABLE `tipo_usuario`
  ADD PRIMARY KEY (`id_tipo_usuario`);

--
-- Indices de la tabla `usuario`
--
ALTER TABLE `usuario`
  ADD PRIMARY KEY (`Id_usuario`),
  ADD KEY `id_tipo_usuario` (`id_tipo_usuario`);

--
-- Indices de la tabla `usuario_sistema_pc`
--
ALTER TABLE `usuario_sistema_pc`
  ADD PRIMARY KEY (`Id_usuario`,`Id_sistema`,`Id_pc`),
  ADD KEY `Id_sistema` (`Id_sistema`),
  ADD KEY `Id_pc` (`Id_pc`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `categoria_historial`
--
ALTER TABLE `categoria_historial`
  MODIFY `id_categoria` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `historial`
--
ALTER TABLE `historial`
  MODIFY `Id_historial` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=32;

--
-- AUTO_INCREMENT de la tabla `notificaciones`
--
ALTER TABLE `notificaciones`
  MODIFY `id_notificacion` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `pc`
--
ALTER TABLE `pc`
  MODIFY `Id_pc` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `reportes`
--
ALTER TABLE `reportes`
  MODIFY `id_reporte` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `sistema`
--
ALTER TABLE `sistema`
  MODIFY `Id_sistema` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=54;

--
-- AUTO_INCREMENT de la tabla `tipo_usuario`
--
ALTER TABLE `tipo_usuario`
  MODIFY `id_tipo_usuario` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `usuario`
--
ALTER TABLE `usuario`
  MODIFY `Id_usuario` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `historial`
--
ALTER TABLE `historial`
  ADD CONSTRAINT `historial_ibfk_1` FOREIGN KEY (`id_categoria`) REFERENCES `categoria_historial` (`id_categoria`) ON DELETE CASCADE;

--
-- Filtros para la tabla `notificaciones`
--
ALTER TABLE `notificaciones`
  ADD CONSTRAINT `notificaciones_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`Id_usuario`) ON DELETE CASCADE,
  ADD CONSTRAINT `notificaciones_ibfk_2` FOREIGN KEY (`id_reporte`) REFERENCES `reportes` (`id_reporte`) ON DELETE CASCADE;

--
-- Filtros para la tabla `reportes`
--
ALTER TABLE `reportes`
  ADD CONSTRAINT `reportes_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuario` (`Id_usuario`) ON DELETE CASCADE;

--
-- Filtros para la tabla `usuario`
--
ALTER TABLE `usuario`
  ADD CONSTRAINT `usuario_ibfk_1` FOREIGN KEY (`id_tipo_usuario`) REFERENCES `tipo_usuario` (`id_tipo_usuario`) ON DELETE CASCADE;

--
-- Filtros para la tabla `usuario_sistema_pc`
--
ALTER TABLE `usuario_sistema_pc`
  ADD CONSTRAINT `usuario_sistema_pc_ibfk_1` FOREIGN KEY (`Id_usuario`) REFERENCES `usuario` (`Id_usuario`) ON DELETE CASCADE,
  ADD CONSTRAINT `usuario_sistema_pc_ibfk_2` FOREIGN KEY (`Id_sistema`) REFERENCES `sistema` (`Id_sistema`) ON DELETE CASCADE,
  ADD CONSTRAINT `usuario_sistema_pc_ibfk_3` FOREIGN KEY (`Id_pc`) REFERENCES `pc` (`Id_pc`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
