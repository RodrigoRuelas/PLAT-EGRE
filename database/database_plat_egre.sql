-- ============================================================================
-- PROYECTO: PLAT-EGRE (Observatorio de Empleabilidad)
-- DDL FIEL AL DIAGRAMA ENTIDAD-RELACI�N
-- GESTOR: Microsoft SQL Server 2019+
-- ============================================================================

CREATE DATABASE PLAT_EGRE_DB;
GO

USE PLAT_EGRE_DB;
GO

-- ----------------------------------------------------------------------------
-- 1. TABLA: Rol
-- ----------------------------------------------------------------------------
CREATE TABLE Rol (
    id_rol INT IDENTITY(1,1) PRIMARY KEY,
    nombre_rol VARCHAR(50) NOT NULL
);

-- ----------------------------------------------------------------------------
-- 2. TABLA: Usuario
-- ----------------------------------------------------------------------------
CREATE TABLE Usuario (
    id_usuario INT IDENTITY(1,1) PRIMARY KEY,
    id_rol INT NOT NULL,
    username VARCHAR(50) NOT NULL CONSTRAINT UQ_Usuario_username UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nombre_completo VARCHAR(150) NOT NULL,
    email VARCHAR(100),
    estado BIT DEFAULT 1, -- boolean en SQL Server se representa como BIT
    fecha_creacion DATETIME DEFAULT GETDATE(),
    CONSTRAINT FK_Usuario_Rol FOREIGN KEY (id_rol) REFERENCES Rol(id_rol)
);

-- ----------------------------------------------------------------------------
-- 3. TABLA: Auditoria
-- ----------------------------------------------------------------------------
CREATE TABLE Auditoria (
    id_log INT IDENTITY(1,1) PRIMARY KEY,
    id_usuario INT NOT NULL,
    nombre_archivo VARCHAR(225) NOT NULL,
    registros_procesados INT NOT NULL,
    registros_exitosos INT NOT NULL,
    registros_fallidos INT NOT NULL,
    fecha_ejecucion DATETIME DEFAULT GETDATE(),
    estado_proceso VARCHAR(30) NOT NULL,
    CONSTRAINT FK_Auditoria_Usuario FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario)
);

-- ----------------------------------------------------------------------------
-- 4. TABLA: Carrera
-- ----------------------------------------------------------------------------
CREATE TABLE Carrera (
    id_carrera INT IDENTITY(1,1) PRIMARY KEY,
    nombre_carrera VARCHAR(100) NOT NULL,
    facultad VARCHAR(100) NOT NULL
);

-- ----------------------------------------------------------------------------
-- 5. TABLA: Egresado
-- ----------------------------------------------------------------------------
CREATE TABLE Egresado (
    id_egresado INT IDENTITY(1,1) PRIMARY KEY,
    id_carrera INT NOT NULL,
    codigo_dni VARCHAR(15) NOT NULL CONSTRAINT UQ_Egresado_codigo_dni UNIQUE,
    nom_egresado VARCHAR(150) NOT NULL,
    sexo VARCHAR(15),
    celular VARCHAR(20),
    email_profesional VARCHAR(100),
    anio_egreso INT NOT NULL,
    fecha_registro DATETIME DEFAULT GETDATE(),
    CONSTRAINT FK_Egresado_Carrera FOREIGN KEY (id_carrera) REFERENCES Carrera(id_carrera)
);

-- ----------------------------------------------------------------------------
-- 6. TABLA: Empresa
-- ----------------------------------------------------------------------------
CREATE TABLE Empresa (
    id_empresa INT IDENTITY(1,1) PRIMARY KEY,
    razon_social VARCHAR(150) NOT NULL,
    sector_economico VARCHAR(50),
);

-- ----------------------------------------------------------------------------
-- 7. TABLA: Periodo_Seguimiento
-- ----------------------------------------------------------------------------
CREATE TABLE Periodo_Seguimiento (
    id_periodo INT IDENTITY(1,1) PRIMARY KEY,
    nombre_periodo VARCHAR(50) NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL
);

-- ----------------------------------------------------------------------------
-- 8. TABLA: Historico_Egresado
-- ----------------------------------------------------------------------------
CREATE TABLE Historico_Egresado (
    id_historico INT IDENTITY(1,1) PRIMARY KEY,
    id_egresado INT NOT NULL,
    id_periodo INT NOT NULL,
    id_empresa INT NULL,
    ciudad_residencia VARCHAR(100),
    condicion_trabajo VARCHAR(50) NOT NULL,
    area_cargo VARCHAR(100),
    tipo_contrato VARCHAR(50),
    ingreso_mensual FLOAT NULL,
    fecha_encuesta DATETIME DEFAULT GETDATE(),
    CONSTRAINT FK_Historico_Egresado FOREIGN KEY (id_egresado) REFERENCES Egresado(id_egresado),
    CONSTRAINT FK_Historico_Periodo FOREIGN KEY (id_periodo) REFERENCES Periodo_Seguimiento(id_periodo),
    CONSTRAINT FK_Historico_Empresa FOREIGN KEY (id_empresa) REFERENCES Empresa(id_empresa)
);
GO

-- ============================================================================
-- VISTAS ANAL�TICAS PARA LOS KPIS DEL DASHBOARD
-- ============================================================================

-- VISTA 1: KPI DE EMPLEABILIDAD
GO
CREATE VIEW vw_KPI_Empleabilidad AS
SELECT 
    c.nombre_carrera,
    c.facultad,
    ps.nombre_periodo,
    h.condicion_trabajo,
    COUNT(h.id_historico) AS cantidad_egresados,
    ROUND(
        (COUNT(h.id_historico) * 100.0) / SUM(COUNT(h.id_historico)) OVER (PARTITION BY c.id_carrera, ps.id_periodo), 
        2
    ) AS porcentaje_empleabilidad
FROM Historico_Egresado h
INNER JOIN Egresado e ON h.id_egresado = e.id_egresado
INNER JOIN Carrera c ON e.id_carrera = c.id_carrera
INNER JOIN Periodo_Seguimiento ps ON h.id_periodo = ps.id_periodo
GROUP BY c.id_carrera, c.nombre_carrera, c.facultad, ps.id_periodo, ps.nombre_periodo, h.condicion_trabajo;
GO

-- VISTA 2: KPI DE INGRESO PROMEDIO
CREATE VIEW vw_KPI_IngresoPromedio AS
SELECT 
    c.nombre_carrera,
    c.facultad,
    ps.nombre_periodo,
    h.condicion_trabajo,
    h.area_cargo,
    COUNT(h.id_historico) AS egresados_con_ingreso,
    ROUND(AVG(h.ingreso_mensual), 2) AS ingreso_promedio,
    ROUND(MIN(h.ingreso_mensual), 2) AS ingreso_minimo,
    ROUND(MAX(h.ingreso_mensual), 2) AS ingreso_maximo
FROM Historico_Egresado h
INNER JOIN Egresado e ON h.id_egresado = e.id_egresado
INNER JOIN Carrera c ON e.id_carrera = c.id_carrera
INNER JOIN Periodo_Seguimiento ps ON h.id_periodo = ps.id_periodo
WHERE h.ingreso_mensual IS NOT NULL AND h.ingreso_mensual > 0
GROUP BY c.nombre_carrera, c.facultad, ps.nombre_periodo, h.condicion_trabajo, h.area_cargo;
GO

-- ----------------------------------------------------------------------------
-- REGISTROS INICIALES DE CONFIGURACI�N
-- ----------------------------------------------------------------------------
INSERT INTO Rol (nombre_rol) VALUES ('Administrador'), ('Usuario');

INSERT INTO Usuario (id_rol, username, password_hash, nombre_completo, email, estado) VALUES 
(1, 'admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'Administrador General', 'admin@plategre.edu.pe', 1);
GO