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
        try:
            self.auditor.registrar_evento(f"Inicio de procesamiento: {ruta}")

            # 1. Extracción e Identificación
            df_raw = self.extractor.cargar_archivo(ruta)
            self.extractor.validar_estructura(df_raw)
            tipo_tabla = self.extractor.identificar_tipo_archivo(ruta)
            self.auditor.registrar_evento(f"Tipo de archivo identificado: {tipo_tabla}")

            self.estado_ejecucion = "EXITOSO"
            self.auditor.registrar_evento(f"Carga finalizada con éxito en {tipo_tabla}.")
            return True

        except Exception as err:
            self.estado_ejecucion = "ERROR"
            self.auditor.registrar_error(f"Fallo en el pipeline ETL: {str(err)}")
            return False

    def obtener_resumen_ejecucion(self) -> str:
        return f"Estado de Pipeline: {self.estado_ejecucion}"