import pandas as pd
from config.database import DatabaseConfig

class DashboardAnalyticsService:
    """
    Servicio encargado de ejecutar consultas parametrizadas sobre las vistas analíticas
    en SQL Server y calcular los indicadores clave (KPIs) de empleabilidad.
    """
    def __init__(self):
        self.kpi_empleabilidad: float = 0.0
        self.kpi_ingreso_promedio: float = 0.0

    def conectar_db(self) -> bool:
        """Verifica la conectividad con la base de datos SQL Server."""
        try:
            conn = DatabaseConfig.get_pyodbc_connection()
            conn.close()
            return True
        except Exception as e:
            print(f"[DashboardAnalyticsService] Error de conexión DB: {e}")
            return False

    def calcular_tasa_empleo(self, filtros: dict) -> float:
        """Calcula el porcentaje de egresados empleados según los filtros aplicados."""
        if not self.conectar_db():
            return 0.0

        try:
            conn = DatabaseConfig.get_pyodbc_connection()
            query = "SELECT condicion_trabajo, cantidad_egresados FROM vw_KPI_Empleabilidad WHERE 1=1"
            params = []

            if filtros.get("carrera") and filtros["carrera"] != "Todas":
                query += " AND nombre_carrera = ?"
                params.append(filtros["carrera"])

            df = pd.read_sql(query, conn, params=params)
            conn.close()

            if df.empty:
                self.kpi_empleabilidad = 0.0
                return 0.0

            total = df["cantidad_egresados"].sum()
            empleados = df[df["condicion_trabajo"].str.lower().str.contains("empleado|dependiente|independiente", na=False)]["cantidad_egresados"].sum()

            self.kpi_empleabilidad = round((empleados / total) * 100, 2) if total > 0 else 0.0
            return self.kpi_empleabilidad
        except Exception as e:
            print(f"[DashboardAnalyticsService] Error al calcular tasa de empleo: {e}")
            return 0.0

    def obtener_prom_salarial(self, filtros: dict) -> float:
        """Obtiene el ingreso promedio global o filtrado por carrera."""
        if not self.conectar_db():
            return 0.0

        try:
            conn = DatabaseConfig.get_pyodbc_connection()
            query = "SELECT ingreso_promedio, egresados_con_ingreso FROM vw_KPI_IngresoPromedio WHERE 1=1"
            params = []

            if filtros.get("carrera") and filtros["carrera"] != "Todas":
                query += " AND nombre_carrera = ?"
                params.append(filtros["carrera"])

            df = pd.read_sql(query, conn, params=params)
            conn.close()

            if df.empty:
                self.kpi_ingreso_promedio = 0.0
                return 0.0

            promedio_ponderado = (df["ingreso_promedio"] * df["egresados_con_ingreso"]).sum() / df["egresados_con_ingreso"].sum()
            self.kpi_ingreso_promedio = round(promedio_ponderado, 2)
            return self.kpi_ingreso_promedio
        except Exception as e:
            print(f"[DashboardAnalyticsService] Error al obtener ingreso promedio: {e}")
            return 0.0

    def filtrar_datos_observatorio(self) -> list:
        """Retorna el listado de registros consolidados para poblar las tablas."""
        if not self.conectar_db():
            return []

        try:
            conn = DatabaseConfig.get_pyodbc_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT TOP 100 e.nom_egresado, c.nombre_carrera, h.condicion_trabajo, h.area_cargo, h.ingreso_mensual
                FROM Egresado e
                INNER JOIN Carrera c ON e.id_carrera = c.id_carrera
                LEFT JOIN Historico_Egresado h ON e.id_egresado = h.id_egresado
            """)
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            return [list(row) for row in rows]
        except Exception as e:
            print(f"[DashboardAnalyticsService] Error al filtrar datos: {e}")
            return []

    def obtener_historico(self) -> list:
        """Obtiene el historial completo de encuestas de seguimiento."""
        if not self.conectar_db():
            return []

        try:
            conn = DatabaseConfig.get_pyodbc_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT h.id_historico, e.nom_egresado, h.ciudad_residencia, h.condicion_trabajo, h.ingreso_mensual, h.fecha_encuesta
                FROM Historico_Egresado h
                INNER JOIN Egresado e ON h.id_egresado = e.id_egresado
            """)
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            return [list(row) for row in rows]
        except Exception as e:
            print(f"[DashboardAnalyticsService] Error al obtener histórico: {e}")
            return []