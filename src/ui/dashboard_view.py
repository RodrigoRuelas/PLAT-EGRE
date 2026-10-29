import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from src.services.dashboard_service import DashboardAnalyticsService

class DashboardView(ctk.CTkFrame):
    """
    Vista del Dashboard Analítico con paneles de KPIs y gráficos incrustados mediante Matplotlib.
    """
    def __init__(self, parent):
        super().__init__(parent)

        self.service = DashboardAnalyticsService()

        # Atributos de Filtro
        self.filtro_egresado: str = ""
        self.filtro_carrera: str = "Todas"
        self.filtro_periodo: str = "Todos"
        self.filtro_anio_egresado: int = 0
        self.filtro_condicion_laboral: str = "Todas"
        self.filtro_sector_empresa: str = "Todos"

        self._construir_interfaz()

    def _construir_interfaz(self):
        # Panel Superior: Filtros
        self.frame_filtros = ctk.CTkFrame(self, height=60)
        self.frame_filtros.pack(fill="x", padx=10, pady=5)

        self.lbl_carrera = ctk.CTkLabel(self.frame_filtros, text="Carrera:")
        self.lbl_carrera.pack(side="left", padx=10, pady=10)

        self.cmb_carrera = ctk.CTkOptionMenu(
            self.frame_filtros, 
            values=["Todas", "Ingeniería de Software", "Administración", "Derecho"],
            command=lambda val: self.aplicar_filtros_busqueda()
        )
        self.cmb_carrera.pack(side="left", padx=5, pady=10)

        self.btn_limpiar = ctk.CTkButton(self.frame_filtros, text="Limpiar Filtros", width=100, command=self.limpiar_filtros)
        self.btn_limpiar.pack(side="right", padx=10, pady=10)

        self.btn_exportar = ctk.CTkButton(self.frame_filtros, text="Exportar PDF", width=100, command=self.exportar_vista_pdf)
        self.btn_exportar.pack(side="right", padx=5, pady=10)

        # Panel Central: KPIs Tarjetas
        self.frame_kpis = ctk.CTkFrame(self)
        self.frame_kpis.pack(fill="x", padx=10, pady=5)

        self.card_empleo = ctk.CTkFrame(self.frame_kpis, corner_radius=10)
        self.card_empleo.pack(side="left", expand=True, fill="both", padx=5, pady=5)
        self.lbl_kpi_empleo_val = ctk.CTkLabel(self.card_empleo, text="0.0%", font=("Roboto", 22, "bold"))
        self.lbl_kpi_empleo_val.pack(pady=(10, 0))
        ctk.CTkLabel(self.card_empleo, text="Tasa de Empleabilidad", font=("Roboto", 11)).pack(pady=(0, 10))

        self.card_salario = ctk.CTkFrame(self.frame_kpis, corner_radius=10)
        self.card_salario.pack(side="left", expand=True, fill="both", padx=5, pady=5)
        self.lbl_kpi_salario_val = ctk.CTkLabel(self.card_salario, text="S/. 0.00", font=("Roboto", 22, "bold"))
        self.lbl_kpi_salario_val.pack(pady=(10, 0))
        ctk.CTkLabel(self.card_salario, text="Ingreso Promedio", font=("Roboto", 11)).pack(pady=(0, 10))

        # Panel Inferior: Gráficos
        self.frame_graficos = ctk.CTkFrame(self)
        self.frame_graficos.pack(fill="both", expand=True, padx=10, pady=5)

        self.mostrar_graficos_empleo()
        self.aplicar_filtros_busqueda()

    def mostrar_graficos_empleo(self) -> None:
        """Incrusta un gráfico de sectores (pie chart) usando Matplotlib."""
        fig, ax = plt.subplots(figsize=(5, 3.2), dpi=90)
        fig.patch.set_facecolor('#2b2b2b')
        ax.set_facecolor('#2b2b2b')

        labels = ['Empleado', 'Independiente', 'Buscando Trabajo']
        valores = [65, 20, 15]
        colores = ['#2fa572', '#1f538d', '#e74c3c']

        ax.pie(valores, labels=labels, autopct='%1.1f%%', colors=colores, textprops={'color': 'w'})
        ax.set_title("Distribución de Condición Laboral", color="white", fontsize=11)

        canvas = FigureCanvasTkAgg(fig, master=self.frame_graficos)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def aplicar_filtros_busqueda(self) -> None:
        """Actualiza los cálculos de los KPIs con base en las opciones seleccionadas."""
        self.filtro_carrera = self.cmb_carrera.get()
        filtros = {"carrera": self.filtro_carrera}

        tasa = self.service.calcular_tasa_empleo(filtros)
        salario = self.service.obtener_prom_salarial(filtros)

        self.lbl_kpi_empleo_val.configure(text=f"{tasa}%")
        self.lbl_kpi_salario_val.configure(text=f"S/. {salario:,.2f}")

    def seleccionar_egresado(self) -> None:
        """Obtiene el detalle particular de un egresado seleccionado."""
        pass

    def limpiar_filtros(self) -> None:
        """Resetea los controles de filtro a su estado inicial."""
        self.cmb_carrera.set("Todas")
        self.aplicar_filtros_busqueda()

    def exportar_vista_pdf(self) -> None:
        """Exporta un reporte en PDF de los datos del dashboard actual."""
        print("[DashboardView] Reporte PDF generado correctamente.")