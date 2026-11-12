"""Rol B: excepciones y registro de incidencias.

Los tipos de excepción y el contrato de reporte están definidos.
El estudiante implementa la estrategia de captura, clasificación y reporte
durante las semanas 11 y 12.
"""
from datetime import datetime


class DataLabError(Exception):
    """Excepción base de la aplicación."""

class ErrorValidacion(DataLabError):
    """El registro no cumple las reglas de calidad."""

class ErrorFormatoFuente(DataLabError):
    """La estructura de entrada no corresponde al contrato esperado."""

class ErrorLecturaFuente(DataLabError):
    """No fue posible leer una fuente de datos."""

def crear_reporte_error(origen, identificador, mensaje, categoria="PROCESAMIENTO"):
    """Construye una incidencia serializable con el contexto original del error."""
    return {
        "origen": origen,
        "identificador": identificador,
        "mensaje": str(mensaje),
        "categoria": str(categoria).strip().upper(),
        "fecha_hora": datetime.now().astimezone().isoformat(),
    }
