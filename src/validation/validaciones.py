# Rol A: reglas de validación de calidad de registros.
import math

from src.validation.normalizacion import normalizar_registro

TIPOS_PERMITIDOS = {"temperatura", "presion", "humedad"}
UNIDADES_POR_TIPO = {
    "temperatura": "°C",
    "presion": "hPa",
    "humedad": "%",
}
MARCADORES_VALOR_FALTANTE = {
    "n/d",
    "nd",
    "na",
    "n/a",
    "nan",
    "null",
    "none",
    "sin_dato",
    "sin dato",
    "desconocido",
    "?",
    "pendiente",
    "error",
    "-",
    "sin lectura",
}

def validar_registro(registro):
    """Contrato: devuelve (es_valido: bool, motivos: list[str])."""
    if not isinstance(registro, dict):
        return False, ["El registro debe ser un diccionario."]

    registro = normalizar_registro(registro)
    motivos = []

    for campo in ("id", "tipo", "valor", "unidad"):
        valor = registro.get(campo)
        if valor is None or (isinstance(valor, str) and not valor.strip()):
            motivos.append(f"El campo '{campo}' es obligatorio.")

    identificador = registro.get("id")
    if identificador is not None and not isinstance(identificador, str):
        motivos.append(
            f"El campo 'id' debe ser texto; se recibió {identificador!r}."
        )

    tipo = registro.get("tipo")
    tipo_valido = isinstance(tipo, str) and tipo in TIPOS_PERMITIDOS
    tipo_presente = tipo is not None and not (isinstance(tipo, str) and not tipo)
    if tipo_presente and not isinstance(tipo, str):
        motivos.append(f"El campo 'tipo' debe ser texto; se recibió {tipo!r}.")
    elif tipo_presente and not tipo_valido:
        motivos.append(f"Tipo no permitido: {tipo!r}.")

    valor = registro.get("valor")
    valor_presente = valor is not None and not (isinstance(valor, str) and not valor)
    if valor_presente:
        marcador = valor.casefold() if isinstance(valor, str) else None
        if marcador in MARCADORES_VALOR_FALTANTE:
            motivos.append(
                f"El campo 'valor' contiene el marcador de dato faltante "
                f"{valor!r}, que no es un valor numérico; ingrese una medición."
            )
        elif isinstance(valor, bool):
            motivos.append("El campo 'valor' no puede ser booleano.")
        else:
            try:
                valor_numerico = float(valor)
            except (TypeError, ValueError, OverflowError):
                motivos.append(
                    f"El campo 'valor' debe ser numérico; se recibió {valor!r}."
                )
            else:
                if not math.isfinite(valor_numerico):
                    motivos.append(
                        f"El campo 'valor' debe ser finito; se recibió {valor!r}."
                    )

    unidad = registro.get("unidad")
    unidad_presente = unidad is not None and not (
        isinstance(unidad, str) and not unidad
    )
    if unidad_presente and not isinstance(unidad, str):
        motivos.append(f"El campo 'unidad' debe ser texto; se recibió {unidad!r}.")
    elif tipo_valido and unidad_presente and unidad != UNIDADES_POR_TIPO[tipo]:
        motivos.append(
            f"Unidad no válida para '{tipo}': se esperaba "
            f"'{UNIDADES_POR_TIPO[tipo]}' y se recibió {unidad!r}."
        )

    return not motivos, motivos
