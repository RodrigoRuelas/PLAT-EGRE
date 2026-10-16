import pandas as pd
from config.database import DatabaseConfig

class CargadorBD:
    def __init__(self):
        self.cadena_conexion: str = DatabaseConfig.get_connection_string()
        self.nombre_tabla: str = ""

    def conectar_bd(self) -> bool:
        try:
            conn = DatabaseConfig.get_pyodbc_connection()
            conn.close()
            return True
        except Exception as e:
            raise ConnectionError(f"Error de conexión con la base de datos: {e}")

    def ejecutar_upsert(self, datos: pd.DataFrame, tipo_tabla: str) -> None:
        self.nombre_tabla = "Egresado" if tipo_tabla == "Egresados" else "Historico_Egresado"
        conn = DatabaseConfig.get_pyodbc_connection()
        cursor = conn.cursor()

        if tipo_tabla == "Egresados":
            self._cargar_egresados(cursor, datos)
        else:
            self._cargar_historico(cursor, datos)

        conn.commit()
        cursor.close()
        conn.close()

    # Métodos privados auxiliares para resolución de llaves foráneas
    def _obtener_o_crear_carrera(self, cursor, nombre_carrera: str) -> int:
        nombre_clean = str(nombre_carrera).strip() if nombre_carrera else "General"
        cursor.execute("SELECT id_carrera FROM Carrera WHERE LOWER(nombre_carrera) = LOWER(?)", (nombre_clean,))
        row = cursor.fetchone()
        if row:
            return row[0]
        cursor.execute("INSERT INTO Carrera (nombre_carrera, facultad) VALUES (?, ?)", (nombre_clean, "General"))
        cursor.execute("SELECT @@IDENTITY")
        return cursor.fetchone()[0]

    def _obtener_o_crear_empresa(self, cursor, razon_social: str) -> int:
        if not razon_social or str(razon_social).strip() in ["", "None"]:
            return None
        empresa_clean = str(razon_social).strip()
        cursor.execute("SELECT id_empresa FROM Empresa WHERE LOWER(razon_social) = LOWER(?)", (empresa_clean,))
        row = cursor.fetchone()
        if row:
            return row[0]
        cursor.execute("INSERT INTO Empresa (razon_social, sector_economico) VALUES (?, ?)", (empresa_clean, "Privado"))
        cursor.execute("SELECT @@IDENTITY")
        return cursor.fetchone()[0]

    def _obtener_id_egresado(self, cursor, nom_egresado: str) -> int:
        if not nom_egresado or str(nom_egresado).strip() in ["", "None"]:
            return None
        cursor.execute("SELECT id_egresado FROM Egresado WHERE LOWER(nom_egresado) LIKE LOWER(?)", (f"%{str(nom_egresado).strip()}%",))
        row = cursor.fetchone()
        return row[0] if row else None

    def _cargar_egresados(self, cursor, df: pd.DataFrame) -> None:
        for _, row in df.iterrows():
            # Mapeo dinámico por columnas
            dni = next((str(row[c]) for c in df.columns if "dni" in str(c).lower() or "carnet" in str(c).lower()), "00000000")
            nombre = next((str(row[c]) for c in df.columns if "apellidos" in str(c).lower() or "nombre" in str(c).lower()), "Sin Nombre")
            sexo = next((str(row[c]) for c in df.columns if "sexo" in str(c).lower()), "No especificado")
            celular = next((str(row[c]) for c in df.columns if "celular" in str(c).lower()), "")
            email = next((str(row[c]) for c in df.columns if "email" in str(c).lower() or "correo" in str(c).lower()), "")
            carrera_txt = next((str(row[c]) for c in df.columns if "carrera" in str(c).lower()), "General")
            anio = next((int(row[c]) for c in df.columns if "año" in str(c).lower() and str(row[c]).isdigit()), 2026)

            id_carrera = self._obtener_o_crear_carrera(cursor, carrera_txt)

            cursor.execute("""
                IF NOT EXISTS (SELECT 1 FROM Egresado WHERE codigo_dni = ?)
                BEGIN
                    INSERT INTO Egresado (id_carrera, codigo_dni, nom_egresado, sexo, celular, email_profesional, anio_egreso, fecha_registro)
                    VALUES (?, ?, ?, ?, ?, ?, ?, GETDATE())
                END
            """, (dni, id_carrera, dni, nombre, sexo, celular, email, anio))

    def _cargar_historico(self, cursor, df: pd.DataFrame) -> None:
        for _, row in df.iterrows():
            nombre_egresado = next((str(row[c]) for c in df.columns if "apellidos" in str(c).lower()), "")
            id_egresado = self._obtener_id_egresado(cursor, nombre_egresado)

            if id_egresado:
                empresa_txt = next((str(row[c]) for c in df.columns if "empresa" in str(c).lower()), "")
                id_empresa = self._obtener_o_crear_empresa(cursor, empresa_txt)

                ciudad = next((str(row[c]) for c in df.columns if "ciudad" in str(c).lower()), "Arequipa")
                condicion = next((str(row[c]) for c in df.columns if "condición" in str(c).lower()), "Empleado")
                cargo = next((str(row[c]) for c in df.columns if "cargo" in str(c).lower()), "No especificado")
                contrato = next((str(row[c]) for c in df.columns if "contrato" in str(c).lower()), "Indefinido")
                ingreso = next((row[c] for c in df.columns if "ingreso" in str(c).lower() or "monto" in str(c).lower()), None)
                afinidad = next((str(row[c]) for c in df.columns if "relacionado" in str(c).lower()), "Media")
                satisfaccion = next((str(row[c]) for c in df.columns if "satisfecho" in str(c).lower()), "Satisfecho")

                cursor.execute("""
                    INSERT INTO Historico_Egresado (
                        id_egresado, id_periodo, id_empresa, ciudad_residencia, 
                        condicion_trabajo, area_cargo, tipo_contrato, ingreso_mensual, 
                        nivel_afinidad_carrera, satisfaccion_empleabilidad, fecha_encuesta
                    ) VALUES (?, 1, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
                """, (id_egresado, id_empresa, ciudad, condicion, cargo, contrato, ingreso, afinidad, satisfaccion))