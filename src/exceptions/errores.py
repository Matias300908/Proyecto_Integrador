
from datetime import datetime
import json


# ==================================================
# SEMANA 11
# EXCEPCIONES, LECTURA Y CONVERSIÓN DE DATOS
# ==================================================


# 1. DEFINICIÓN DE EXCEPCIONES

class DataLabError(Exception):
    """Excepción base de la aplicación."""


class ErrorValidacion(DataLabError):
    """El registro no cumple las reglas de calidad."""


class ErrorFormatoFuente(DataLabError):
    """La estructura de entrada no corresponde al contrato esperado."""


class ErrorLecturaFuente(DataLabError):
    """No fue posible leer una fuente de datos."""


# 2. LECTURA CONTROLADA DE LA FUENTE

def leer_fuente(ruta):

    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            contenido = archivo.read()

        if not contenido.strip():
            raise ErrorFormatoFuente("El archivo está vacío.")

        try:
            datos = json.loads(contenido)

        except json.JSONDecodeError as error:
            raise ErrorFormatoFuente(
                f"El archivo JSON tiene un formato incorrecto: {error}"
            ) from error

        if not isinstance(datos, list):
            raise ErrorFormatoFuente(
                "La fuente debe contener una lista de registros."
            )

        return datos

    except FileNotFoundError as error:
        raise ErrorLecturaFuente(
            f"No se encontró el archivo: {ruta}"
        ) from error

    except PermissionError as error:
        raise ErrorLecturaFuente(
            "No hay permisos para leer el archivo."
        ) from error

    except UnicodeDecodeError as error:
        raise ErrorLecturaFuente(
            "El archivo tiene una codificación incorrecta."
        ) from error

    except OSError as error:
        raise ErrorLecturaFuente(
            f"No fue posible leer el archivo: {error}"
        ) from error


# 3. CONVERSIÓN Y VALIDACIÓN DE CADA REGISTRO

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

    # Conversión de datos

    try:
        identificador = int(registro["id"])
        edad = int(registro["edad"])

    except (ValueError, TypeError) as error:
        raise ErrorValidacion(
            f"Error al convertir los datos: {error}"
        ) from error

    # Validación de identificador

    if identificador <= 0:
        raise ErrorValidacion(
            "El identificador debe ser positivo."
        )

    # Validación de edad

    if edad < 0 or edad > 120:
        raise ErrorValidacion(
            "La edad debe estar entre 0 y 120."
        )

    # Validación de nombre

    if not isinstance(registro["nombre"], str):
        raise ErrorValidacion(
            "El nombre debe ser texto."
        )

    if not registro["nombre"].strip():
        raise ErrorValidacion(
            "El nombre no puede estar vacío."
        )

    # Validación de correo

    correo = registro["correo"]

    if not isinstance(correo, str):
        raise ErrorValidacion(
            "El correo debe ser texto."
        )

    if "@" not in correo or "." not in correo:
        raise ErrorValidacion(
            "El correo electrónico no es válido."
        )

    # Retornar datos convertidos

    registro["id"] = identificador
    registro["edad"] = edad

    return registro


# ==================================================
# SEMANA 12
# CAPTURA, CLASIFICACIÓN Y REPORTE DE ERRORES
# ==================================================


# 4. CONSTRUCCIÓN DEL REPORTE DE ERRORES

def crear_reporte_error(origen, identificador, mensaje,
                        categoria="PROCESAMIENTO"):

    return {
        "origen": origen,
        "identificador": identificador,
        "mensaje": str(mensaje),
        "categoria": str(categoria).strip().upper(),
        "fecha_hora": datetime.now().astimezone().isoformat(),
    }


# 5. PROCESAMIENTO CON CONTINUIDAD POR REGISTRO

def procesar_registros(registros, origen="FUENTE_DATOS"):

    registros_correctos = []
    reportes_errores = []

    for posicion, registro in enumerate(registros, start=1):

        # Obtener identificador del registro

        if isinstance(registro, dict):
            identificador = registro.get(
                "id", f"REGISTRO_{posicion}"
            )
        else:
            identificador = f"REGISTRO_{posicion}"

        try:
            # Validar y convertir el registro

            registro_validado = validar_registro(registro)

            # Guardar registro correcto

            registros_correctos.append(registro_validado)

            print(
                f"Registro {identificador}: "
                "PROCESADO CORRECTAMENTE"
            )

        except ErrorValidacion as error:

            reportes_errores.append(
                crear_reporte_error(
                    origen,
                    identificador,
                    error,
                    "VALIDACION"
                )
            )

            print(
                f"Registro {identificador}: "
                "ERROR DE VALIDACIÓN"
            )

        except ErrorFormatoFuente as error:

            reportes_errores.append(
                crear_reporte_error(
                    origen,
                    identificador,
                    error,
                    "FORMATO"
                )
            )

            print(
                f"Registro {identificador}: "
                "ERROR DE FORMATO"
            )

        except DataLabError as error:

            reportes_errores.append(
                crear_reporte_error(
                    origen,
                    identificador,
                    error,
                    "PROCESAMIENTO"
                )
            )

            print(
                f"Registro {identificador}: "
                "ERROR DE PROCESAMIENTO"
            )

        except Exception as error:

            reportes_errores.append(
                crear_reporte_error(
                    origen,
                    identificador,
                    error,
                    "ERROR_INESPERADO"
                )
            )

            print(
                f"Registro {identificador}: "
                "ERROR INESPERADO"
            )

        # El ciclo continúa con el siguiente registro

    return registros_correctos, reportes_errores


# 6. GENERACIÓN Y ALMACENAMIENTO DEL REPORTE

def mostrar_resultados(correctos, errores):

    print("\n========== RESUMEN DEL PROCESAMIENTO ==========")

    print(f"Registros correctos: {len(correctos)}")
    print(f"Registros con errores: {len(errores)}")

    print("\n========== REGISTROS CORRECTOS ==========")

    for registro in correctos:
        print(registro)

    print("\n========== REPORTE DE ERRORES ==========")

    for reporte in errores:
        print(json.dumps(
            reporte,
            indent=4,
            ensure_ascii=False
        ))

    try:
        with open(
            "reporte_errores.json",
            "w",
            encoding="utf-8"
        ) as archivo:

            json.dump(
                errores,
                archivo,
                indent=4,
                ensure_ascii=False
            )

        print("\nReporte guardado correctamente.")

    except OSError as error:
        print(f"Error al guardar el reporte: {error}")


# ==================================================
# EJECUCIÓN PRINCIPAL DEL PROGRAMA
# ==================================================

def main():

    # Datos de prueba

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
            "edad": "veinticinco",
            "correo": "pedro@gmail.com"
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

    # Procesamiento de registros

    correctos, errores = procesar_registros(registros)

    # Mostrar resultados y generar reporte

    mostrar_resultados(correctos, errores)


# Ejecutar programa

if __name__ == "__main__":
    main()

