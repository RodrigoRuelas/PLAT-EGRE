import os
import pyodbc
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

class DatabaseConfig:
    """
    Clase encargada de la configuración y proveimiento de conexiones
    hacia la base de datos SQL Server para el sistema PLAT-EGRE.
    """
    SERVER: str = os.getenv("DB_SERVER", r".\SQLEXPRESS")
    DATABASE: str = os.getenv("DB_NAME", "PLAT_EGRE_DB")
    DRIVER: str = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    
    TRUSTED_CONNECTION: str = os.getenv("DB_TRUSTED", "yes")
    USERNAME: str = os.getenv("DB_USER", "")
    PASSWORD: str = os.getenv("DB_PASS", "")

    @classmethod
    def get_connection_string(cls) -> str:
        """Construye la cadena de conexión ODBC estándar."""
        if cls.TRUSTED_CONNECTION.lower() == "yes":
            return (
                f"DRIVER={{{cls.DRIVER}}};"
                f"SERVER={cls.SERVER};"
                f"DATABASE={cls.DATABASE};"
                f"Trusted_Connection=yes;"
            )
        else:
            return (
                f"DRIVER={{{cls.DRIVER}}};"
                f"SERVER={cls.SERVER};"
                f"DATABASE={cls.DATABASE};"
                f"UID={cls.USERNAME};"
                f"PWD={cls.PASSWORD};"
            )

    @classmethod
    def get_pyodbc_connection(cls) -> pyodbc.Connection:
        """Retorna un objeto de conexión nativo pyodbc para consultas directas."""
        try:
            connection_str = cls.get_connection_string()
            conn = pyodbc.connect(connection_str)
            return conn
        except pyodbc.Error as e:
            raise ConnectionError(f"Error al conectar con SQL Server (pyodbc): {e}")

    @classmethod
    def get_sqlalchemy_engine(cls) -> Engine:
        """Retorna un motor de SQLAlchemy configurado para pandas y cargas masivas."""
        try:
            if cls.TRUSTED_CONNECTION.lower() == "yes":
                connection_url = (
                    f"mssql+pyodbc://@{cls.SERVER}/{cls.DATABASE}"
                    f"?driver={cls.DRIVER.replace(' ', '+')}&trusted_connection=yes"
                )
            else:
                connection_url = (
                    f"mssql+pyodbc://{cls.USERNAME}:{cls.PASSWORD}@{cls.SERVER}/{cls.DATABASE}"
                    f"?driver={cls.DRIVER.replace(' ', '+')}"
                )
            
            engine = create_engine(connection_url, fast_executemany=True)
            return engine
        except Exception as e:
            raise ConnectionError(f"Error al crear motor SQLAlchemy: {e}")


if __name__ == "__main__":
    try:
        conn = DatabaseConfig.get_pyodbc_connection()
        print("✅ Conexión exitosa a SQL Server con pyodbc.")
        conn.close()
    except Exception as err:
        print(f"❌ Error de conexión: {err}")