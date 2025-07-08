-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 07-04-2025 a las 02:10:22
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12
-- MODIFICADO: Incluye campos DNI, fecha_nacimiento y direccion_empleado

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
-- ACTUALIZADA: Incluye dni_empleado, fecha_nacimiento, direccion_empleado
--

DROP TABLE IF EXISTS `tbl_empleados`;
CREATE TABLE `tbl_empleados` (
  `id_empleado` int(11) NOT NULL AUTO_INCREMENT,
  `dni_empleado` varchar(8) DEFAULT NULL COMMENT 'Documento Nacional de Identidad',
  `nombre_empleado` varchar(50) DEFAULT NULL,
  `apellido_empleado` varchar(50) DEFAULT NULL,
  `sexo_empleado` int(11) DEFAULT NULL,
  `telefono_empleado` varchar(50) DEFAULT NULL,
  `email_empleado` varchar(50) DEFAULT NULL,
  `profesion_empleado` varchar(50) DEFAULT NULL,
  `foto_empleado` mediumtext DEFAULT NULL,
  `salario_empleado` bigint(20) DEFAULT NULL,
  `fecha_nacimiento` date DEFAULT NULL COMMENT 'Fecha de nacimiento del empleado',
  `direccion_empleado` varchar(255) DEFAULT NULL COMMENT 'Dirección de residencia del empleado',
  `fecha_registro` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id_empleado`),
  UNIQUE KEY `uk_dni_empleado` (`dni_empleado`),
  KEY `idx_dni_empleado` (`dni_empleado`),
  KEY `idx_fecha_nacimiento` (`fecha_nacimiento`),
  KEY `idx_direccion_empleado` (`direccion_empleado`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `tbl_empleados`
-- ACTUALIZADO: Incluye datos de ejemplo para los nuevos campos
--

INSERT INTO `tbl_empleados` (`id_empleado`, `dni_empleado`, `nombre_empleado`, `apellido_empleado`, `sexo_empleado`, `telefono_empleado`, `email_empleado`, `profesion_empleado`, `foto_empleado`, `salario_empleado`, `fecha_nacimiento`, `direccion_empleado`, `fecha_registro`) VALUES
(4, '73443858', 'Renato', 'Yonz', 1, '984353973', 'renato.yonz@gmail.com', 'Ingeniero de Sistemas', '3011d28d2ac84d1d8f69f4a326152623ec364b49fe9d4b99b928ce1406b0c562.png', 3500000, '1990-05-15', 'Av. Ejemplo 123, Lima, Perú', '2023-08-23 22:04:49'),
(5, '75025881', 'Brittani', 'Palomino', 2, '977476104', 'brittani.palomino@gmail.com', 'Ingeniera de Sistemas', '87d8c959e4c947048cf6f203a061452aee2c7d37a41e45498554fd8c7fd77c3e.jpg', 1200000, '1992-08-20', 'Jr. Prueba 456, Lima, Perú', '2023-08-23 22:05:34'),
(6, '70766108', 'Ricardo', 'Medina', 1, '953293291', 'ricardo.medina@gmail.com', 'Ingeniero de Sistemas', '4f86bf4d0fb24073b4cd765fea583ebf03857dd82708415183f50570575fd9c1.png', 21000, '1988-12-10', 'Calle Test 789, Lima, Perú', '2023-08-23 22:06:13'),
(7, '72315114', 'Valentino', 'Oriundo', 1, '922196988', 'valentino.oriundo@gmail.com', 'Ingeniero de Sistemas', 'b2028c6ecdb34f1888792ced2069f147fb28f189af62478f88de6324746a0dde.png', 50000, '1995-03-25', 'Av. Demo 321, Lima, Perú', '2023-08-23 22:07:28');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `users`
--

DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name_surname` varchar(100) NOT NULL,
  `email_user` varchar(50) NOT NULL,
  `pass_user` text NOT NULL,
  `created_user` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`)
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

DROP TABLE IF EXISTS `tbl_configuracion_asistencia`;
CREATE TABLE `tbl_configuracion_asistencia` (
  `id_configuracion` int(11) NOT NULL AUTO_INCREMENT,
  `parametro` varchar(100) NOT NULL,
  `valor` text NOT NULL,
  `descripcion` text DEFAULT NULL,
  `tipo_dato` enum('string','number','boolean','time') DEFAULT 'string',
  `fecha_creacion` timestamp NOT NULL DEFAULT current_timestamp(),
  `fecha_actualizacion` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id_configuracion`),
  UNIQUE KEY `parametro` (`parametro`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `tbl_configuracion_asistencia`
-- CONFIGURACIÓN: Lunes a Sábado de 9:00 AM a 7:00 PM
--

INSERT INTO `tbl_configuracion_asistencia` (`parametro`, `valor`, `descripcion`, `tipo_dato`) VALUES
('hora_entrada_inicio', '09:00:00', 'Hora de inicio permitida para marcar (9 AM)', 'time'),
('hora_entrada_fin', '19:00:00', 'Hora límite permitida para marcar (7 PM)', 'time'),
('hora_salida_inicio', '09:00:00', 'Hora de inicio permitida para salida (9 AM)', 'time'),
('hora_salida_fin', '19:00:00', 'Hora límite permitida para salida (7 PM)', 'time'),
('tolerancia_minutos', '15', 'Minutos de tolerancia para llegadas tarde', 'number'),
('requiere_foto', 'true', 'Requiere foto para marcar asistencia', 'boolean'),
('permitir_marcado_remoto', 'false', 'Permite marcado desde ubicaciones remotas', 'boolean'),
('dias_laborables', '1,2,3,4,5,6', 'Días laborables: Lunes(1) a Sábado(6)', 'string'),
('empresa_nombre', 'Mi Empresa', 'Nombre de la empresa', 'string'),
('sistema_activo', 'true', 'Sistema de asistencia activo', 'boolean'),
('tolerancia_salida_minutos', '15', 'Minutos de tolerancia para salida temprana', 'number'),
('permitir_marcado_fuera_horario', 'false', 'NO permitir marcar fuera de 9AM-7PM', 'boolean'),
('validar_dias_laborables', 'true', 'Validar que solo se marque Lunes-Sábado', 'boolean'),
('horas_laborales_dia', '10', 'Horas laborales por día (9AM a 7PM = 10 horas)', 'number'),
('zona_horaria', 'America/Lima', 'Zona horaria del sistema', 'string');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tbl_asistencia`
--

DROP TABLE IF EXISTS `tbl_asistencia`;
CREATE TABLE `tbl_asistencia` (
  `id_asistencia` int(11) NOT NULL AUTO_INCREMENT,
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
  `fecha_registro` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id_asistencia`),
  KEY `idx_empleado_fecha` (`id_empleado`,`fecha_asistencia`),
  KEY `idx_fecha` (`fecha_asistencia`),
  CONSTRAINT `fk_asistencia_empleado` FOREIGN KEY (`id_empleado`) REFERENCES `tbl_empleados` (`id_empleado`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Tabla adicional para estadísticas de consultas DNI (OPCIONAL)
--

DROP TABLE IF EXISTS `tbl_estadisticas_dni`;
CREATE TABLE `tbl_estadisticas_dni` (
  `id_estadistica` int(11) NOT NULL AUTO_INCREMENT,
  `fecha` date NOT NULL,
  `tipo` enum('consulta','autocompletado','duplicado','error') DEFAULT 'consulta',
  `cantidad` int(11) DEFAULT 1,
  `detalles` text DEFAULT NULL,
  `fecha_creacion` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id_estadistica`),
  UNIQUE KEY `uk_fecha_tipo` (`fecha`,`tipo`),
  KEY `idx_fecha` (`fecha`),
  KEY `idx_tipo` (`tipo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Función para calcular edad
--

DELIMITER //

DROP FUNCTION IF EXISTS calcular_edad//
CREATE FUNCTION calcular_edad(fecha_nac DATE) 
RETURNS INT
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE edad INT;
    IF fecha_nac IS NULL THEN
        RETURN NULL;
    END IF;
    SET edad = TIMESTAMPDIFF(YEAR, fecha_nac, CURDATE());
    RETURN edad;
END//

DELIMITER ;

-- --------------------------------------------------------

--
-- Vista para consultas rápidas de empleados con edad calculada
--

DROP VIEW IF EXISTS `vw_empleados_completo`;
CREATE VIEW `vw_empleados_completo` AS
SELECT 
    e.id_empleado,
    e.dni_empleado,
    e.nombre_empleado,
    e.apellido_empleado,
    CONCAT(e.nombre_empleado, ' ', e.apellido_empleado) AS nombre_completo,
    CASE
        WHEN e.sexo_empleado = 1 THEN 'Masculino'
        ELSE 'Femenino'
    END AS sexo_empleado,
    e.telefono_empleado,
    e.email_empleado,
    e.profesion_empleado,
    e.salario_empleado,
    e.fecha_nacimiento,
    calcular_edad(e.fecha_nacimiento) AS edad,
    e.direccion_empleado,
    e.foto_empleado,
    DATE_FORMAT(e.fecha_registro, '%d/%m/%Y %h:%i %p') AS fecha_registro_formato,
    e.fecha_registro
FROM tbl_empleados e
ORDER BY e.id_empleado DESC;

-- --------------------------------------------------------

--
-- Datos de ejemplo para estadísticas DNI (OPCIONAL)
--

INSERT INTO `tbl_estadisticas_dni` (`fecha`, `tipo`, `cantidad`, `detalles`) VALUES
(CURDATE(), 'consulta', 0, 'Consultas DNI realizadas hoy'),
(CURDATE(), 'autocompletado', 0, 'Campos autocompletados hoy'),
(CURDATE(), 'duplicado', 0, 'DNIs duplicados detectados hoy'),
(CURDATE(), 'error', 0, 'Errores en consultas DNI hoy');

COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

-- ========================================
-- VERIFICACIONES FINALES
-- ========================================

-- Verificar estructura de tabla empleados
SELECT 
    COLUMN_NAME,
    COLUMN_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT,
    COLUMN_COMMENT
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'crud_python' 
AND TABLE_NAME = 'tbl_empleados'
ORDER BY ORDINAL_POSITION;

-- Verificar datos de empleados con nuevos campos
SELECT 
    id_empleado,
    dni_empleado,
    nombre_empleado,
    apellido_empleado,
    fecha_nacimiento,
    edad,
    direccion_empleado
FROM vw_empleados_completo;

-- Verificar índices creados
SHOW INDEX FROM tbl_empleados WHERE Key_name IN ('idx_dni_empleado', 'idx_fecha_nacimiento', 'idx_direccion_empleado', 'uk_dni_empleado');

-- ========================================
-- COMENTARIOS DE IMPLEMENTACIÓN
-- ========================================

/*
CAMBIOS REALIZADOS EN EL SCRIPT ORIGINAL:

1. TABLA tbl_empleados:
   ✅ Agregado: dni_empleado VARCHAR(8) - Documento Nacional de Identidad
   ✅ Agregado: fecha_nacimiento DATE - Fecha de nacimiento
   ✅ Agregado: direccion_empleado VARCHAR(255) - Dirección de residencia
   ✅ Índices: idx_dni_empleado, idx_fecha_nacimiento, idx_direccion_empleado
   ✅ Restricción: uk_dni_empleado UNIQUE

2. DATOS DE PRUEBA:
   ✅ Actualizados registros existentes con DNI, fecha nacimiento y dirección
   ✅ DNIs únicos para cada empleado
   ✅ Fechas de nacimiento realistas
   ✅ Direcciones de ejemplo

3. FUNCIONALIDADES ADICIONALES:
   ✅ Tabla tbl_estadisticas_dni - Para monitoreo de consultas
   ✅ Función calcular_edad() - Cálculo automático de edad
   ✅ Vista vw_empleados_completo - Consultas optimizadas
   ✅ Datos de ejemplo para estadísticas

4. COMPATIBILIDAD:
   ✅ Mantiene toda la estructura original
   ✅ Compatible con sistema de asistencias existente
   ✅ No rompe funcionalidad actual
   ✅ Preparado para Docker

PRÓXIMOS PASOS:
1. Usar este script en tu docker-compose.yml o Dockerfile
2. Actualizar funciones_home.py con las modificaciones del backend
3. Reemplazar form_empleado.html con la versión que incluye DNI
4. Probar funcionalidad de consulta DNI

ESTRUCTURA FINAL:
- 4 tablas originales (sin cambios)
- tbl_empleados actualizada con 3 campos nuevos
- 1 tabla nueva para estadísticas (opcional)
- 1 función para calcular edad
- 1 vista para consultas optimizadas
- Índices optimizados para búsquedas
*/