# Rol A: normalización y estandarización de registros.

# SEMANA 10: implementar las funciones marcadas TODO.
# Contrato: recibir un diccionario y devolver una COPIA normalizada.
# No modificar el registro original.

# REVISIÓN (semanas 10–12) — resumen de cambios. Busque "# REVISIÓN" en el
# archivo para ver el porqué de cada uno:
#   A-1  Las unidades se estandarizan con una tabla de equivalencias
#        ("HPA" -> "hPa", "°c" -> "°C"). Esta tabla ya existía en el commit
#        01f5f2a del Rol A, pero se perdió en el merge e80784a; se recupera.
#   A-2  El id se pasa a MAYÚSCULAS y al tipo se le quitan las tildes
#        ("Presión" -> "presion", que es como aparece en TIPOS_PERMITIDOS).
#   A-3  Un NaN (celda vacía de Excel/pandas) se convierte en None para que
#        la validación lo reporte como "campo faltante" igual que en CSV/JSON.
#   A-6  La coma decimal en un valor de texto ("21,5") se cambia por punto.
#   Se respeta el TODO A-S10-04: el valor NO se convierte a float aquí; la
#   conversión la hace el procesamiento (Rol B) después de validar.

# REVISIÓN A-1: tabla de equivalencias. La clave es la unidad en minúsculas y
# sin espacios; el valor es la forma oficial que espera validaciones.py.
# Para aceptar una variante nueva basta con agregar una línea.
EQUIVALENCIAS_UNIDAD = {
    "°c": "°C",
    "ºc": "°C",       # "º" (ordinal) se confunde a menudo con "°" (grado)
    "c": "°C",
    "celsius": "°C",
    "hpa": "hPa",
    "%": "%",
    "porcentaje": "%",
}

# REVISIÓN A-2: str.maketrans crea una tabla de traducción carácter a
# carácter; translate() la aplica en una sola pasada sobre el texto.
SIN_TILDES = str.maketrans("áéíóúÁÉÍÓÚ", "aeiouAEIOU")


def _es_nan(contenido):
    # REVISIÓN A-3: NaN es el único valor que es distinto de sí mismo.
    # Así se detecta sin importar math ni pandas.
    return isinstance(contenido, float) and contenido != contenido


def normalizar_registro(registro):
    if not isinstance(registro, dict):
        raise TypeError("El registro debe ser un diccionario.")

    # dict.copy() crea un diccionario NUEVO: el original no se modifica (A-S10-04).
    registro_normalizado = registro.copy()
    for campo in ("id", "tipo", "unidad", "valor"):
        valor = registro_normalizado.get(campo)

        # REVISIÓN A-3: NaN -> None (defensa en profundidad: aunque el lector
        # de Excel ya evita los NaN, la calidad no debe depender del origen).
        if _es_nan(valor):
            registro_normalizado[campo] = None
            continue

        if isinstance(valor, str):
            valor = valor.strip()
            if campo == "id":
                # REVISIÓN A-2: "p101" y "P101" son el mismo sensor.
                valor = valor.upper()
            elif campo == "tipo":
                # REVISIÓN A-2: minúsculas y sin tildes.
                valor = valor.lower().translate(SIN_TILDES)
            elif campo == "unidad":
                # REVISIÓN A-1: si la unidad no está en la tabla se deja tal
                # cual llegó y la validación explicará por qué se rechaza.
                # Normalizar NO es aceptar cualquier cosa.
                clave = valor.lower().replace(" ", "")
                valor = EQUIVALENCIAS_UNIDAD.get(clave, valor)
            elif campo == "valor":
                # REVISIÓN A-6: regla conservadora. Solo actúa si hay
                # exactamente una coma y ningún punto ("21,5" -> "21.5").
                # "1.013,2" se deja igual y la validación lo rechaza.
                if valor.count(",") == 1 and "." not in valor:
                    valor = valor.replace(",", ".")
            registro_normalizado[campo] = valor

    return registro_normalizado
