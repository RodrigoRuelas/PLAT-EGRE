import customtkinter as ctk
from src.services.auth_service import AuthService

class LoginView(ctk.CTk):
    """
    Interfaz gráfica de inicio de sesión implementada con CustomTkinter.
    """
    def __init__(self, callback_exito=None):
        super().__init__()

        # Configuración de ventana
        self.title("PLAT-EGRE | Inicio de Sesión")
        self.geometry("400x500")
        self.resizable(False, False)
        
        self.callback_exito = callback_exito
        self.auth_service = AuthService()

        # Atributos de entradas
        self.txt_usuario: str = ""
        self.txt_password: str = ""

        # Inicializar interfaz
        self.renderizar()

    def renderizar(self) -> None:
        """Construye y posiciona los elementos visuales en la ventana."""
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # Frame principal
        self.frame = ctk.CTkFrame(self, corner_radius=15)
        self.frame.pack(pady=30, padx=30, fill="both", expand=True)

        # Título
        self.lbl_titulo = ctk.CTkLabel(
            self.frame, text="PLAT-EGRE", font=("Roboto", 24, "bold")
        )
        self.lbl_titulo.pack(pady=(20, 5))

        self.lbl_subtitulo = ctk.CTkLabel(
            self.frame, text="Observatorio de Empleabilidad", font=("Roboto", 12)
        )
        self.lbl_subtitulo.pack(pady=(0, 20))

        # Input Usuario
        self.entry_usuario = ctk.CTkEntry(
            self.frame, placeholder_text="Usuario", width=260, height=40
        )
        self.entry_usuario.pack(pady=10)

        # Input Contraseña
        self.entry_password = ctk.CTkEntry(
            self.frame, placeholder_text="Contraseña", show="*", width=260, height=40
        )
        self.entry_password.pack(pady=10)

        # Etiqueta de Error
        self.lbl_error = ctk.CTkLabel(
            self.frame, text="", text_color="red", font=("Roboto", 11)
        )
        self.lbl_error.pack(pady=5)

        # Botón Iniciar Sesión
        self.btn_login = ctk.CTkButton(
            self.frame, text="Iniciar Sesión", width=260, height=40, command=self._ejecutar_login
        )
        self.btn_login.pack(pady=15)

    def capturas_credenciales(self) -> dict:
        """Obtiene el contenido actual de los campos de texto."""
        self.txt_usuario = self.entry_usuario.get().strip()
        self.txt_password = self.entry_password.get().strip()
        return {"usuario": self.txt_usuario, "password": self.txt_password}

    def mostrar_error(self, msg: str) -> None:
        """Muestra un mensaje de advertencia o error en la interfaz."""
        self.lbl_error.configure(text=msg)

    def solicitar_registro(self) -> None:
        """Abre la ventana modal o formulario de registro de nuevos usuarios."""
        pass

    def capturas_datos_registros(self) -> dict:
        """Captura datos para la creación de un nuevo usuario."""
        return {}

    def _ejecutar_login(self) -> None:
        """Maneja el evento del botón de inicio de sesión."""
        credenciales = self.capturas_credenciales()
        
        if not credenciales["usuario"] or not credenciales["password"]:
            self.mostrar_error("Por favor complete todos los campos.")
            return

        if self.auth_service.autenticar(credenciales["usuario"], credenciales["password"]):
            self.mostrar_error("")
            if self.callback_exito:
                self.callback_exito(credenciales["usuario"])
            self.destroy()
        else:
            self.mostrar_error("Credenciales incorrectas o usuario inactivo.")