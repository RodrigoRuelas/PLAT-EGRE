import pandas as pd
import numpy as np
import re


class ValidadorTransformador:
    """
    Clase encargada de la limpieza, normalización y transformación de datos
    en memoria previa a la ingesta en SQL Server.
    """

    def normalizar_textos(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normaliza las cadenas de texto aplicando strip a los extremos y
        extrae los montos numéricos limpios (float) de columnas monetarias.
        """
        df = df.copy()

        # 1. Recorte estricto de espacios laterales (strip) usando métodos vectorizados de Pandas
        for col in df.columns:
            if df[col].dtype == 'object' or pd.api.types.is_string_dtype(df[col]):
                df[col] = df[col].astype(str).str.strip()

        # 2. Limpieza y conversión de montos numéricos (ejemplo: "S/. 3,500.50" -> 3500.50)
        if "Ingreso_Mensual" in df.columns:
            def extraer_monto_float(val):
                if pd.isna(val) or val is None or str(val).strip().lower() in ['none', 'nan', 'null', '']:
                    return None
                
                val_str = str(val).strip()
                # Eliminar símbolos de moneda (S/., S/, $)
                val_str = re.sub(r'^[S\/\$\s\.]+', '', val_str).strip()
                # Eliminar comas de millares
                val_str = val_str.replace(',', '')
                
                try:
                    return float(val_str)
                except ValueError:
                    return None

            df["Ingreso_Mensual"] = df["Ingreso_Mensual"].apply(extraer_monto_float)

        return df

    def convertir_vacios_null(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Identifica representaciones sintácticas de vacíos ("N/A", "nan", "null", "   ")
        y las sustituye por el objeto None (SQL NULL), asegurando que np.nan cambie a None.
        """
        df = df.copy()

        # Conjunto de representaciones de valores nulos o vacíos
        patrones_vacios = {
            'N/A', 'n/a', 'Na', 'NA', 
            'NULL', 'null', 'Null', 
            'NAN', 'nan', 'NaN', 
            'NONE', 'none', 'None', 
            '', '   '
        }

        # 1. Limpieza de cadenas de texto y evaluación de patrones nulos
        for col in df.columns:
            df[col] = df[col].apply(
                lambda x: None if pd.isna(x) or (isinstance(x, str) and x.strip() in patrones_vacios) else x
            )

        # 2. Conversión final de cualquier objeto np.nan a None puro para compatibilidad SQL / assertIsNone
        df = df.astype(object).where(pd.notnull(df), None)

        return df