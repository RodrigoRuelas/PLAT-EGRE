import customtkinter as ctk
from tkinter import filedialog, messagebox
from src.etl.pipeline_manager import ETLPipelineManager
from src.ui.dashboard_view import DashboardView

class PlataformaRegistros(ctk.CTk):
    """
    Ventana principal del sistema PLAT-EGRE que orquesta la navegación 
    entre la ingesta de archivos (ETL) y la visualización del Dashboard.
    """
    def __init__(self, usuario_actual: str = "Admin"):
        super().__init__()

        self.usuario_actual: str = usuario_actual
        self.estado_vista: str = "DASHBOARD"
        self.pipeline_manager = ETLPipelineManager()

        self.title(f"PLAT-EGRE | Usuario: {self.usuario_actual}")
        self.geometry("1000x650")

        self._construir_menu_lateral()

    def _construir_menu_lateral(self):
        # Sidebar Navigation
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        self.lbl_logo = ctk.CTkLabel(self.sidebar, text="PLAT-EGRE", font=("Roboto", 20, "bold"))
        self.lbl_logo.pack(pady=20, padx=20)

        self.btn_cargar = ctk.CTkButton(self.sidebar, text="Subir Excel (ETL)", command=self.seleccionar_archivo)
        self.btn_cargar.pack(pady=10, padx=20)

        self.btn_dash = ctk.CTkButton(self.sidebar, text="Dashboard Analítico", command=self.actualizar_dashboard)
        self.btn_dash.pack(pady=10, padx=20)

        # Contenedor Principal Vista
        self.container = ctk.CTkFrame(self)
        self.container.pack(side="right", fill="both", expand=True)

        self.dashboard_view = DashboardView(self.container)
        self.dashboard_view.pack(fill="both", expand=True)

    def seleccionar_archivo(self) -> str:
        """Abre un diálogo de selección para cargar un archivo Excel/CSV en el Motor ETL-AS."""
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo de Egresados o Histórico",
            filetypes=[("Archivos Excel / CSV", "*.xlsx *.xls *.csv")]
        )
        if ruta:
            exito = self.pipeline_manager.ejecutar_pipeline(ruta)
            if exito:
                self.mostrar_mensaje("Archivo procesado e inyectado con éxito a SQL Server.")
                self.actualizar_dashboard()
            else:
                self.mostrar_mensaje("Ocurrió un error al procesar el archivo. Verifique el Log.")
        return ruta

    def mostrar_mensaje(self, msg: str) -> None:
        """Muestra una caja emergente con el resultado de la operación."""
        messagebox.showinfo("PLAT-EGRE | Notificación", msg)

    def actualizar_dashboard(self) -> None:
        """Refresca los gráficos y KPIs del Dashboard Analítico."""
        self.dashboard_view.aplicar_filtros_busqueda()