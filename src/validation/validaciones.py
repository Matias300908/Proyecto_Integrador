"""Rol A: reglas de validación de calidad de registros."""
import math

TIPOS_PERMITIDOS = {"temperatura", "presion", "humedad"}
UNIDADES_POR_TIPO = {
    "temperatura": {"c", "°c"},
    "presion": {"hpa", "pa", "kpa", "mb"},
    "humedad": {"%", "percent", "pct"},
}


def _valor_numerico_aceptado(valor):
    if valor is None or isinstance(valor, bool):
        return False

    try:
        if isinstance(valor, (int, float)):
            numero = float(valor)
        elif isinstance(valor, str):
            texto = valor.strip()
            if not texto or texto.lower() in {"nan", "inf", "-inf", "+inf"}:
                return False
            numero = float(texto)
        else:
            return False
    except (TypeError, ValueError):
        return False

    return math.isfinite(numero)


def validar_registro(registro):
    """Contrato: devuelve (es_valido: bool, motivos: list[str])."""
    if not isinstance(registro, dict):
        return False, ["El registro debe ser un diccionario."]

    motivos = []
    campos_obligatorios = ("id", "tipo", "valor", "unidad")

    for campo in campos_obligatorios:
        if campo not in registro or registro[campo] is None or str(registro[campo]).strip() == "":
            motivos.append(f"Falta el campo obligatorio '{campo}'.")

    tipo = str(registro.get("tipo", "")).strip().lower()
    if tipo and tipo not in TIPOS_PERMITIDOS:
        motivos.append(f"Tipo no reconocido: '{tipo}'.")

    valor = registro.get("valor")
    if not _valor_numerico_aceptado(valor):
        motivos.append("El valor debe ser numérico y finito.")

    unidad = str(registro.get("unidad", "")).strip()
    if unidad == "":
        motivos.append("Falta la unidad del sensor.")
    elif tipo in UNIDADES_POR_TIPO:
        unidad_normalizada = unidad.lower().replace(" ", "")
        if unidad_normalizada not in UNIDADES_POR_TIPO[tipo]:
            motivos.append(f"Unidad no compatible para '{tipo}': '{unidad}'.")

    return (not motivos), motivos
