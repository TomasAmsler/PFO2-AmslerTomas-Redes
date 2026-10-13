"""
PFO 2: Sistema de Gestión de Tareas con API y Base de Datos
Cliente de consola

Programación sobre Redes - 1C 2026

Cliente interactivo que consume la API del servidor (servidor.py):
registrar usuario, iniciar sesión y consultar /tareas.
"""

import requests

# ---------------------------------------------------------------------------
# Configuración general
# ---------------------------------------------------------------------------
URL_BASE = "http://127.0.0.1:5000"
TIMEOUT = 5  # segundos de espera máxima por respuesta

# Session mantiene la cookie de sesión entre peticiones (necesario para
# que /tareas reconozca que ya hicimos login).
sesion = requests.Session()


# ---------------------------------------------------------------------------
# Funciones de comunicación con la API
# ---------------------------------------------------------------------------
def pedir_credenciales():
    """Pide usuario y contraseña por consola."""
    usuario = input("Usuario: ").strip()
    contrasena = input("Contraseña: ")
    return {"usuario": usuario, "contraseña": contrasena}


def enviar_post(ruta, datos):
    """
    Envía un POST con JSON a la API y muestra la respuesta.
    Maneja el caso de servidor caído o sin respuesta.
    """
    try:
        respuesta = sesion.post(f"{URL_BASE}{ruta}", json=datos, timeout=TIMEOUT)
        print(f"[{respuesta.status_code}] {respuesta.json()}")
    except requests.exceptions.ConnectionError:
        print("[ERROR] No se pudo conectar: ¿está corriendo servidor.py?")
    except requests.exceptions.Timeout:
        print("[ERROR] El servidor tardó demasiado en responder.")
    except ValueError:
        print("[ERROR] La respuesta del servidor no es un JSON válido.")


def registrar():
    """Opción 1: POST /registro."""
    enviar_post("/registro", pedir_credenciales())


def iniciar_sesion():
    """Opción 2: POST /login."""
    enviar_post("/login", pedir_credenciales())


def ver_tareas():
    """Opción 3: GET /tareas (muestra el HTML o el error de acceso)."""
    try:
        respuesta = sesion.get(f"{URL_BASE}/tareas", timeout=TIMEOUT)
        print(f"[{respuesta.status_code}]")
        print(respuesta.text)
    except requests.exceptions.ConnectionError:
        print("[ERROR] No se pudo conectar: ¿está corriendo servidor.py?")
    except requests.exceptions.Timeout:
        print("[ERROR] El servidor tardó demasiado en responder.")


# ---------------------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------------------
def mostrar_menu():
    """Imprime el menú de opciones."""
    print("\n=== Gestión de Tareas ===")
    print("1. Registrar usuario")
    print("2. Iniciar sesión")
    print("3. Ver tareas")
    print("4. Salir")


def main():
    """Bucle principal del menú."""
    acciones = {"1": registrar, "2": iniciar_sesion, "3": ver_tareas}

    while True:
        mostrar_menu()
        opcion = input("Elegí una opción: ").strip()

        if opcion == "4":
            print("Hasta luego.")
            break
        elif opcion in acciones:
            acciones[opcion]()
        else:
            print("Opción inválida.")


if __name__ == "__main__":
    main()
