import hashlib
from config.database import DatabaseConfig

class AuthService:
    """
    Servicio encargado de la gestión de usuarios, autenticación
    y validación de permisos en la base de datos SQL Server.
    """
    def __init__(self):
        self.sesion_activa: bool = False
        self._usuario_actual: str = ""
        self._rol_actual: str = ""

    def conectar_db(self) -> bool:
        """Verifica la conectividad con la base de datos SQL Server."""
        try:
            conn = DatabaseConfig.get_pyodbc_connection()
            conn.close()
            return True
        except Exception as e:
            print(f"[AuthService] Error de conexión DB: {e}")
            return False

    def _hash_password(self, pwd: str) -> str:
        """Método privado auxiliar para encriptar contraseñas en SHA-256."""
        return hashlib.sha256(pwd.encode('utf-8')).hexdigest()

    def autenticar(self, usr: str, pwd: str) -> bool:
        """
        Valida las credenciales ingresadas contra la tabla Usuario de SQL Server.
        """
        if not self.conectar_db():
            return False

        try:
            conn = DatabaseConfig.get_pyodbc_connection()
            cursor = conn.cursor()
            pwd_hashed = self._hash_password(pwd)

            cursor.execute("""
                SELECT id_usuario, rol 
                FROM Usuario 
                WHERE username = ? AND password_hash = ? AND estado = 'ACTIVO'
            """, (usr.strip(), pwd_hashed))
            
            row = cursor.fetchone()
            cursor.close()
            conn.close()

            if row:
                self.sesion_activa = True
                self._usuario_actual = usr
                self._rol_actual = row[1]
                return True
            else:
                self.sesion_activa = False
                return False

        except Exception as e:
            print(f"[AuthService] Error durante autenticación: {e}")
            self.sesion_activa = False
            return False

    def validar_permisos(self, rol: str) -> bool:
        """Verifica si el rol de la sesión activa tiene permisos concedidos."""
        if not self.sesion_activa:
            return False
        return self._rol_actual.upper() == rol.upper()

    def registrar_usuario(self, datos: dict) -> bool:
        """Registra un nuevo usuario en la base de datos SQL Server."""
        try:
            conn = DatabaseConfig.get_pyodbc_connection()
            cursor = conn.cursor()
            pwd_hashed = self._hash_password(datos.get("password", ""))

            cursor.execute("""
                INSERT INTO Usuario (username, password_hash, rol, email, estado)
                VALUES (?, ?, ?, ?, 'ACTIVO')
            """, (
                datos.get("username", "").strip(),
                pwd_hashed,
                datos.get("rol", "Usuario"),
                datos.get("email", "").strip()
            ))

            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"[AuthService] Error al registrar usuario: {e}")
            return False