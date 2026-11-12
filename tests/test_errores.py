from datetime import datetime

from src.exceptions.errores import crear_reporte_error
from src.processing import procesamiento
from src.processing.procesamiento import procesar_registros


def test_crear_reporte_error_conserva_contexto_y_agrega_fecha_hora():
    reporte = crear_reporte_error(
        "archivo.csv",
        "T001",
        "No se pudo convertir el valor original: 'x'",
        categoria="lectura",
    )

    assert reporte["origen"] == "archivo.csv"
    assert reporte["identificador"] == "T001"
    assert reporte["mensaje"] == "No se pudo convertir el valor original: 'x'"
    assert reporte["categoria"] == "LECTURA"
    fecha_hora = datetime.fromisoformat(reporte["fecha_hora"])
    assert fecha_hora.tzinfo is not None


def test_procesar_registros_continua_despues_de_un_error_tecnico(monkeypatch):
    clasificacion_original = procesamiento.clasificar_valor

    def clasificar_con_falla(valor, tipo):
        if valor == 2:
            raise RuntimeError("Falla inesperada en clasificación")
        return clasificacion_original(valor, tipo)

    monkeypatch.setattr(procesamiento, "clasificar_valor", clasificar_con_falla)
    registros = [
        {"id": "T001", "tipo": "temperatura", "valor": "1", "unidad": "°C"},
        {"id": "T002", "tipo": "temperatura", "valor": "2", "unidad": "°C"},
        {"id": "T003", "tipo": "temperatura", "valor": "3", "unidad": "°C"},
    ]

    resultado = procesar_registros(registros)

    assert [registro["id"] for registro in resultado["registros_validos"]] == ["T001", "T003"]
    assert resultado["errores"][0]["identificador"] == "T002"
    assert resultado["errores"][0]["mensaje"] == "Falla inesperada en clasificación"
    assert resultado["registros_invalidos"][0]["registro"] == registros[1]
