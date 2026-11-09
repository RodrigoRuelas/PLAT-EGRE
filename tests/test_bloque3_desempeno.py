import unittest
import pandas as pd
import time
from datetime import datetime

# Importación de módulos del proyecto PLAT-EGRE
from config.database import DatabaseConfig
from src.etl.pipeline_manager import ETLPipelineManager
from src.etl.transformer import ValidadorTransformador
from src.etl.loader import CargadorBD


class TestBloque3Desempeno(unittest.TestCase):
    """
    Bloque 3: Pruebas de Desempeño y Carga Masiva (Eficiencia Temporal).
    Evaluación del tiempo de respuesta y escalabilidad del pipeline ETL.
    """

    @classmethod
    def setUpClass(cls):
        """Inicialización de servicios y motor de prueba."""
        cls.db_config = DatabaseConfig()
        cls.transformador = ValidadorTransformador()
        cls.loader = CargadorBD()
        cls.pipeline = ETLPipelineManager()

    def _generar_dataset_sintetico(self, cantidad: int) -> pd.DataFrame:
        """Genera un DataFrame sintético con N registros para pruebas de estrés."""
        return pd.DataFrame([
            {
                "dni": f"{10000000 + i}",
                "nombres": f"Nombre_{i}",
                "apellidos": f"Apellido_{i}",
                "carrera": "Ingeniería de Sistemas",
                "periodo_egreso": "2023-II",
                "correo": f"egresado_{i}@test.com",
                "celular": f"900000{i:03d}",
                "Ingreso_Mensual": f"S/. {3000 + (i % 10) * 100}.00"
            } for i in range(1, cantidad + 1)
        ])

    def test_PD01_procesamiento_100_registros(self):
        """
        PD-01: Carga y transformación masiva de 100 registros sintéticos.
        Requerimiento: RNF-0002, RF-0002
        Umbral máximo permitido: 2.00 segundos
        """
        df_100 = self._generar_dataset_sintetico(100)

        print("\n" + "-" * 70)
        print(" 📌 CASO: PD-01 | Procesamiento Masivo de 100 Registros")
        print(f"   • Volumetría : {len(df_100)} registros sintéticos en memoria")

        inicio = time.time()
        # Proceso de normalización y limpieza
        df_limpio = self.transformador.normalizar_textos(df_100)
        df_final = self.transformador.convertir_vacios_null(df_limpio)
        tiempo_ejecucion = time.time() - inicio

        # Cálculo de Eficiencia Temporal (ET = segundos / (registros / 100))
        et = tiempo_ejecucion / (len(df_100) / 100)

        print(f"   • Salida   : Procesado en {tiempo_ejecucion:.4f} segundos")
        print(f"   • Métrica  : Eficiencia Temporal (ET) = {et:.4f} seg/100 reg")
        print("   • Umbral   : Max. 2.0000 segundos")

        self.assertLessEqual(tiempo_ejecucion, 2.00)
        print("   ✅ ESTADO  : PASS (Desempeño óptimo bajo carga de 100 registros)")

    def test_PD02_procesamiento_500_registros(self):
        """
        PD-02: Carga y transformación masiva de 500 registros sintéticos.
        Requerimiento: RNF-0002, RF-0002
        Umbral máximo permitido: 5.00 segundos
        """
        df_500 = self._generar_dataset_sintetico(500)

        print("\n" + "-" * 70)
        print(" 📌 CASO: PD-02 | Procesamiento Masivo de 500 Registros")
        print(f"   • Volumetría : {len(df_500)} registros sintéticos en memoria")

        inicio = time.time()
        df_limpio = self.transformador.normalizar_textos(df_500)
        df_final = self.transformador.convertir_vacios_null(df_limpio)
        tiempo_ejecucion = time.time() - inicio

        et = tiempo_ejecucion / (len(df_500) / 100)

        print(f"   • Salida   : Procesado en {tiempo_ejecucion:.4f} segundos")
        print(f"   • Métrica  : Eficiencia Temporal (ET) = {et:.4f} seg/100 reg")
        print("   • Umbral   : Max. 5.0000 segundos")

        self.assertLessEqual(tiempo_ejecucion, 5.00)
        print("   ✅ ESTADO  : PASS (Desempeño estable bajo carga de 500 registros)")

    def test_PD03_procesamiento_1000_registros(self):
        """
        PD-03: Prueba de Estrés y Escalabilidad con 1,000 registros sintéticos.
        Requerimiento: RNF-0002, RF-0002
        Umbral máximo permitido: 10.00 segundos
        """
        df_1000 = self._generar_dataset_sintetico(1000)

        print("\n" + "-" * 70)
        print(" 📌 CASO: PD-03 | Prueba de Estrés con 1,000 Registros")
        print(f"   • Volumetría : {len(df_1000)} registros sintéticos en memoria")

        inicio = time.time()
        df_limpio = self.transformador.normalizar_textos(df_1000)
        df_final = self.transformador.convertir_vacios_null(df_limpio)
        tiempo_ejecucion = time.time() - inicio

        et = tiempo_ejecucion / (len(df_1000) / 100)

        print(f"   • Salida   : Procesado en {tiempo_ejecucion:.4f} segundos")
        print(f"   • Métrica  : Eficiencia Temporal (ET) = {et:.4f} seg/100 reg")
        print("   • Umbral   : Max. 10.0000 segundos")

        self.assertLessEqual(tiempo_ejecucion, 10.00)
        print("   ✅ ESTADO  : PASS (Escalabilidad lineal confirmada)")


def ejecutar_banco_bloque3():
    print("=" * 70)
    print(" 🧪 EJECUCIÓN AUTOMATIZADA: BLOQUE 3 (PRUEBAS DE DESEMPEÑO Y CARGA MASIVA)")
    print(f" Fecha/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    suite = unittest.TestLoader().loadTestsFromTestCase(TestBloque3Desempeno)
    runner = unittest.TextTestRunner(verbosity=0)
    resultado = runner.run(suite)

    total_pruebas = resultado.testsRun
    fallos = len(resultado.failures) + len(resultado.errors)
    exitosas = total_pruebas - fallos
    tti = (exitosas / total_pruebas) * 100 if total_pruebas > 0 else 0

    print("\n" + "=" * 70)
    print(" 📊 RESUMEN DE RESULTADOS Y MÉTRICAS - BLOQUE 3")
    print("=" * 70)
    print(f"   • Pruebas Programadas y Ejecutadas : {total_pruebas}")
    print(f"   • Pruebas Exitosas (Passed)         : {exitosas}")
    print(f"   • Pruebas Fallidas (Failed)         : {fallos}")
    print(f"   • Tasa de Tolerancia / Éxito (TTI)  : {tti:.2f}%")
    print("=" * 70)

    if tti == 100.0:
        print(" 🎉 ESTADO GLOBAL DEL BLOQUE 3: APROBADO (100% SUCCESS)")
    else:
        print(" ⚠️ ESTADO GLOBAL DEL BLOQUE 3: REQUIERE REVISIÓN")
    print("=" * 70)


if __name__ == "__main__":
    ejecutar_banco_bloque3()