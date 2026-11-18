# Rol A: reglas de validación de calidad de registros.

# REVISIÓN (semanas 10–12) — resumen de cambios. Busque "# REVISIÓN":
#   A-3  Un NaN cuenta como campo VACÍO (mismo motivo venga de CSV, JSON o Excel).
#   A-4  Rangos plausibles por tipo: 999 °C o 150 % son números bien escritos,
#        pero no mediciones creíbles. Antes pasaban como válidos.
#   A-5  Tipo, unidad o id que no son texto: motivo claro, nunca una excepción.
#   A-7  Se recuperan los marcadores de dato faltante (N/A, SIN_DATO, ...) y los
#        motivos detallados del commit 01f5f2a, que se perdieron en el merge
#        e80784a.
#   A-8  Formato de los motivos: "<descripción general>: <detalle>". La interfaz
#        agrupa los motivos por el texto anterior a ":", así la gráfica
#        "Motivos de rechazo" muestra pocas barras y fáciles de leer.
import math

from src.validation.normalizacion import normalizar_registro

TIPOS_PERMITIDOS = {"temperatura", "presion", "humedad"}
UNIDADES_POR_TIPO = {
    "temperatura": "°C",
    "presion": "hPa",
    "humedad": "%",
}

# REVISIÓN A-4: rango PLAUSIBLE (¿el dato es creíble?). No es la clasificación
# BAJO/NORMAL/ALTO, que sigue centralizada en clasificar_valor(). Los límites
# salen del análisis de los datasets: las lecturas normales están entre 2 y
# 42 °C, entre 851 y 1080 hPa y entre 5 y 95 %; todas las incidencias
# extremas (999, -25, 75 °C; 650, 1500 hPa; -15, 150 %) quedan por fuera.
# Si el docente decide no rechazar extremos, basta con vaciar este diccionario.
RANGOS_PLAUSIBLES = {
    "temperatura": (-10.0, 50.0),
    "presion": (800.0, 1100.0),
    "humedad": (0.0, 100.0),
}

# REVISIÓN A-7: textos que en los datasets significan "no hay medición".
# Se comparan en minúsculas. Recuperado del commit 01f5f2a y ampliado con
# "error_sensor", que aparece en los tres archivos.
MARCADORES_VALOR_FALTANTE = {
    "n/d", "nd", "na", "n/a", "nan", "null", "none",
    "sin_dato", "sin dato", "sin lectura", "desconocido",
    "?", "-", "pendiente", "error", "error_sensor",
}


def _esta_vacio(contenido):
    """True si el campo no tiene contenido útil."""
    if contenido is None:
        return True
    # REVISIÓN A-3: NaN es el único valor distinto de sí mismo.
    if isinstance(contenido, float) and contenido != contenido:
        return True
    return isinstance(contenido, str) and not contenido.strip()


def validar_registro(registro):
    """Contrato: devuelve (es_valido: bool, motivos: list[str]).

    Acumula TODOS los motivos encontrados (A-S10-09), no solo el primero.
    """
    if not isinstance(registro, dict):
        return False, ["El registro debe ser un diccionario."]

    # La validación normaliza por su cuenta: así da el mismo resultado aunque
    # quien la llame haya olvidado normalizar antes.
    registro = normalizar_registro(registro)
    motivos = []

    # 1) Campos obligatorios (A-S10-05).
    for campo in ("id", "tipo", "valor", "unidad"):
        if _esta_vacio(registro.get(campo)):
            motivos.append(f"El campo '{campo}' es obligatorio.")

    # REVISIÓN A-5: el id debe ser texto (regla del commit 01f5f2a).
    identificador = registro.get("id")
    if not _esta_vacio(identificador) and not isinstance(identificador, str):
        motivos.append(f"El campo 'id' debe ser texto: {identificador!r}")

    # 2) Tipo permitido (A-S10-06).
    tipo = registro.get("tipo")
    # REVISIÓN A-5: isinstance va PRIMERO. Si tipo fuera una lista,
    # "tipo in TIPOS_PERMITIDOS" lanzaría TypeError (una lista no es hashable).
    # El operador "and" evalúa en cortocircuito y evita ese caso.
    tipo_valido = isinstance(tipo, str) and tipo in TIPOS_PERMITIDOS
    if not _esta_vacio(tipo) and not tipo_valido:
        if isinstance(tipo, str):
            motivos.append(f"Tipo no permitido: {tipo!r}")
        else:
            motivos.append(f"El campo 'tipo' debe ser texto: {tipo!r}")

    # 3) Formato numérico (A-S10-07).
    valor = registro.get("valor")
    numero = None  # quedará con el número si el valor es correcto
    if not _esta_vacio(valor):
        if isinstance(valor, str) and valor.lower() in MARCADORES_VALOR_FALTANTE:
            # REVISIÓN A-7: motivo específico para "N/A", "SIN_DATO", ...
            motivos.append(f"El campo 'valor' contiene un marcador de dato faltante: {valor!r}")
        elif isinstance(valor, bool):
            # True/False son int en Python: hay que rechazarlos explícitamente.
            motivos.append(f"El campo 'valor' no puede ser booleano: {valor!r}")
        else:
            try:
                numero = float(valor)
            except (TypeError, ValueError, OverflowError):
                motivos.append(f"El campo 'valor' no es numérico: {valor!r}")
            else:
                if not math.isfinite(numero):
                    motivos.append(f"El campo 'valor' debe ser finito: {valor!r}")
                    numero = None

    # 4) Unidad según el tipo (A-S10-08).
    unidad = registro.get("unidad")
    if not _esta_vacio(unidad):
        if not isinstance(unidad, str):
            motivos.append(f"El campo 'unidad' debe ser texto: {unidad!r}")
        elif tipo_valido and unidad != UNIDADES_POR_TIPO[tipo]:
            motivos.append(
                f"Unidad no válida para '{tipo}': se esperaba "
                f"'{UNIDADES_POR_TIPO[tipo]}' y se recibió {unidad!r}"
            )

    # 5) REVISIÓN A-4: rango plausible. Solo tiene sentido si el tipo es
    # conocido y el valor ya es un número finito (por eso se usa "numero").
    if tipo_valido and numero is not None and tipo in RANGOS_PLAUSIBLES:
        minimo, maximo = RANGOS_PLAUSIBLES[tipo]
        if numero < minimo or numero > maximo:
            motivos.append(
                f"Valor fuera del rango plausible para {tipo}: {numero:g} "
                f"(admitido de {minimo:g} a {maximo:g} {UNIDADES_POR_TIPO[tipo]})"
            )

    # A-S10-09: la lista vacía significa "sin motivos" -> registro válido.
    return not motivos, motivos
