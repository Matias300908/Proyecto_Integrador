"""Rol A: normalización y estandarización de registros.

SEMANA 10: implementar las funciones marcadas TODO.
Contrato: recibir un diccionario y devolver una COPIA normalizada.
No modificar el registro original.
"""

def normalizar_registro(registro):
    """Devuelve una copia normalizada sin alterar el registro original."""
    if not isinstance(registro, dict):
        raise TypeError("El registro debe ser un diccionario.")

    normalizado = dict(registro)

    for campo in ("id", "tipo", "unidad"):
        if campo in normalizado and normalizado[campo] is not None:
            normalizado[campo] = str(normalizado[campo]).strip()

    if "valor" in normalizado and normalizado["valor"] is not None:
        normalizado["valor"] = str(normalizado["valor"]).strip()

    if "tipo" in normalizado:
        normalizado["tipo"] = str(normalizado["tipo"]).lower()

    return normalizado
