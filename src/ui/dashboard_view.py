import customtkinter as ctk
import matplotlib.pyplot as plt
import os
from datetime import datetime
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from src.services.dashboard_service import DashboardAnalyticsService


class DashboardView(ctk.CTkFrame):
    """
    Vista del Dashboard Analítico con paneles de KPIs y gráficos dinámicos mediante Matplotlib.
    """
    def __init__(self, parent):
        super().__init__(parent)

        self.service = DashboardAnalyticsService()
        self.canvas_grafico = None
        self.fig_actual = None

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

        self.btn_limpiar = ctk.CTkButton(
            self.frame_filtros, text="Limpiar Filtros", width=110, command=self.limpiar_filtros
        )
        self.btn_limpiar.pack(side="right", padx=10, pady=10)

        self.btn_exportar = ctk.CTkButton(
            self.frame_filtros, text="Exportar PDF", width=110, command=self.exportar_vista_pdf
        )
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

        # Carga inicial de KPIs y Gráfico desde SQL Server
        self.aplicar_filtros_busqueda()

    def mostrar_graficos_empleo(self, distribucion: dict) -> None:
        """Renderiza o actualiza dinámicamente el gráfico de sectores con los datos de SQL Server."""
        if self.canvas_grafico is not None:
            self.canvas_grafico.get_tk_widget().destroy()
            self.canvas_grafico = None
        if self.fig_actual is not None:
            plt.close(self.fig_actual)

        fig, ax = plt.subplots(figsize=(5.5, 3.4), dpi=90)
        self.fig_actual = fig
        fig.patch.set_facecolor('#2b2b2b')
        ax.set_facecolor('#2b2b2b')

        titulo_carrera = self.filtro_carrera if self.filtro_carrera != "Todas" else "Todas las Carreras"

        if not distribucion:
            ax.text(
                0.5, 0.5,
                f"Sin registros históricos para:\n{titulo_carrera}\n\n(Suba el archivo de Histórico ETL)",
                color="#cccccc", fontsize=11, ha="center", va="center"
            )
            ax.set_xticks([])
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_visible(False)
        else:
            labels = list(distribucion.keys())
            valores = list(distribucion.values())
            paleta = ['#2fa572', '#1f538d', '#e67e22', '#e74c3c', '#9b59b6']
            colores = [paleta[i % len(paleta)] for i in range(len(labels))]

            ax.pie(valores, labels=labels, autopct='%1.1f%%', colors=colores, textprops={'color': 'w'})
            ax.set_title(f"Distribución Laboral — {titulo_carrera}", color="white", fontsize=11, pad=10)

        self.canvas_grafico = FigureCanvasTkAgg(fig, master=self.frame_graficos)
        self.canvas_grafico.draw()
        self.canvas_grafico.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def aplicar_filtros_busqueda(self) -> None:
        """Actualiza los KPIs y el gráfico con base en la carrera seleccionada."""
        self.filtro_carrera = self.cmb_carrera.get()
        filtros = {"carrera": self.filtro_carrera}

        tasa = self.service.calcular_tasa_empleo(filtros)
        salario = self.service.obtener_prom_salarial(filtros)
        distribucion = self.service.obtener_distribucion_condicion(filtros)

        self.lbl_kpi_empleo_val.configure(text=f"{tasa:.2f}%")
        self.lbl_kpi_salario_val.configure(text=f"S/. {salario:,.2f}")
        self.mostrar_graficos_empleo(distribucion)

    def seleccionar_egresado(self) -> None:
        """Obtiene el detalle particular de un egresado seleccionado."""
        pass

    def limpiar_filtros(self) -> None:
        """Resetea los controles de filtro a su estado inicial."""
        self.cmb_carrera.set("Todas")
        self.aplicar_filtros_busqueda()

    def exportar_vista_pdf(self) -> None:
        """Genera un reporte ejecutivo en PDF con KPIs, gráfico y tabla de egresados, y lo abre."""
        carrera_actual = self.cmb_carrera.get()
        nombre_sugerido = f"Reporte_PLATEGRE_{carrera_actual.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"

        ruta_pdf = filedialog.asksaveasfilename(
            title="Guardar Reporte Analítico PDF",
            initialfile=nombre_sugerido,
            defaultextension=".pdf",
            filetypes=[("Documentos PDF", "*.pdf")]
        )

        if not ruta_pdf:
            return

        try:
            filtros = {"carrera": carrera_actual}
            tasa = self.service.calcular_tasa_empleo(filtros)
            salario = self.service.obtener_prom_salarial(filtros)
            distribucion = self.service.obtener_distribucion_condicion(filtros)
            registros = self.service.filtrar_datos_observatorio()

            # Filtrar registros de tabla si hay una carrera específica seleccionada
            if carrera_actual != "Todas":
                registros = [r for r in registros if str(r[1]).strip().lower() == carrera_actual.strip().lower()]

            with PdfPages(ruta_pdf) as pdf:
                # Crear lienzo tamaño A4 vertical (8.27 x 11.69 pulgadas)
                fig = plt.figure(figsize=(8.27, 11.69), dpi=150)
                fig.patch.set_facecolor("white")

                # 1. Encabezado Institucional
                fig.text(0.5, 0.95, "PLAT-EGRE | Observatorio de Seguimiento de Egresados",
                         ha="center", va="top", fontsize=15, fontweight="bold", color="#1B365D")
                fig.text(0.5, 0.925, f"Reporte Analítico — Filtro de Carrera: {carrera_actual}",
                         ha="center", va="top", fontsize=11, color="#333333")
                fig.text(0.5, 0.905, f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
                         ha="center", va="top", fontsize=9, color="#666666")

                # Línea separadora
                line = plt.Line2D([0.08, 0.92], [0.89, 0.89], transform=fig.transFigure, color="#1B365D", linewidth=1.2)
                fig.add_artist(line)

                # 2. Tarjetas de KPIs
                ax_kpi = fig.add_axes([0.08, 0.78, 0.84, 0.09])
                ax_kpi.axis("off")
                ax_kpi.text(0.25, 0.65, f"{tasa:.2f}%", ha="center", va="center", fontsize=20, fontweight="bold", color="#2fa572")
                ax_kpi.text(0.25, 0.20, "Tasa de Empleabilidad", ha="center", va="center", fontsize=10, color="#333333")

                ax_kpi.text(0.75, 0.65, f"S/. {salario:,.2f}", ha="center", va="center", fontsize=20, fontweight="bold", color="#1f538d")
                ax_kpi.text(0.75, 0.20, "Ingreso Laboral Promedio", ha="center", va="center", fontsize=10, color="#333333")

                # 3. Gráfico de Distribución Laboral
                ax_pie = fig.add_axes([0.15, 0.46, 0.70, 0.29])
                if distribucion:
                    labels = list(distribucion.keys())
                    valores = list(distribucion.values())
                    paleta = ['#2fa572', '#1f538d', '#e67e22', '#e74c3c', '#9b59b6']
                    colores = [paleta[i % len(paleta)] for i in range(len(labels))]
                    ax_pie.pie(valores, labels=labels, autopct='%1.1f%%', colors=colores, textprops={'fontsize': 9})
                    ax_pie.set_title("Distribución de Condición Laboral", fontsize=11, fontweight="bold", color="#1B365D", pad=8)
                else:
                    ax_pie.text(0.5, 0.5, "Sin datos históricos para el filtro seleccionado", ha="center", va="center", fontsize=10)
                    ax_pie.axis("off")

                # 4. Tabla de Detalle de Egresados (máximo 15 filas en la hoja resumen)
                ax_tbl = fig.add_axes([0.08, 0.06, 0.84, 0.36])
                ax_tbl.axis("off")
                ax_tbl.set_title("Detalle Consolidado de Egresados (Muestra)", fontsize=11, fontweight="bold", color="#1B365D", loc="left", pad=6)

                columnas = ["Egresado", "Carrera", "Condición", "Cargo / Área", "Ingreso (S/.)"]
                filas_tabla = []
                for r in registros[:15]:
                    nombre = str(r[0])[:26]
                    carr = str(r[1])[:22]
                    cond = str(r[2]) if r[2] else "Sin registro"
                    cargo = str(r[3])[:22] if r[3] else "-"
                    ing = f"S/. {float(r[4]):,.2f}" if r[4] is not None else "S/. 0.00"
                    filas_tabla.append([nombre, carr, cond, cargo, ing])

                if not filas_tabla:
                    filas_tabla = [["Sin registros", "-", "-", "-", "-"]]

                tabla = ax_tbl.table(
                    cellText=filas_tabla,
                    colLabels=columnas,
                    loc="upper center",
                    cellLoc="left",
                    colColours=["#1B365D"] * 5
                )
                tabla.auto_set_font_size(False)
                tabla.set_fontsize(7.5)
                tabla.scale(1, 1.35)

                # Estilizar encabezados de tabla en blanco y negrita
                for (row_idx, col_idx), cell in tabla.get_celld().items():
                    cell.set_edgecolor("#CCCCCC")
                    if row_idx == 0:
                        cell.get_text().set_color("white")
                        cell.get_text().set_weight("bold")
                    elif row_idx % 2 == 0:
                        cell.set_facecolor("#F4F7FA")

                pdf.savefig(fig)
                plt.close(fig)

            print(f"[DashboardView] Reporte PDF generado correctamente en: {ruta_pdf}")
            messagebox.showinfo("PLAT-EGRE | Reporte Generado", f"Reporte PDF exportado con éxito:\n{ruta_pdf}")

            # Abrir automáticamente el PDF generado en Windows
            if os.name == "nt":
                os.startfile(ruta_pdf)

        except Exception as e:
            print(f"[DashboardView] Error al exportar PDF: {e}")
            messagebox.showerror("Error al Exportar PDF", f"No se pudo generar el reporte:\n{e}")