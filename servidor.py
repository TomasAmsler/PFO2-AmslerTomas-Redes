"""
PFO 2: Sistema de Gestión de Tareas con API y Base de Datos
Servidor (API Flask + SQLite)

Programación sobre Redes - 1C 2026

Endpoints:
    POST /registro  -> registra un usuario (contraseña hasheada)
    POST /login     -> verifica credenciales e inicia sesión
    GET  /tareas    -> muestra un HTML de bienvenida (requiere login)
"""

import sqlite3

from flask import Flask, jsonify, request, session
from markupsafe import escape
from werkzeug.security import check_password_hash, generate_password_hash

# ---------------------------------------------------------------------------
# Configuración general
# ---------------------------------------------------------------------------
DB_NAME = "tareas.db"     # Archivo de la base de datos SQLite
HOST = "127.0.0.1"        # Dirección donde escucha el servidor
PORT = 5000               # Puerto donde escucha el servidor

app = Flask(__name__)

# Clave usada por Flask para firmar la cookie de sesión.
# En un proyecto real debe ser secreta y venir de una variable de entorno.
app.secret_key = "clave-secreta-solo-para-el-tp"


# ---------------------------------------------------------------------------
# Base de datos
# ---------------------------------------------------------------------------
def obtener_conexion():
    """Abre y devuelve una conexión a la base de datos SQLite."""
    return sqlite3.connect(DB_NAME)


def inicializar_db():
    """
    Crea la tabla 'usuarios' si no existe.
    Campos: id, usuario (único) y contraseña (guardada como hash).
    """
    conexion = obtener_conexion()
    try:
        conexion.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            )
        """)
        conexion.commit()
        print(f"[DB] Base de datos '{DB_NAME}' lista para usarse.")
    finally:
        conexion.close()


def crear_usuario(usuario, password_hash):
    """
    Inserta un usuario nuevo. Usa consulta parametrizada (?) para evitar
    inyección SQL.
    Retorna True si se creó, False si el usuario ya existía.
    """
    conexion = obtener_conexion()
    try:
        conexion.execute(
            "INSERT INTO usuarios (usuario, password_hash) VALUES (?, ?)",
            (usuario, password_hash),
        )
        conexion.commit()
        return True
    except sqlite3.IntegrityError:
        # La columna 'usuario' es UNIQUE: ya existe ese nombre
        return False
    finally:
        conexion.close()


def buscar_hash_usuario(usuario):
    """Devuelve el hash guardado para un usuario, o None si no existe."""
    conexion = obtener_conexion()
    try:
        fila = conexion.execute(
            "SELECT password_hash FROM usuarios WHERE usuario = ?",
            (usuario,),
        ).fetchone()
        return fila[0] if fila else None
    finally:
        conexion.close()


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
def leer_credenciales():
    """
    Extrae 'usuario' y 'contraseña' del JSON de la petición.
    Retorna (usuario, contraseña) o (None, None) si faltan o son inválidos.
    """
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        return None, None

    usuario = datos.get("usuario")
    contrasena = datos.get("contraseña")

    if not isinstance(usuario, str) or not isinstance(contrasena, str):
        return None, None
    if usuario.strip() == "" or contrasena == "":
        return None, None

    return usuario.strip(), contrasena


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.route("/registro", methods=["POST"])
def registro():
    """
    POST /registro
    Recibe {"usuario": "nombre", "contraseña": "1234"}.
    Guarda el usuario con la contraseña hasheada (nunca en texto plano).
    """
    usuario, contrasena = leer_credenciales()
    if usuario is None:
        return jsonify({"error": "Se requiere JSON con 'usuario' y 'contraseña'"}), 400

    # Hasheamos la contraseña (incluye salt aleatorio automáticamente)
    password_hash = generate_password_hash(contrasena)

    try:
        creado = crear_usuario(usuario, password_hash)
    except sqlite3.Error as error:
        print(f"[DB] Error al registrar usuario: {error}")
        return jsonify({"error": "Error interno de la base de datos"}), 500

    if not creado:
        return jsonify({"error": "El usuario ya existe"}), 409

    return jsonify({"mensaje": f"Usuario '{usuario}' registrado correctamente"}), 201


@app.route("/login", methods=["POST"])
def login():
    """
    POST /login
    Verifica las credenciales. Si son correctas, guarda al usuario en la
    sesión (cookie firmada) para permitir el acceso a /tareas.
    """
    usuario, contrasena = leer_credenciales()
    if usuario is None:
        return jsonify({"error": "Se requiere JSON con 'usuario' y 'contraseña'"}), 400

    try:
        password_hash = buscar_hash_usuario(usuario)
    except sqlite3.Error as error:
        print(f"[DB] Error al buscar usuario: {error}")
        return jsonify({"error": "Error interno de la base de datos"}), 500

    # Mismo mensaje si el usuario no existe o la clave es incorrecta,
    # para no revelar qué usuarios están registrados.
    if password_hash is None or not check_password_hash(password_hash, contrasena):
        return jsonify({"error": "Usuario o contraseña incorrectos"}), 401

    session["usuario"] = usuario
    return jsonify({"mensaje": f"Bienvenido, {usuario}. Login exitoso"}), 200


@app.route("/tareas", methods=["GET"])
def tareas():
    """
    GET /tareas
    Devuelve un HTML de bienvenida. Solo accesible si hubo login previo.
    """
    usuario = session.get("usuario")
    if usuario is None:
        return jsonify({"error": "Debes iniciar sesión en /login primero"}), 401

    # escape() evita que un nombre de usuario con HTML/JS se ejecute (XSS)
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Gestión de Tareas</title>
</head>
<body>
    <h1>¡Bienvenido, {escape(usuario)}!</h1>
    <p>Este es tu sistema de gestión de tareas.</p>
</body>
</html>"""
    return html, 200, {"Content-Type": "text/html; charset=utf-8"}


# ---------------------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    inicializar_db()
    app.run(host=HOST, port=PORT, debug=False)
