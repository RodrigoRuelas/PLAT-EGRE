import os
from datetime import datetime

class ServicioAuditoria:
    def __init__(self, ruta_log: str = "logs/log_auditoria.txt"):
        self.ruta_log: str = ruta_log
        self.ID_ejecucion: str = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._asegurar_directorio()

    def _asegurar_directorio(self) -> None:
        os.makedirs(os.path.dirname(self.ruta_log), exist_ok=True)

    def registrar_evento(self, msg: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [INFO] [{self.ID_ejecucion}] {msg}\n"
        with open(self.ruta_log, "a", encoding="utf-8") as f:
            f.write(log_line)
        print(log_line.strip())

    def registrar_error(self, err: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [ERROR] [{self.ID_ejecucion}] {err}\n"
        with open(self.ruta_log, "a", encoding="utf-8") as f:
            f.write(log_line)
        print(log_line.strip())