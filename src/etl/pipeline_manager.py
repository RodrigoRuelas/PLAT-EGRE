from src.etl.auditor import ServicioAuditoria
from src.etl.extractor import ExtractorExcel
from src.etl.transformer import ValidadorTransformador
from src.etl.loader import CargadorBD

class ETLPipelineManager:
    def __init__(self, ruta_archivo: str = ""):
        self.ruta_archivo: str = ruta_archivo
        self.estado_ejecucion: str = "PENDIENTE"
        
        # Instanciación según Diagrama de Clases
        self.auditor = ServicioAuditoria()
        self.extractor = ExtractorExcel()
        self.transformador = ValidadorTransformador()
        self.cargador = CargadorBD()

    def ejecutar_pipeline(self, ruta: str) -> bool:
        self.ruta_archivo = ruta
        self.auditor.iniciar_cronometro()

        try:
            self.auditor.registrar_evento(f"Inicio de procesamiento: {ruta}")

            # 1. Extracción e Identificación
            df_raw = self.extractor.cargar_archivo(ruta)
            self.extractor.validar_estructura(df_raw)
            tipo_tabla = self.extractor.identificar_tipo_archivo(ruta)
            self.auditor.registrar_evento(f"Tipo de archivo identificado: {tipo_tabla}")

            total_leidos = len(df_raw)

            # Detección de inconsistencias antes de la limpieza (celdas vacías o con espacios redundantes)
            inconsistencias_detectadas = int(
                df_raw.isna().sum().sum() +
                df_raw.apply(
                    lambda col: col.astype(str).str.strip().ne(col.astype(str)).sum()
                    if col.dtype == "object" else 0
                ).sum()
            )

            # 2. Transformación y Limpieza
            df_norm = self.transformador.normalizar_textos(df_raw)
            df_clean = self.transformador.convertir_vacios_null(df_norm)
            atributos_corregidos = inconsistencias_detectadas

            # 3. Carga en Base de Datos
            self.cargador.conectar_bd()
            self.cargador.ejecutar_upsert(df_clean, tipo_tabla)

            registros_exitosos = len(df_clean)
            self.estado_ejecucion = "EXITOSO"
            self.auditor.registrar_evento(f"Carga finalizada con éxito en {tipo_tabla}.")

            # 4. Registro de Métricas de Auditoría (ET, TEI, TTI)
            self.auditor.registrar_metricas_carga(
                nombre_archivo=ruta,
                total_leidos=total_leidos,
                registros_exitosos=registros_exitosos,
                inconsistencias_detectadas=inconsistencias_detectadas,
                atributos_corregidos=atributos_corregidos
            )
            return True

        except Exception as err:
            self.estado_ejecucion = "ERROR"
            self.auditor.registrar_error(f"Fallo en el pipeline ETL: {str(err)}")
            return False

    def obtener_resumen_ejecucion(self) -> str:
        return f"Estado de Pipeline: {self.estado_ejecucion}"