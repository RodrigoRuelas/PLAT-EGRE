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

    def identificar_tipo_archivo(self, origen) -> str:
        # Si recibe la ruta en texto (str), lee las columnas del Excel; si ya es DataFrame, lo usa directo
        if isinstance(origen, str):
            df = pd.read_excel(origen, nrows=1)
        else:
            df = origen

        cols_lower = [str(c).strip().lower() for c in df.columns]

        # 1. Evaluar PRIMERO las columnas exclusivas de Histórico Laboral
        if any("condición" in c or "condicion" in c or "ingreso" in c for c in cols_lower):
            return "Historico"

        # 2. Evaluar DESPUÉS el padrón maestro de Egresados
        if any("dni" in c or "año egres" in c or "anio_egreso" in c for c in cols_lower):
            return "Egresados"

        raise ValueError("Estructura de columnas no reconocida para Egresados ni Histórico.")