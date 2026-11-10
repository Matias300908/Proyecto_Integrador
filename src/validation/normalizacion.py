# Rol A: normalización y estandarización de registros.

# SEMANA 10: implementar las funciones marcadas TODO.
# Contrato: recibir un diccionario y devolver una COPIA normalizada.
# No modificar el registro original.

import math

UNIDADES_CANONICAS = {
    "°c": "°C",
    "ºc": "°C",
    "hpa": "hPa",
    "%": "%",
}


def normalizar_registro(registro):
    if not isinstance(registro, dict):
        raise TypeError("El registro debe ser un diccionario.")

    registro_normalizado = registro.copy()
    for campo in ("id", "tipo", "unidad", "valor"):
        valor = registro_normalizado.get(campo)
        if isinstance(valor, str):
            valor = valor.strip()
            if campo == "tipo":
                valor = valor.lower()
            elif campo == "unidad":
                valor = UNIDADES_CANONICAS.get(valor.casefold(), valor)
            elif campo == "valor":
                try:
                    valor_numerico = float(valor)
                except (TypeError, ValueError, OverflowError):
                    pass
                else:
                    if math.isfinite(valor_numerico):
                        valor = valor_numerico
            registro_normalizado[campo] = valor

    return registro_normalizado
