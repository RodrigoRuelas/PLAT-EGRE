import pandas as pd

class ExtractorExcel:
    def __init__(self):
        self.hoja_activa: str = "Hoja1"
        self.columnas_requeridas: list = []
        self.tipo_archivo: str = ""

    def cargar_archivo(self, ruta: str) -> pd.DataFrame:
        try:
            if ruta.endswith('.csv'):
                df = pd.read_csv(ruta)
            else:
                df = pd.read_excel(ruta)
            return df
        except Exception as e:
            raise ValueError(f"Error al leer el archivo en {ruta}: {e}")

    def validar_estructura(self, datos: pd.DataFrame = None) -> bool:
        if datos is None or datos.empty:
            raise ValueError("El archivo cargado está vacío o no contiene una estructura válida.")
        return True

    def identificar_tipo_archivo(self, ruta: str) -> str:
        df_preview = pd.read_csv(ruta, nrows=2) if ruta.endswith('.csv') else pd.read_excel(ruta, nrows=2)
        cols_text = " ".join([str(c).lower() for c in df_preview.columns])

        if "dni" in cols_text or "carnet" in cols_text or "qué año egreso" in cols_text:
            self.tipo_archivo = "Egresados"
        elif "condición se encuentra" in cols_text or "ingreso laboral" in cols_text or "3.1 si su respuesta" in cols_text:
            self.tipo_archivo = "Historico"
        else:
            raise ValueError("No se pudo identificar un formato válido (Registro o Histórico).")

        return self.tipo_archivo