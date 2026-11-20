import os
import time
from datetime import datetime


class ServicioAuditoria:
    def __init__(self, ruta_log: str = "logs/log_auditoria.txt"):
        self.ruta_log: str = ruta_log
        self.ID_ejecucion: str = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._tiempo_inicio: float = 0.0
        self._asegurar_directorio()

    def _asegurar_directorio(self) -> None:
        directorio = os.path.dirname(self.ruta_log)
        if directorio:
            os.makedirs(directorio, exist_ok=True)

    def iniciar_cronometro(self) -> None:
        """Inicia el contador de alta precisión para medir la Eficiencia Temporal (ET)."""
        self.ID_ejecucion = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._tiempo_inicio = time.perf_counter()

    def obtener_tiempo_transcurrido(self) -> float:
        """Retorna el tiempo transcurrido en segundos desde iniciar_cronometro()."""
        if self._tiempo_inicio == 0.0:
            return 0.0
        return round(time.perf_counter() - self._tiempo_inicio, 4)

    def registrar_evento(self, msg: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [INFO] [{self.ID_ejecucion}] {msg}\n"
        with open(self.ruta_log, "a", encoding="utf-8") as f:
            f.write(log_line)
        print(log_line.strip())

    def registrar_error(self, err: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tiempo_et = self.obtener_tiempo_transcurrido()
        sufijo_tiempo = f" (Tiempo transcurrido: {tiempo_et:.4f} s)" if self._tiempo_inicio > 0 else ""
        log_line = f"[{timestamp}] [ERROR] [{self.ID_ejecucion}] {err}{sufijo_tiempo}\n"
        with open(self.ruta_log, "a", encoding="utf-8") as f:
            f.write(log_line)
        print(log_line.strip())

    def registrar_metricas_carga(
        self,
        nombre_archivo: str,
        total_leidos: int,
        registros_exitosos: int,
        inconsistencias_detectadas: int = 0,
        atributos_corregidos: int = 0,
        tiempo_segundos: float = None
    ) -> dict:
        """
        Calcula y escribe en el log las métricas de calidad y rendimiento del ETL:
        - Eficiencia Temporal (ET)
        - Tasa de Eficiencia de Inserción (TEI)
        - Tasa de Tolerancia a Inconsistencias (TTI)
        """
        et_segundos = tiempo_segundos if tiempo_segundos is not None else self.obtener_tiempo_transcurrido()
        et_ms = round(et_segundos * 1000, 2)

        # 1. Tasa de Eficiencia de Inserción (TEI)
        tei = round((registros_exitosos / total_leidos) * 100, 2) if total_leidos > 0 else 0.0

        # 2. Tasa de Tolerancia a Inconsistencias (TTI)
        if inconsistencias_detectadas > 0:
            tti = round((atributos_corregidos / inconsistencias_detectadas) * 100, 2)
        else:
            tti = 100.00  # Sin inconsistencias detectadas -> tolerancia óptima

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        resumen = (
            f"[{timestamp}] [METRICAS] [{self.ID_ejecucion}] Archivo: {os.path.basename(nombre_archivo)} | "
            f"ET (Tiempo): {et_segundos:.4f} s ({et_ms} ms) | "
            f"TEI: {tei:.2f}% ({registros_exitosos}/{total_leidos} registros) | "
            f"TTI: {tti:.2f}% ({atributos_corregidos}/{inconsistencias_detectadas} inconsistencias corregidas)\n"
        )

        with open(self.ruta_log, "a", encoding="utf-8") as f:
            f.write(resumen)
        print(resumen.strip())

        return {
            "ET_segundos": et_segundos,
            "ET_ms": et_ms,
            "TEI": tei,
            "TTI": tti
        }