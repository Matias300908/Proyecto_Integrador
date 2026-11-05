# Rol A: reglas de validación de calidad de registros.
import math

from src.validation.normalizacion import normalizar_registro

TIPOS_PERMITIDOS = {"temperatura", "presion", "humedad"}
UNIDADES_POR_TIPO = {
    "temperatura": "°C",
    "presion": "hPa",
    "humedad": "%",
}

def validar_registro(registro):
    """Contrato: devuelve (es_valido: bool, motivos: list[str])."""
    if not isinstance(registro, dict):
        return False, ["El registro debe ser un diccionario."]

    registro = normalizar_registro(registro)
    motivos = []

    for campo in ("id", "tipo", "valor", "unidad"):
        valor = registro.get(campo)
        if valor is None or (isinstance(valor, str) and not valor):
            motivos.append(f"El campo '{campo}' es obligatorio.")

    tipo = registro.get("tipo")
    tipo_valido = isinstance(tipo, str) and tipo in TIPOS_PERMITIDOS
    if tipo and not tipo_valido:
        motivos.append(f"Tipo no permitido: {tipo}.")

    valor = registro.get("valor")
    if valor is not None and not (isinstance(valor, str) and not valor):
        if isinstance(valor, bool):
            valor_numerico = False
        else:
            try:
                valor_numerico = math.isfinite(float(valor))
            except (TypeError, ValueError, OverflowError):
                valor_numerico = False
        if not valor_numerico:
            motivos.append("El campo 'valor' debe ser numérico y finito.")

    unidad = registro.get("unidad")
    if tipo_valido and unidad and unidad != UNIDADES_POR_TIPO[tipo]:
        motivos.append(
            f"Unidad no válida para '{tipo}': se esperaba '{UNIDADES_POR_TIPO[tipo]}'."
        )

    return not motivos, motivos
