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
        nombre_clean = str(nombre_carrera).strip() if pd.notna(nombre_carrera) and str(nombre_carrera).strip() else "General"
        cursor.execute("SELECT id_carrera FROM Carrera WHERE LOWER(nombre_carrera) = LOWER(?)", (nombre_clean,))
        row = cursor.fetchone()
        if row:
            return row[0]
        cursor.execute("INSERT INTO Carrera (nombre_carrera, facultad) VALUES (?, ?)", (nombre_clean, "General"))
        cursor.execute("SELECT @@IDENTITY")
        return cursor.fetchone()[0]

    def _obtener_o_crear_empresa(self, cursor, razon_social: str):
        if pd.isna(razon_social) or str(razon_social).strip() in ["", "None", "nan"]:
            return None
        empresa_clean = str(razon_social).strip()
        cursor.execute("SELECT id_empresa FROM Empresa WHERE LOWER(razon_social) = LOWER(?)", (empresa_clean,))
        row = cursor.fetchone()
        if row:
            return row[0]
        cursor.execute("INSERT INTO Empresa (razon_social, sector_economico) VALUES (?, ?)", (empresa_clean, "Privado"))
        cursor.execute("SELECT @@IDENTITY")
        return cursor.fetchone()[0]

    def _obtener_o_crear_periodo(self, cursor, fecha_encuesta: str) -> int:
        anio = str(fecha_encuesta).strip()[:4] if pd.notna(fecha_encuesta) and len(str(fecha_encuesta).strip()) >= 4 else "2026"
        if not anio.isdigit():
            anio = "2026"

        # Busca el periodo que coincida con el año de la encuesta (ej. 2026)
        cursor.execute("SELECT TOP 1 id_periodo FROM Periodo_Seguimiento WHERE nombre_periodo LIKE ?", (f"%{anio}%",))
        row = cursor.fetchone()
        if row:
            return row[0]

        # Si no existe aún en Periodo_Seguimiento, toma el último activo o lo crea automáticamente
        cursor.execute("SELECT TOP 1 id_periodo FROM Periodo_Seguimiento ORDER BY id_periodo DESC")
        row_fallback = cursor.fetchone()
        if row_fallback:
            return row_fallback[0]

        cursor.execute("""
            INSERT INTO Periodo_Seguimiento (nombre_periodo, fecha_inicio, fecha_fin, estado)
            OUTPUT INSERTED.id_periodo
            VALUES (?, ?, ?, 'Activo')
        """, (anio, f"{anio}-01-01", f"{anio}-12-31"))
        return cursor.fetchone()[0]

    def _obtener_id_egresado(self, cursor, dni: str, nom_egresado: str):
        # 1. Búsqueda exacta por DNI (prioritaria)
        if pd.notna(dni) and str(dni).strip() not in ["", "None", "nan"]:
            dni_clean = str(dni).strip().split(".")[0]
            cursor.execute("SELECT id_egresado FROM Egresado WHERE codigo_dni = ?", (dni_clean,))
            row = cursor.fetchone()
            if row:
                return row[0]

        # 2. Búsqueda de respaldo por Nombres y Apellidos
        if pd.notna(nom_egresado) and str(nom_egresado).strip() not in ["", "None", "nan"]:
            cursor.execute("SELECT id_egresado FROM Egresado WHERE LOWER(nom_egresado) LIKE LOWER(?)", (f"%{str(nom_egresado).strip()}%",))
            row = cursor.fetchone()
            return row[0] if row else None

        return None

    def _cargar_egresados(self, cursor, df: pd.DataFrame) -> None:
        for _, row in df.iterrows():
            dni_raw = next((row[c] for c in df.columns if "dni" in str(c).lower() or "carnet" in str(c).lower()), "00000000")
            dni = str(dni_raw).strip().split(".")[0] if pd.notna(dni_raw) else "00000000"

            nombre = next((str(row[c]).strip() for c in df.columns if ("apellidos" in str(c).lower() or "nombre" in str(c).lower()) and pd.notna(row[c])), "Sin Nombre")
            sexo = next((str(row[c]).strip() for c in df.columns if "sexo" in str(c).lower() and pd.notna(row[c])), "No especificado")
            celular_raw = next((row[c] for c in df.columns if ("celular" in str(c).lower() or "teléfono" in str(c).lower() or "telefono" in str(c).lower()) and pd.notna(row[c])), "")
            celular = str(celular_raw).strip().split(".")[0] if celular_raw != "" else ""
            email = next((str(row[c]).strip() for c in df.columns if ("email" in str(c).lower() or "correo" in str(c).lower()) and pd.notna(row[c])), "")
            carrera_txt = next((str(row[c]).strip() for c in df.columns if "carrera" in str(c).lower() and pd.notna(row[c])), "General")

            anio_raw = next((row[c] for c in df.columns if ("año" in str(c).lower() or "anio" in str(c).lower()) and pd.notna(row[c])), 2026)
            try:
                anio = int(float(anio_raw))
            except (ValueError, TypeError):
                anio = 2026

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
            dni_egresado = next((row[c] for c in df.columns if "dni" in str(c).lower()), None)
            nombre_egresado = next((row[c] for c in df.columns if "apellidos" in str(c).lower() or "nombre" in str(c).lower()), "")
            id_egresado = self._obtener_id_egresado(cursor, dni_egresado, nombre_egresado)

            if id_egresado:
                empresa_txt = next((row[c] for c in df.columns if "empresa" in str(c).lower()), None)
                id_empresa = self._obtener_o_crear_empresa(cursor, empresa_txt)

                ciudad = next((str(row[c]).strip() for c in df.columns if "ciudad" in str(c).lower() and pd.notna(row[c])), "Arequipa")
                condicion = next((str(row[c]).strip() for c in df.columns if ("condición" in str(c).lower() or "condicion" in str(c).lower()) and pd.notna(row[c])), "Empleado")
                cargo = next((str(row[c]).strip() for c in df.columns if "cargo" in str(c).lower() and pd.notna(row[c])), "No especificado")
                contrato = next((str(row[c]).strip() for c in df.columns if "contrato" in str(c).lower() and pd.notna(row[c])), "Indefinido")

                ingreso_raw = next((row[c] for c in df.columns if ("ingreso" in str(c).lower() or "monto" in str(c).lower()) and pd.notna(row[c])), None)
                try:
                    ingreso = float(ingreso_raw) if ingreso_raw is not None else None
                except (ValueError, TypeError):
                    ingreso = None

                fecha_raw = next((row[c] for c in df.columns if "fecha" in str(c).lower() and pd.notna(row[c])), "2026-10-15")
                fecha_encuesta = str(fecha_raw).strip()[:10]
                id_periodo = self._obtener_o_crear_periodo(cursor, fecha_encuesta)

                cursor.execute("""
                    INSERT INTO Historico_Egresado (
                        id_egresado, id_periodo, id_empresa, ciudad_residencia, condicion_trabajo, area_cargo, tipo_contrato, ingreso_mensual, fecha_encuesta
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (id_egresado, id_periodo, id_empresa, ciudad, condicion, cargo, contrato, ingreso, fecha_encuesta))