import math
import unittest

from src.validation.normalizacion import normalizar_registro
from src.validation.validaciones import validar_registro


class TestNormalizarRegistro(unittest.TestCase):
    def test_normaliza_una_copia_sin_alterar_el_original(self):
        original = {
            "id": " T001 ",
            "tipo": " TEMPERATURA ",
            "valor": " 22.5 ",
            "unidad": " °C ",
            "origen": " sensor ",
        }

        normalizado = normalizar_registro(original)

        self.assertEqual(
            normalizado,
            {
                "id": "T001",
                "tipo": "temperatura",
                "valor": 22.5,
                "unidad": "°C",
                "origen": " sensor ",
            },
        )
        self.assertIsNot(normalizado, original)
        self.assertEqual(original["tipo"], " TEMPERATURA ")
        self.assertEqual(original["valor"], " 22.5 ")

    def test_rechaza_entradas_que_no_son_diccionarios(self):
        with self.assertRaises(TypeError):
            normalizar_registro([])

    def test_convierte_valores_numericos_textuales_a_float(self):
        for valor, esperado in (("22", 22.0), (" 22.5 ", 22.5), ("-3e2", -300.0)):
            with self.subTest(valor=valor):
                normalizado = normalizar_registro({"valor": valor})

                self.assertEqual(normalizado["valor"], esperado)
                self.assertIsInstance(normalizado["valor"], float)

    def test_conserva_como_texto_valores_no_numericos_o_no_finitos(self):
        for valor in (" N/D ", " NaN ", " inf ", " texto ", " "):
            with self.subTest(valor=valor):
                normalizado = normalizar_registro({"valor": valor})

                self.assertEqual(normalizado["valor"], valor.strip())
                self.assertIsInstance(normalizado["valor"], str)

    def test_normaliza_variantes_simples_de_unidad(self):
        original = {"id": "T001", "tipo": "temperatura", "valor": 22, "unidad": " ºc "}

        normalizado = normalizar_registro(original)

        self.assertEqual(normalizado["unidad"], "°C")
        self.assertEqual(original["unidad"], " ºc ")


class TestValidarRegistro(unittest.TestCase):
    def test_acepta_unidades_y_valores_numericos_de_los_tres_tipos(self):
        casos = (
            ("temperatura", 22.5, "°C"),
            ("presion", 1010, "hPa"),
            ("humedad", 225, "%"),
        )
        for tipo, valor, unidad in casos:
            with self.subTest(tipo=tipo):
                registro = {"id": "S001", "tipo": tipo, "valor": valor, "unidad": unidad}
                self.assertEqual(validar_registro(registro), (True, []))

    def test_acepta_valor_numerico_textual_despues_de_normalizar(self):
        registro = {
            "id": "T001",
            "tipo": "temperatura",
            "valor": " 22.5 ",
            "unidad": "°C",
        }

        self.assertEqual(validar_registro(registro), (True, []))

    def test_reporta_todos_los_campos_obligatorios_vacios(self):
        es_valido, motivos = validar_registro({})

        self.assertFalse(es_valido)
        self.assertEqual(len(motivos), 4)
        for campo in ("id", "tipo", "valor", "unidad"):
            self.assertTrue(any(f"'{campo}'" in motivo for motivo in motivos))

    def test_rechaza_tipo_no_permitido_y_valor_no_numerico(self):
        es_valido, motivos = validar_registro(
            {"id": "X001", "tipo": "sensor", "valor": "N/D", "unidad": "x"}
        )

        self.assertFalse(es_valido)
        self.assertTrue(any("Tipo no permitido" in motivo for motivo in motivos))
        self.assertTrue(any("numérico" in motivo for motivo in motivos))

    def test_rechaza_valores_no_finitos_y_booleanos(self):
        for valor in (math.nan, math.inf, -math.inf, True):
            with self.subTest(valor=valor):
                registro = {
                    "id": "T001",
                    "tipo": "temperatura",
                    "valor": valor,
                    "unidad": "°C",
                }
                self.assertFalse(validar_registro(registro)[0])

    def test_explica_marcadores_de_valor_faltante(self):
        for valor in ("N/D", " ERROR ", "sin lectura", "?"):
            with self.subTest(valor=valor):
                registro = {
                    "id": "T001",
                    "tipo": "temperatura",
                    "valor": valor,
                    "unidad": "°C",
                }

                es_valido, motivos = validar_registro(registro)

                self.assertFalse(es_valido)
                self.assertTrue(any("dato faltante" in motivo for motivo in motivos))

    def test_reporta_tipos_incorrectos_de_campos(self):
        registro = {"id": 12, "tipo": [], "valor": 22, "unidad": 5}

        es_valido, motivos = validar_registro(registro)

        self.assertFalse(es_valido)
        for campo in ("id", "tipo", "unidad"):
            self.assertTrue(any(f"'{campo}' debe ser texto" in motivo for motivo in motivos))

    def test_informa_cuando_el_valor_no_es_numerico_o_no_es_finito(self):
        casos = (
            ("texto", "debe ser numérico"),
            (math.inf, "debe ser finito"),
            ("inf", "debe ser finito"),
        )
        for valor, parte_mensaje in casos:
            with self.subTest(valor=valor):
                registro = {
                    "id": "T001",
                    "tipo": "temperatura",
                    "valor": valor,
                    "unidad": "°C",
                }

                es_valido, motivos = validar_registro(registro)

                self.assertFalse(es_valido)
                self.assertTrue(any(parte_mensaje in motivo for motivo in motivos))

    def test_rechaza_unidad_incorrecta(self):
        es_valido, motivos = validar_registro(
            {"id": "T001", "tipo": "temperatura", "valor": 22, "unidad": "hPa"}
        )

        self.assertFalse(es_valido)
        self.assertTrue(any("Unidad no válida" in motivo for motivo in motivos))

    def test_rechaza_registro_no_diccionario(self):
        es_valido, motivos = validar_registro(None)

        self.assertFalse(es_valido)
        self.assertTrue(motivos)


if __name__ == "__main__":
    unittest.main()