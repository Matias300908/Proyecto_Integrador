
"""
Orquestación del procesamiento.

Semana 10-12: integración con validación y excepciones.
Semana 13: refactorización del procesamiento y trazabilidad.

La clasificación permanece centralizada en clasificacion.py.

REVISIÓN (semanas 10–12) — resumen de cambios. Busque "# REVISIÓN":
  B-1  Cada fila queda en UNA sola bandeja: válidos, inválidos o errores.
       Antes un error técnico se agregaba a "errores" Y a
       "registros_invalidos"; la interfaz suma las tres bandejas para
       mostrar "Recibidos", así que el total quedaba inflado.
  B-2  Se detectan los eventos técnicos del sensor (columna
       observacion_tecnica = SIMULACION_*) y las filas que el lector marcó
       con "_error_tecnico". Antes terminaban como válidos o como inválidos
       con motivos engañosos ("falta tipo, valor, unidad").
  B-4  Dos bloques except: DataLabError (errores previstos, la categoría
       sale de error.CATEGORIA) y Exception (red de seguridad, "SISTEMA").
       Antes la categoría era el nombre de la etapa (NORMALIZACION...).
  B-5  La conversión a float lanza ErrorConversion "from exc", que conserva
       el error original como causa.
  B-6  Una entrada que no es lista (un dict, un texto) se reporta como
       error en lugar de recorrerse carácter por carácter.
  Lo marcado como "SEMANA 13" (trazabilidad, lote_id) se conservó tal cual;
  no forma parte de esta revisión (semanas 10 a 12).
"""

from datetime import datetime
from uuid import uuid4

from src.processing.clasificacion import clasificar_valor
from src.processing.resumen import generar_resumen
from src.exceptions.errores import (
    DataLabError,
    ErrorConversion,
    ErrorEstructuraRegistro,
    ErrorEventoSensor,
    EVENTOS_TECNICOS,
    crear_reporte_error,
)
from src.validation.normalizacion import normalizar_registro
from src.validation.validaciones import validar_registro

# REVISIÓN: origen por defecto de los reportes de error del lote.
ORIGEN_LOTE = "PROCESAMIENTO"


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

    # REVISIÓN: también se usa el id cuando viene vacío o None
    # (p. ej. una fila irregular sin id) -> se cae al número de posición.
    if isinstance(registro, dict) and registro.get("id") not in (None, ""):
        return registro["id"]

    return f"REGISTRO_{posicion}"


# ==================================================
# REVISIÓN B-2 (semanas 11–12)
# REVISIÓN TÉCNICA ANTES DE LA CALIDAD
# ==================================================

def _revisar_eventos_tecnicos(registro):
    """Lanza una excepción si el registro trae una falla TÉCNICA del origen.

    Diferencia clave para la sustentación:
      - Dato de MALA CALIDAD (Rol A)  -> registros_invalidos, con motivos.
      - FALLA TÉCNICA del origen (B)  -> errores, con categoría.
    """
    # Un elemento que no es diccionario no puede normalizarse ni validarse.
    if not isinstance(registro, dict):
        raise ErrorEstructuraRegistro(
            f"El registro no es un diccionario sino {type(registro).__name__}: {registro!r}"
        )

    # El Rol C marca así las filas con columnas de más o de menos.
    if "_error_tecnico" in registro:
        fila = registro.get("_fila", "?")
        origen = registro.get("_origen", "fuente")
        raise ErrorEstructuraRegistro(
            f"{registro['_error_tecnico']} ({origen}, fila {fila})"
        )

    # Eventos simulados en la columna observacion_tecnica de los datasets.
    evento = registro.get("observacion_tecnica")
    if isinstance(evento, str) and evento.strip().upper().startswith("SIMULACION_"):
        clave = evento.strip().upper()
        # .get(clave, ErrorEventoSensor): un evento nuevo que no está en la
        # tabla usa la clase general en lugar de romper el procesamiento.
        clase_error = EVENTOS_TECNICOS.get(clave, ErrorEventoSensor)
        raise clase_error(f"Evento técnico del sensor: {clave}")


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

        # REVISIÓN B-2: REVISIÓN TÉCNICA (estructura y eventos del sensor)

        etapa = "REVISION_TECNICA"

        _revisar_eventos_tecnicos(registro)

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

            # Formato que lee la interfaz: {"registro": ..., "motivos": [...]}.
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

        # REVISIÓN B-5: si la conversión falla se lanza la excepción propia
        # del proyecto. "from exc" guarda el error original como causa
        # (se ve en el traceback como "The above exception was the direct
        # cause of..."), útil para depurar.
        try:
            valor = float(registro_normalizado["valor"])
        except (TypeError, ValueError, OverflowError) as exc:
            raise ErrorConversion(
                f"No se pudo convertir el valor {registro_normalizado.get('valor')!r} a número"
            ) from exc
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

    # REVISIÓN B-4: primero los errores PREVISTOS del proyecto. La categoría
    # la sabe la propia excepción (atributo de clase CATEGORIA).
    except DataLabError as exc:

        registrar_evento(
            trazabilidad, lote_id, identificador,
            etapa, "ERROR", str(exc)
        )

        return {
            "estado": "ERROR",
            "registro": registro,
            "motivos": [str(exc)],
            "reporte": crear_reporte_error(
                ORIGEN_LOTE, identificador, exc, exc.CATEGORIA
            )
        }

    # REVISIÓN B-4: red de seguridad para lo IMPREVISTO. El orden importa:
    # si este bloque fuera primero, capturaría también los DataLabError.
    except Exception as exc:

        registrar_evento(
            trazabilidad, lote_id, identificador,
            etapa, "ERROR", str(exc)
        )

        return {
            "estado": "ERROR",
            "registro": registro,
            "motivos": [str(exc)],
            "reporte": crear_reporte_error(
                ORIGEN_LOTE, identificador,
                f"Error inesperado en la etapa {etapa}: {type(exc).__name__}: {exc}",
                "SISTEMA"
            )
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
        # REVISIÓN: el resumen siempre tiene las mismas claves (total 0,
        # promedio 0.0...) aunque el lote esté vacío o falle por completo.
        "resumen": generar_resumen([])
    }

    if registros is None:
        return resultado

    # REVISIÓN B-6: un str también se puede recorrer con for (letra por letra)
    # y un dict recorrería sus claves. Se exige una lista o tupla.
    if not isinstance(registros, (list, tuple)):
        resultado["errores"].append(
            crear_reporte_error(
                ORIGEN_LOTE, "N/A",
                f"Se esperaba una lista de registros y se recibió {type(registros).__name__}",
                ErrorEstructuraRegistro.CATEGORIA
            )
        )
        return resultado

    lote_id = resultado["lote_id"]

    # PROCESAMIENTO INDEPENDIENTE DE CADA REGISTRO

    for posicion, registro in enumerate(registros, start=1):

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

            # REVISIÓN B-1: un error técnico va SOLO a "errores".
            # Antes también se agregaba a "registros_invalidos" y el registro
            # se contaba dos veces (válidos + inválidos + errores > filas).
            resultado["errores"].append(
                procesado["reporte"]
            )

        # El ciclo continúa con el siguiente registro (B-S11-04).

    # GENERACIÓN DEL RESUMEN

    try:

        resultado["resumen"] = generar_resumen(
            resultado["registros_validos"]
        )

    except Exception as exc:

        resultado["errores"].append(
            crear_reporte_error(
                ORIGEN_LOTE,
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
