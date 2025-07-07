-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 07-04-2025 a las 02:10:22
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `crud_python`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tbl_empleados`
--

CREATE TABLE `tbl_empleados` (
  `id_empleado` int(11) NOT NULL,
  `nombre_empleado` varchar(50) DEFAULT NULL,
  `apellido_empleado` varchar(50) DEFAULT NULL,
  `sexo_empleado` int(11) DEFAULT NULL,
  `telefono_empleado` varchar(50) DEFAULT NULL,
  `email_empleado` varchar(50) DEFAULT NULL,
  `profesion_empleado` varchar(50) DEFAULT NULL,
  `foto_empleado` mediumtext DEFAULT NULL,
  `salario_empleado` bigint(20) DEFAULT NULL,
  `fecha_registro` timestamp NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `tbl_empleados`
--

INSERT INTO `tbl_empleados` (`id_empleado`, `nombre_empleado`, `apellido_empleado`, `sexo_empleado`, `telefono_empleado`, `email_empleado`, `profesion_empleado`, `foto_empleado`, `salario_empleado`, `fecha_registro`) VALUES
(4, 'Renato', 'Yonz', 1, '984353973', 'renato.yonz@gmail.com', 'Ingeniero de Sistemas', '3011d28d2ac84d1d8f69f4a326152623ec364b49fe9d4b99b928ce1406b0c562.png', 3500000, '2023-08-23 22:04:49'),
(5, 'Brittani', 'Palomino', 2, '977476104', 'brittani.palomino@gmail.com', 'Ingeniera de Sistemas', '87d8c959e4c947048cf6f203a061452aee2c7d37a41e45498554fd8c7fd77c3e.jpg', 1200000, '2023-08-23 22:05:34'),
(6, 'Ricardo', 'Medina', 1, '953293291', 'ricardo.medina@gmail.com', 'Ingeniero de Sistemas', '4f86bf4d0fb24073b4cd765fea583ebf03857dd82708415183f50570575fd9c1.png', 21000, '2023-08-23 22:06:13'),
(7, 'Valentino', 'Oriundo', 1, '922196988', 'valentino.oriundo@gmail.com', 'Ingeniero de Sistemas', 'b2028c6ecdb34f1888792ced2069f147fb28f189af62478f88de6324746a0dde.png', 50000, '2023-08-23 22:07:28');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `name_surname` varchar(100) NOT NULL,
  `email_user` varchar(50) NOT NULL,
  `pass_user` text NOT NULL,
  `created_user` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `users`
--

INSERT INTO `users` (`id`, `name_surname`, `email_user`, `pass_user`, `created_user`) VALUES
(3, 'Valentino Oriundo', 'valentino@gmail.com', 'scrypt:32768:8:1$QG9Jir2pwhUweMb1$0b080c6157f68d8c01fd89b4752c320c8ab5feff71ff06fcf19d6aa13ff827c15de8550af375a148b600a29a1d54515540bdcae773fdebf79e6af0196bd53b32', '2025-04-05 02:05:57');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tbl_configuracion_asistencia`
--

CREATE TABLE `tbl_configuracion_asistencia` (
  `id_configuracion` int(11) NOT NULL,
  `parametro` varchar(100) NOT NULL,
  `valor` text NOT NULL,
  `descripcion` text DEFAULT NULL,
  `tipo_dato` enum('string','number','boolean','time') DEFAULT 'string',
  `fecha_creacion` timestamp NOT NULL DEFAULT current_timestamp(),
  `fecha_actualizacion` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `tbl_configuracion_asistencia`
--

INSERT INTO `tbl_configuracion_asistencia` (`id_configuracion`, `parametro`, `valor`, `descripcion`, `tipo_dato`) VALUES
(1, 'hora_entrada_inicio', '08:00:00', 'Hora de inicio del rango de entrada', 'time'),
(2, 'hora_entrada_fin', '09:00:00', 'Hora límite para marcar entrada', 'time'),
(3, 'hora_salida_inicio', '17:00:00', 'Hora de inicio del rango de salida', 'time'),
(4, 'hora_salida_fin', '18:00:00', 'Hora límite para marcar salida', 'time'),
(5, 'tolerancia_minutos', '15', 'Minutos de tolerancia para llegadas tarde', 'number'),
(6, 'requiere_foto', 'true', 'Requiere foto para marcar asistencia', 'boolean'),
(7, 'permitir_marcado_remoto', 'false', 'Permite marcado desde ubicaciones remotas', 'boolean'),
(8, 'dias_laborables', '1,2,3,4,5', 'Días laborables (1=Lunes, 7=Domingo)', 'string'),
(9, 'empresa_nombre', 'Mi Empresa', 'Nombre de la empresa', 'string'),
(10, 'sistema_activo', 'true', 'Sistema de asistencia activo', 'boolean');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tbl_asistencia`
--

CREATE TABLE `tbl_asistencia` (
  `id_asistencia` int(11) NOT NULL,
  `id_empleado` int(11) NOT NULL,
  `fecha_asistencia` date NOT NULL,
  `hora_entrada` time DEFAULT NULL,
  `hora_salida` time DEFAULT NULL,
  `tipo_marcado` enum('entrada','salida') NOT NULL,
  `estado` enum('presente','ausente','tarde','temprano') DEFAULT 'presente',
  `observaciones` text DEFAULT NULL,
  `imagen_entrada` longtext DEFAULT NULL,
  `imagen_salida` longtext DEFAULT NULL,
  `coordenadas_gps` varchar(100) DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `fecha_registro` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `tbl_empleados`
--
ALTER TABLE `tbl_empleados`
  ADD PRIMARY KEY (`id_empleado`);

--
-- Indices de la tabla `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `tbl_configuracion_asistencia`
--
ALTER TABLE `tbl_configuracion_asistencia`
  ADD PRIMARY KEY (`id_configuracion`),
  ADD UNIQUE KEY `parametro` (`parametro`);

--
-- Indices de la tabla `tbl_asistencia`
--
ALTER TABLE `tbl_asistencia`
  ADD PRIMARY KEY (`id_asistencia`),
  ADD KEY `idx_empleado_fecha` (`id_empleado`,`fecha_asistencia`),
  ADD KEY `idx_fecha` (`fecha_asistencia`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `tbl_empleados`
--
ALTER TABLE `tbl_empleados`
  MODIFY `id_empleado` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT de la tabla `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `tbl_configuracion_asistencia`
--
ALTER TABLE `tbl_configuracion_asistencia`
  MODIFY `id_configuracion` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT de la tabla `tbl_asistencia`
--
ALTER TABLE `tbl_asistencia`
  MODIFY `id_asistencia` int(11) NOT NULL AUTO_INCREMENT;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `tbl_asistencia`
--
ALTER TABLE `tbl_asistencia`
  ADD CONSTRAINT `fk_asistencia_empleado` FOREIGN KEY (`id_empleado`) REFERENCES `tbl_empleados` (`id_empleado`) ON DELETE CASCADE ON UPDATE CASCADE;

COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;