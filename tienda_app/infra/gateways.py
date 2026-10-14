import datetime
import os
from ..domain.interfaces import ProcesadorPago


class BancoNacionalProcesador(ProcesadorPago):
    """
    Implementación concreta de la infraestructura.
    Simula un banco local escribiendo en un log de pagos.
    """

    def pagar(self, monto: float) -> bool:
        # Simulamos una operación de red o persistencia externa escribiendo en log
        log_filename = os.getenv("PAYMENT_LOG_FILE", "pagos_locales.log")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        line = f"[{timestamp}] BANCO NACIONAL - Cobro procesado: ${monto}\n"
        with open(log_filename, "a", encoding="utf-8") as f:
            f.write(line)
        return True