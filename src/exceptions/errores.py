"""Rol B: excepciones y registro de incidencias.

REVISIÓN (semanas 11–12) — resumen de cambios. Busque "# REVISIÓN":
  B-3  Se eliminó el código de OTRO ejercicio que estaba en este archivo:
       leer_fuente(), validar_registro() y procesar_registros() para
       registros de personas (nombre, edad, correo), mostrar_resultados()
       que escribía reporte_errores.json y un main() con datos de prueba.
       Ese código no pertenece a DataLab y además repetía los nombres de
       las funciones de los contratos de los roles A y B
       (validar_registro, procesar_registros), lo que confunde a quien
       lee e importa. Git conserva la versión anterior (commit da42b86).
  B-4  Cada excepción declara su CATEGORIA como atributo de clase. El
       procesamiento ya no necesita cadenas if/elif para saber qué
       categoría reportar: le pregunta al propio error (error.CATEGORIA).
  B-5  Nuevas excepciones para los eventos técnicos de los datasets
       (columna observacion_tecnica), para filas con estructura rota y
       para fallas de conversión.
"""
from datetime import datetime


# --------------------------------------------------------------------------
# Jerarquía de excepciones
# --------------------------------------------------------------------------
# REVISIÓN B-4: las subclases heredan CATEGORIA o la redefinen. Así
# "except DataLabError as error" captura todas y error.CATEGORIA dice cuál fue.

class DataLabError(Exception):
    """Excepción base de la aplicación."""
    CATEGORIA = "PROCESAMIENTO"


class ErrorValidacion(DataLabError):
    """El registro no cumple las reglas de calidad."""
    CATEGORIA = "VALIDACION"


class ErrorConversion(DataLabError):
    # REVISIÓN B-5: antes un fallo de float() terminaba como error genérico.
    """No fue posible convertir un campo al tipo esperado (p. ej. valor a float)."""
    CATEGORIA = "CONVERSION"


class ErrorFormatoFuente(DataLabError):
    """La estructura de entrada no corresponde al contrato esperado."""
    CATEGORIA = "FORMATO"


class ErrorEstructuraRegistro(ErrorFormatoFuente):
    # REVISIÓN B-5: un elemento que no es diccionario (None, un texto suelto)
    # o una fila que el lector marcó con "_error_tecnico".
    """Un registro individual llegó con una estructura que no se puede procesar."""
    CATEGORIA = "ESTRUCTURA_REGISTRO"


class ErrorLecturaFuente(DataLabError):
    """No fue posible leer una fuente de datos."""
    CATEGORIA = "LECTURA"


class ErrorEventoSensor(DataLabError):
    # REVISIÓN B-5: falla TÉCNICA reportada por el origen (no es mala calidad
    # del dato). Va a "errores", no a "registros_invalidos".
    """El sensor reportó un evento técnico durante la lectura."""
    CATEGORIA = "EVENTO_SENSOR"


class ErrorTimeoutSensor(ErrorEventoSensor):
    """El sensor no respondió a tiempo."""
    CATEGORIA = "TIMEOUT_SENSOR"


class ErrorPaqueteIncompleto(ErrorEventoSensor):
    """El paquete de datos del sensor llegó incompleto."""
    CATEGORIA = "PAQUETE_INCOMPLETO"


class ErrorLecturaIntermitente(ErrorEventoSensor):
    """La lectura del sensor fue intermitente."""
    CATEGORIA = "LECTURA_INTERMITENTE"


# REVISIÓN B-5: tabla "texto del evento -> clase de excepción". Agregar un
# evento nuevo es agregar una línea; el ciclo de procesamiento no cambia.
EVENTOS_TECNICOS = {
    "SIMULACION_TIMEOUT_SENSOR": ErrorTimeoutSensor,
    "SIMULACION_PAQUETE_INCOMPLETO": ErrorPaqueteIncompleto,
    "SIMULACION_LECTURA_INTERMITENTE": ErrorLecturaIntermitente,
}


# --------------------------------------------------------------------------
# Reporte de errores (B-S11-01 y B-S11-02)
# --------------------------------------------------------------------------
def crear_reporte_error(origen, identificador, mensaje, categoria="PROCESAMIENTO"):
    """Construye una incidencia serializable con el contexto original del error.

    Las claves (origen, identificador, mensaje, categoria, fecha_hora) son las
    que muestra y descarga la pestaña de errores técnicos de la interfaz.
    """
    return {
        "origen": origen,
        "identificador": identificador,
        # str(mensaje) conserva el texto original de la excepción (B-S11-02).
        "mensaje": str(mensaje),
        "categoria": str(categoria).strip().upper(),
        # REVISIÓN: timespec="seconds" quita los microsegundos; la fecha se lee
        # mejor en la tabla y en el CSV descargado.
        "fecha_hora": datetime.now().astimezone().isoformat(timespec="seconds"),
    }
