
"""
Orquestación del procesamiento.

Semana 10-12: integración con validación y excepciones.
Semana 13: refactorización del procesamiento y trazabilidad.

La clasificación permanece centralizada en clasificacion.py.
"""

from datetime import datetime
from uuid import uuid4

from src.processing.clasificacion import clasificar_valor
from src.processing.resumen import generar_resumen
from src.exceptions.errores import crear_reporte_error
from src.validation.normalizacion import normalizar_registro
from src.validation.validaciones import validar_registro


# ==================================================
# SEMANA 13
# 1. IDENTIFICACIÓN Y TRAZABILIDAD
# ==================================================

def registrar_evento(trazabilidad, lote_id, registro_id,
                     etapa, estado, detalle=""):

    evento = {
        "lote_id": lote_id,
        "registro_id": registro_id,
        "etapa": etapa,
        "estado": estado,
        "detalle": str(detalle),
        "fecha_hora": datetime.now().astimezone().isoformat()
    }

    trazabilidad.append(evento)


# ==================================================
# SEMANA 13
# 2. OBTENER IDENTIFICADOR DEL REGISTRO
# ==================================================

def obtener_identificador(registro, posicion):

    if isinstance(registro, dict):
        return registro.get("id", f"REGISTRO_{posicion}")

    return f"REGISTRO_{posicion}"


# ==================================================
# SEMANA 13
# 3. PROCESAMIENTO INDIVIDUAL
# ==================================================

def procesar_registro(registro, posicion, lote_id, trazabilidad):

    identificador = obtener_identificador(registro, posicion)
    etapa = "INICIO"

    registrar_evento(
        trazabilidad, lote_id, identificador,
        etapa, "INICIADO"
    )

    try:

        # NORMALIZACIÓN

        etapa = "NORMALIZACION"

        registro_normalizado = normalizar_registro(registro)

        registrar_evento(
            trazabilidad, lote_id, identificador,
            etapa, "EXITOSO"
        )

        # VALIDACIÓN

        etapa = "VALIDACION"

        es_valido, motivos = validar_registro(registro_normalizado)

        if not es_valido:

            registrar_evento(
                trazabilidad, lote_id, identificador,
                etapa, "RECHAZADO", motivos
            )

            return {
                "estado": "INVALIDO",
                "registro": registro_normalizado,
                "motivos": motivos
            }

        registrar_evento(
            trazabilidad, lote_id, identificador,
            etapa, "EXITOSO"
        )

        # CONVERSIÓN

        etapa = "CONVERSION"

        valor = float(registro_normalizado["valor"])
        registro_normalizado["valor"] = valor

        registrar_evento(
            trazabilidad, lote_id, identificador,
            etapa, "EXITOSO",
            "Valor convertido correctamente a número."
        )

        # CLASIFICACIÓN CENTRALIZADA

        etapa = "CLASIFICACION"

        registro_normalizado["clasificacion"] = clasificar_valor(
            valor,
            registro_normalizado["tipo"]
        )

        registrar_evento(
            trazabilidad, lote_id, identificador,
            etapa, "EXITOSO"
        )

        # REGISTRO PROCESADO

        registrar_evento(
            trazabilidad, lote_id, identificador,
            "FINALIZACION", "COMPLETADO"
        )

        return {
            "estado": "VALIDO",
            "registro": registro_normalizado,
            "motivos": []
        }

    except Exception as exc:

        # CAPTURA Y REPORTE DEL ERROR

        registrar_evento(
            trazabilidad, lote_id, identificador,
            etapa, "ERROR", str(exc)
        )

        reporte = crear_reporte_error(
            "PROCESAMIENTO",
            identificador,
            str(exc),
            etapa
        )

        return {
            "estado": "ERROR",
            "registro": registro,
            "motivos": [str(exc)],
            "reporte": reporte
        }


# ==================================================
# SEMANA 13
# 4. ORQUESTACIÓN GENERAL DEL LOTE
# ==================================================

def procesar_registros(registros):

    resultado = {
        "lote_id": uuid4().hex[:12],
        "registros_validos": [],
        "registros_invalidos": [],
        "errores": [],
        "trazabilidad": [],
        "resumen": {}
    }

    if registros is None:
        return resultado

    lote_id = resultado["lote_id"]

    # PROCESAMIENTO INDEPENDIENTE DE CADA REGISTRO

    for posicion, registro in enumerate(registros, start=1):

        identificador = obtener_identificador(registro, posicion)

        procesado = procesar_registro(
            registro,
            posicion,
            lote_id,
            resultado["trazabilidad"]
        )

        if procesado["estado"] == "VALIDO":

            resultado["registros_validos"].append(
                procesado["registro"]
            )

        elif procesado["estado"] == "INVALIDO":

            resultado["registros_invalidos"].append({
                "registro": procesado["registro"],
                "motivos": procesado["motivos"]
            })

        else:

            resultado["errores"].append(
                procesado["reporte"]
            )

            resultado["registros_invalidos"].append({
                "registro": procesado["registro"],
                "motivos": procesado["motivos"]
            })

        # El ciclo continúa con el siguiente registro.

    # GENERACIÓN DEL RESUMEN

    try:

        resultado["resumen"] = generar_resumen(
            resultado["registros_validos"]
        )

    except Exception as exc:

        resultado["errores"].append(
            crear_reporte_error(
                "PROCESAMIENTO",
                None,
                str(exc),
                "RESUMEN"
            )
        )

        registrar_evento(
            resultado["trazabilidad"],
            lote_id,
            None,
            "RESUMEN",
            "ERROR",
            str(exc)
        )

    return resultado


# ==================================================
# SEMANA 13
# 5. CONSULTA DE TRAZABILIDAD
# ==================================================

def mostrar_trazabilidad(resultado):

    print("\n========== TRAZABILIDAD DEL LOTE ==========")

    print("Identificador del lote:", resultado["lote_id"])

    for evento in resultado["trazabilidad"]:

        print("\nRegistro:", evento["registro_id"])
        print("Etapa:", evento["etapa"])
        print("Estado:", evento["estado"])
        print("Detalle:", evento["detalle"])
        print("Fecha:", evento["fecha_hora"])


# ==================================================
# SEMANA 13
# 6. REPORTE FINAL
# ==================================================

def mostrar_resultados(resultado):

    print("\n========== RESULTADOS DEL PROCESAMIENTO ==========")

    print(
        "Registros válidos:",
        len(resultado["registros_validos"])
    )

    print(
        "Registros inválidos:",
        len(resultado["registros_invalidos"])
    )

    print(
        "Errores técnicos:",
        len(resultado["errores"])
    )

    print("\n========== RESUMEN ==========")

    print(resultado["resumen"])

    print("\n========== ERRORES ==========")

    for error in resultado["errores"]:
        print(error)

    mostrar_trazabilidad(resultado)

