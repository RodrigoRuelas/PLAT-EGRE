import pandas as pd
import numpy as np
import re

class ValidadorTransformador:
    def __init__(self):
        self.reglas_limpieza: list = ["strip", "extract_numeric", "convert_nulls"]

    def normalizar_textos(self, datos: pd.DataFrame) -> pd.DataFrame:
        df = datos.copy()
        
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).str.strip()

        for col in df.columns:
            if "ingreso" in str(col).lower() or "monto" in str(col).lower():
                df[col] = df[col].apply(self._extraer_monto)

        return df

    def convertir_vacios_null(self, datos: pd.DataFrame) -> pd.DataFrame:
        """Sustituye cadenas vacías, 'nan', 'none' o 'null' por None (SQL NULL)."""
        df = datos.copy()
        
        # Regex corregida compatible con Python 3.11+
        patron_vacios = r'^(nan|none|null|n/a|\s*)$'
        
        # Se aplica reemplazo sin banderas embebidas problemáticas
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).apply(
                    lambda x: None if re.match(patron_vacios, x.strip(), re.IGNORECASE) else x
                )

        return df

    def _extraer_monto(self, valor) -> float:
        if pd.isna(valor) or str(valor).strip() in ["", "None", "nan"]:
            return None
        match = re.search(r'(\d+[\.,]?\d*)', str(valor))
        if match:
            return float(match.group(1).replace(',', '.'))
        return None