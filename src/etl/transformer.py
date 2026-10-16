import pandas as pd
import numpy as np
import re

class ValidadorTransformador:
    def __init__(self):
        self.reglas_limpieza: list = ["strip", "extract_numeric", "convert_nulls"]

    def normalizar_textos(self, datos: pd.DataFrame) -> pd.DataFrame:
        df = datos.copy()
        
        # Mapeo y limpieza de texto estándar
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).str.strip()

        # Si el DataFrame contiene columnas de ingreso, aplica extracción numérica
        for col in df.columns:
            if "ingreso" in str(col).lower() or "monto" in str(col).lower():
                df[col] = df[col].apply(self._extraer_monto)

        return df

    def convertir_vacios_null(self, datos: pd.DataFrame) -> pd.DataFrame:
        df = datos.replace(
            to_replace=r'^(?i)(nan|none|null|n/a|\s*)$', 
            value=np.nan, 
            regex=True
        )
        return df.where(pd.notnull(df), None)

    # Método auxiliar privado (no afecta la firma UML pública)
    def _extraer_monto(self, valor) -> float:
        if pd.isna(valor) or str(valor).strip() in ["", "None", "nan"]:
            return None
        match = re.search(r'(\d+[\.,]?\d*)', str(valor))
        if match:
            return float(match.group(1).replace(',', '.'))
        return None