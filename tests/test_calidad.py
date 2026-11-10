from src.processing.procesamiento import procesar_registros
from src.validation.normalizacion import normalizar_registro
from src.validation.validaciones import validar_registro


def test_normalizar_registro_devuelve_copia_y_normaliza_campos():
    registro = {"id": "  T001  ", "tipo": " TEMPERATURA ", "valor": " 25.0 ", "unidad": " °C "}

    copia = normalizar_registro(registro)

    assert copia == {"id": "T001", "tipo": "temperatura", "valor": "25.0", "unidad": "°C"}
    assert registro == {"id": "  T001  ", "tipo": " TEMPERATURA ", "valor": " 25.0 ", "unidad": " °C "}


def test_validar_registro_devuelve_todos_los_motivos():
    registro = {"id": "  ", "tipo": "velocidad", "valor": "abc", "unidad": "m/s"}

    es_valido, motivos = validar_registro(registro)

    assert es_valido is False
    assert any("id" in motivo.lower() for motivo in motivos)
    assert any("tipo" in motivo.lower() for motivo in motivos)
    assert any("valor" in motivo.lower() for motivo in motivos)
    assert any("unidad" in motivo.lower() for motivo in motivos)


def test_procesar_registros_separa_validos_e_invalidos():
    registros = [
        {"id": "T001", "tipo": "temperatura", "valor": " 17.5 ", "unidad": "°C"},
        {"id": "X999", "tipo": "velocidad", "valor": "98", "unidad": "m/s"},
    ]

    resultado = procesar_registros(registros)

    assert len(resultado["registros_validos"]) == 1
    assert resultado["registros_validos"][0]["clasificacion"] == "BAJO"
    assert len(resultado["registros_invalidos"]) == 1
    assert resultado["registros_invalidos"][0]["motivos"]
