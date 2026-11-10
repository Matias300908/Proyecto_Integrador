"""Orquestación del procesamiento.

Semana 10–12: completar integración con validación y excepciones.
La clasificación permanece centralizada en clasificacion.py.
"""
from src.processing.clasificacion import clasificar_valor
from src.processing.resumen import generar_resumen
from src.exceptions.errores import crear_reporte_error
from src.validation.normalizacion import normalizar_registro
from src.validation.validaciones import validar_registro


def procesar_registros(registros):
    """Normaliza, valida y clasifica lotes de registros sin detener el flujo."""
    resultado = {
        "registros_validos": [],
        "registros_invalidos": [],
        "errores": [],
        "resumen": {},
    }

    if registros is None:
        return resultado

    for registro in registros:
        try:
            registro_normalizado = normalizar_registro(registro)
            es_valido, motivos = validar_registro(registro_normalizado)
            if not es_valido:
                resultado["registros_invalidos"].append({
                    "registro": registro_normalizado,
                    "motivos": motivos,
                })
                continue

            valor = float(registro_normalizado["valor"])
            registro_normalizado["valor"] = valor
            registro_normalizado["clasificacion"] = clasificar_valor(valor, registro_normalizado["tipo"])
            resultado["registros_validos"].append(registro_normalizado)
        except Exception as exc:  # Aislar fallas técnicas de un registro sin abortar el lote.
            identificador = registro.get("id") if isinstance(registro, dict) else None
            resultado["errores"].append(
                crear_reporte_error("PROCESAMIENTO", identificador, str(exc))
            )
            resultado["registros_invalidos"].append({
                "registro": registro,
                "motivos": [str(exc)],
            })

    resultado["resumen"] = generar_resumen(resultado["registros_validos"])
    return resultado
