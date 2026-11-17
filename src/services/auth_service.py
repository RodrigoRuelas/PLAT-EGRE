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
        Valida las credenciales ingresadas contra las tablas Usuario y Rol de SQL Server.
        """
        if not self.conectar_db():
            return False

        try:
            conn = DatabaseConfig.get_pyodbc_connection()
            cursor = conn.cursor()
            pwd_hashed = self._hash_password(pwd)

            # Consulta corregida: INNER JOIN con tabla Rol y evaluación de estado BIT (1)
            cursor.execute("""
                SELECT u.id_usuario, r.nombre_rol 
                FROM Usuario u
                INNER JOIN Rol r ON u.id_rol = r.id_rol
                WHERE u.username = ? AND u.password_hash = ? AND u.estado = 1
            """, (usr.strip(), pwd_hashed))
            
            row = cursor.fetchone()
            cursor.close()
            conn.close()

            if row:
                self.sesion_activa = True
                self._usuario_actual = usr.strip()
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
        return self._rol_actual.upper() == rol.strip().upper()

    def registrar_usuario(self, datos: dict) -> bool:
        """
        Registra un nuevo usuario en la base de datos SQL Server resolviendo
        su llave foránea id_rol y almacenando su contraseña encriptada en SHA-256.
        """
        try:
            conn = DatabaseConfig.get_pyodbc_connection()
            cursor = conn.cursor()
            pwd_hashed = self._hash_password(datos.get("password", ""))

            # Resolver id_rol dinámicamente si se envía 'rol' como texto o usar 'id_rol' directo
            id_rol = datos.get("id_rol")
            if not id_rol:
                nombre_rol = datos.get("rol", "Administrador").strip()
                cursor.execute("SELECT id_rol FROM Rol WHERE LOWER(nombre_rol) = LOWER(?)", (nombre_rol,))
                rol_row = cursor.fetchone()
                id_rol = rol_row[0] if rol_row else 1

            cursor.execute("""
                INSERT INTO Usuario (
                    id_rol, username, password_hash, nombre_completo, email, estado, fecha_creacion
                )
                VALUES (?, ?, ?, ?, ?, 1, GETDATE())
            """, (
                id_rol,
                datos.get("username", "").strip(),
                pwd_hashed,
                datos.get("nombre_completo", "Usuario Sistema").strip(),
                datos.get("email", "").strip()
            ))

            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"[AuthService] Error al registrar usuario: {e}")
            return False