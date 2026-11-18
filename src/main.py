"""Punto de entrada de la versión de consola.

REVISIÓN (base común): antes este archivo clasificaba directamente los
registros de memoria, sin pasar por normalización, validación ni manejo de
errores. Ahora usa el mismo servicio que Streamlit (ejecutar_demo), así la
consola y la interfaz gráfica recorren exactamente el mismo flujo:
fuente (C) -> normalización y validación (A) -> procesamiento y errores (B).
"""
from src.services.datalab_service import ejecutar_demo
from src.interface.consola import mostrar_resumen


def main():
    resultado = ejecutar_demo()
    mostrar_resumen(resultado["resumen"])
    print(
        f"Válidos: {len(resultado['registros_validos'])} | "
        f"Inválidos: {len(resultado['registros_invalidos'])} | "
        f"Errores técnicos: {len(resultado['errores'])}"
    )


if __name__ == "__main__":
    main()
