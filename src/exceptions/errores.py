
from datetime import datetime
import json


# ==========================================
# 1. DEFINICIÓN DE EXCEPCIONES
# ==========================================

class DataLabError(Exception):
    """Excepción base de la aplicación."""


class ErrorValidacion(DataLabError):
    """El registro no cumple las reglas de calidad."""


class ErrorFormatoFuente(DataLabError):
    """La estructura de entrada no corresponde al contrato esperado."""


class ErrorLecturaFuente(DataLabError):
    """No fue posible leer una fuente de datos."""


# ==========================================
# 2. REPORTE DE ERRORES
# ==========================================

def crear_reporte_error(origen, identificador, mensaje,
                        categoria="PROCESAMIENTO"):

    return {
        "origen": origen,
        "identificador": identificador,
        "mensaje": str(mensaje),
        "categoria": str(categoria).strip().upper(),
        "fecha_hora": datetime.now().astimezone().isoformat(),
    }


# ==========================================
# 3. LECTURA DE LA FUENTE DE DATOS
# ==========================================

def leer_fuente(ruta):

    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)

        if not isinstance(datos, list):
            raise ErrorFormatoFuente(
                "La fuente debe contener una lista de registros."
            )

        return datos

    except FileNotFoundError as error:
        raise ErrorLecturaFuente(
            f"No se encontró el archivo: {ruta}"
        ) from error

    except json.JSONDecodeError as error:
        raise ErrorFormatoFuente(
            f"El archivo JSON tiene un formato incorrecto: {error}"
        ) from error

    except OSError as error:
        raise ErrorLecturaFuente(
            f"No fue posible leer el archivo: {error}"
        ) from error


# ==========================================
# 4. VALIDACIÓN DE CADA REGISTRO
# ==========================================

def validar_registro(registro):

    if not isinstance(registro, dict):
        raise ErrorFormatoFuente(
            "El registro debe ser un diccionario."
        )

    campos = ["id", "nombre", "edad", "correo"]

    for campo in campos:
        if campo not in registro:
            raise ErrorFormatoFuente(
                f"Falta el campo obligatorio: {campo}"
            )

    if not isinstance(registro["id"], int):
        raise ErrorValidacion("El identificador debe ser entero.")

    if not isinstance(registro["nombre"], str):
        raise ErrorValidacion("El nombre debe ser texto.")

    if not registro["nombre"].strip():
        raise ErrorValidacion("El nombre no puede estar vacío.")

    if not isinstance(registro["edad"], int):
        raise ErrorValidacion("La edad debe ser un número entero.")

    if registro["edad"] < 0 or registro["edad"] > 120:
        raise ErrorValidacion("La edad está fuera del rango permitido.")

    if not isinstance(registro["correo"], str):
        raise ErrorValidacion("El correo debe ser texto.")

    if "@" not in registro["correo"] or "." not in registro["correo"]:
        raise ErrorValidacion("El correo electrónico no es válido.")

    return True


# ==========================================
# 5. PROCESAMIENTO Y CONTINUIDAD POR REGISTRO
# ==========================================

def procesar_registros(registros, origen="FUENTE_DATOS"):

    registros_correctos = []
    reportes_errores = []

    for posicion, registro in enumerate(registros, start=1):

        identificador = (
            registro.get("id", f"REGISTRO_{posicion}")
            if isinstance(registro, dict)
            else f"REGISTRO_{posicion}"
        )

        try:
            # Validar el registro individual
            validar_registro(registro)

            # Si pasa las validaciones, se procesa
            registros_correctos.append(registro)

            print(f"Registro {identificador}: PROCESADO CORRECTAMENTE")

        except ErrorValidacion as error:

            reportes_errores.append(
                crear_reporte_error(
                    origen,
                    identificador,
                    error,
                    "VALIDACION"
                )
            )

            print(f"Registro {identificador}: ERROR DE VALIDACIÓN")

        except ErrorFormatoFuente as error:

            reportes_errores.append(
                crear_reporte_error(
                    origen,
                    identificador,
                    error,
                    "FORMATO"
                )
            )

            print(f"Registro {identificador}: ERROR DE FORMATO")

        except DataLabError as error:

            reportes_errores.append(
                crear_reporte_error(
                    origen,
                    identificador,
                    error,
                    "PROCESAMIENTO"
                )
            )

            print(f"Registro {identificador}: ERROR DE PROCESAMIENTO")

        except Exception as error:

            reportes_errores.append(
                crear_reporte_error(
                    origen,
                    identificador,
                    error,
                    "ERROR_INESPERADO"
                )
            )

            print(f"Registro {identificador}: ERROR INESPERADO")

        # El ciclo continúa con el siguiente registro

    return registros_correctos, reportes_errores


# ==========================================
# 6. GENERACIÓN DEL REPORTE FINAL
# ==========================================

def mostrar_resultados(correctos, errores):

    print("\n========== RESUMEN DEL PROCESAMIENTO ==========")

    print(f"Registros procesados correctamente: {len(correctos)}")
    print(f"Registros con errores: {len(errores)}")

    print("\n========== REGISTROS CORRECTOS ==========")

    for registro in correctos:
        print(registro)

    print("\n========== REPORTE DE ERRORES ==========")

    for reporte in errores:
        print(json.dumps(reporte, indent=4, ensure_ascii=False))

    # Guardar los errores en un archivo JSON
    with open("reporte_errores.json", "w", encoding="utf-8") as archivo:
        json.dump(
            errores,
            archivo,
            indent=4,
            ensure_ascii=False
        )

    print("\nReporte guardado en reporte_errores.json")


# ==========================================
# 7. EJECUCIÓN PRINCIPAL
# ==========================================

def main():

    # Datos de prueba: registros correctos e incorrectos

    registros = [
        {
            "id": 1,
            "nombre": "Laura",
            "edad": 20,
            "correo": "laura@gmail.com"
        },

        {
            "id": 2,
            "nombre": "Carlos",
            "edad": -5,
            "correo": "carlos@gmail.com"
        },

        {
            "id": 3,
            "nombre": "Andrés",
            "edad": 22,
            "correo": "andresgmail.com"
        },

        {
            "id": 4,
            "nombre": "María",
            "edad": 19,
            "correo": "maria@gmail.com"
        },

        {
            "id": 5,
            "nombre": "Pedro",
            "edad": 25
        },

        "Registro con estructura incorrecta",

        {
            "id": 7,
            "nombre": "Sofía",
            "edad": 21,
            "correo": "sofia@gmail.com"
        }
    ]

    print("INICIANDO PROCESAMIENTO DE DATOS...\n")

    correctos, errores = procesar_registros(registros)

    mostrar_resultados(correctos, errores)


if __name__ == "__main__":
    main()
