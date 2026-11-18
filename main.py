import os
import sys

# ==============================================================================
# 1. CONFIGURACIÓN GLOBAL DE ENTORNO TCL/TK (Python 3.13 / Windows venv)
# ==============================================================================
if sys.platform == "win32" and hasattr(sys, "base_prefix"):
    tcl_dir = os.path.join(sys.base_prefix, "tcl", "tcl8.6")
    tk_dir = os.path.join(sys.base_prefix, "tcl", "tk8.6")
    if os.path.exists(tcl_dir):
        os.environ["TCL_LIBRARY"] = tcl_dir
        os.environ["TK_LIBRARY"] = tk_dir

# Asegurar que el directorio raíz esté en el PYTHONPATH
DIRECTORIO_RAIZ = os.path.dirname(os.path.abspath(__file__))
if DIRECTORIO_RAIZ not in sys.path:
    sys.path.insert(0, DIRECTORIO_RAIZ)

import tkinter as tk
from tkinter import messagebox
from config.database import DatabaseConfig
from src.ui.login_view import LoginView
from src.ui.main_view import PlataformaRegistros


def verificar_conexion_inicial() -> bool:
    """
    Comprueba que SQL Server (PLAT_EGRE_DB) esté activo y accesible
    antes de desplegar las ventanas de la plataforma.
    """
    try:
        conn = DatabaseConfig.get_pyodbc_connection()
        conn.close()
        return True
    except Exception as err:
        print(f"[CRÍTICO] No se pudo establecer conexión con SQL Server: {err}")
        root_err = tk.Tk()
        root_err.withdraw()
        messagebox.showerror(
            "PLAT-EGRE | Error de Base de Datos",
            f"No se pudo conectar con SQL Server.\n\nDetalle técnico:\n{err}\n\n"
            "Verifique que el servicio SQL Server esté iniciado y revise config/database.py."
        )
        root_err.destroy()
        return False


def iniciar_plataforma_principal(usuario_autenticado: str) -> None:
    """
    Callback ejecutado tras validar credenciales exitosamente en LoginView.
    Despliega la ventana principal (ETL + Dashboard Analítico).
    """
    print(f"[SESIÓN INICIADA] Operador activo: {usuario_autenticado}")
    app_principal = PlataformaRegistros(usuario_actual=usuario_autenticado)
    app_principal.mainloop()


def main() -> None:
    print("=" * 70)
    print("  🚀 INICIANDO SISTEMA PLAT-EGRE | OBSERVATORIO DE EMPLEABILIDAD")
    print("=" * 70)

    # Paso 1: Validar conectividad con SQL Server
    print(" 🔍 Verificando conexión con SQL Server...")
    if not verificar_conexion_inicial():
        sys.exit(1)
    print(" ✅ Conexión a base de datos establecida correctamente.")

    # Paso 2: Levantar módulo de autenticación (LoginView)
    print(" 🔐 Desplegando ventana de inicio de sesión...")
    login_app = LoginView(callback_exito=iniciar_plataforma_principal)
    login_app.mainloop()

    print(" 👋 Ejecución de PLAT-EGRE finalizada.")


if __name__ == "__main__":
    main()