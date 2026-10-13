# PFO 2: Sistema de Gestión de Tareas con API y Base de Datos

Programación sobre Redes - 1C 2026

API REST desarrollada con **Flask** y **SQLite**, con registro de usuarios
(contraseñas hasheadas), inicio de sesión y una ruta de bienvenida en HTML.
Incluye un cliente de consola para consumir la API.

## Archivos

| Archivo            | Descripción                                          |
|--------------------|------------------------------------------------------|
| `servidor.py`      | API Flask + SQLite (código fuente principal)         |
| `cliente.py`       | Cliente en consola que interactúa con la API         |
| `requirements.txt` | Dependencias del proyecto                            |
| `docs/index.html`  | Página estática para GitHub Pages                    |
| `capturas/`        | Capturas de pantalla de las pruebas exitosas         |
| `tareas.db`        | Base de datos (se crea sola al iniciar el servidor)  |

## Endpoints

| Método | Ruta        | Descripción                                                        |
|--------|-------------|--------------------------------------------------------------------|
| POST   | `/registro` | Recibe `{"usuario": "nombre", "contraseña": "1234"}` y lo guarda con la contraseña hasheada |
| POST   | `/login`    | Verifica las credenciales y habilita el acceso a las tareas        |
| GET    | `/tareas`   | Muestra un HTML de bienvenida (requiere haber hecho login)         |

## Requisitos

- Python 3.9 o superior
- Librerías: `Flask` y `requests` (la de hasheo, `werkzeug.security`, viene incluida con Flask)

## Cómo ejecutar el proyecto

1. Instalar las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

2. Iniciar el servidor (queda corriendo en `http://127.0.0.1:5000`):

   ```bash
   python servidor.py
   ```

3. En **otra terminal**, ejecutar el cliente de consola:

   ```bash
   python cliente.py
   ```

> En Windows usar `python`. En Linux/Mac puede ser `python3`.

## Cómo probarlo

### Opción A: con el cliente de consola

Ejecutar `python cliente.py` y seguir el menú: **1** registrar usuario,
**2** iniciar sesión, **3** ver tareas.

### Opción B: con curl

```bash
# 1. Registrar usuario
curl -X POST http://127.0.0.1:5000/registro \
     -H "Content-Type: application/json" \
     -d '{"usuario":"tomas","contraseña":"1234"}'

# 2. Login (guarda la cookie de sesión en cj.txt)
curl -c cj.txt -X POST http://127.0.0.1:5000/login \
     -H "Content-Type: application/json" \
     -d '{"usuario":"tomas","contraseña":"1234"}'

# 3. Ver tareas (usa la cookie guardada)
curl -b cj.txt http://127.0.0.1:5000/tareas
```

### Respuestas esperadas

| Prueba                         | Código | Resultado                                   |
|--------------------------------|--------|---------------------------------------------|
| Registro correcto              | 201    | `Usuario 'tomas' registrado correctamente`  |
| Registro con usuario repetido  | 409    | `El usuario ya existe`                      |
| Registro sin usuario/contraseña| 400    | Mensaje de error de formato                 |
| Login correcto                 | 200    | `Bienvenido, tomas. Login exitoso`          |
| Login con clave incorrecta     | 401    | `Usuario o contraseña incorrectos`          |
| `/tareas` sin login            | 401    | `Debes iniciar sesión en /login primero`    |
| `/tareas` con login            | 200    | HTML de bienvenida                          |

## Capturas de pantalla de pruebas exitosas

Las capturas se encuentran en la carpeta [`capturas/`](capturas/).

<!-- Reemplazar por los nombres reales de tus imágenes, por ejemplo:
![Registro](capturas/01_registro.png)
![Login](capturas/02_login.png)
![Tareas](capturas/03_tareas.png)
![Hash en la base](capturas/04_base_de_datos.png)
-->

## Seguridad aplicada

- Las contraseñas **nunca** se guardan en texto plano: se almacenan como hash
  (`werkzeug.security.generate_password_hash`, algoritmo scrypt con salt aleatorio).
- Las consultas SQL son **parametrizadas** (`?`), lo que evita la inyección SQL.
- El nombre de usuario se **escapa** al mostrarlo en el HTML, evitando XSS.
- Login y usuario inexistente devuelven el mismo mensaje de error, para no
  revelar qué usuarios están registrados.

## Respuestas conceptuales

### ¿Por qué hashear contraseñas?

Porque si la base de datos se filtra o alguien accede a ella, las contraseñas
no quedan expuestas. Un **hash** es una función de un solo sentido: a partir
de la contraseña se obtiene un valor, pero de ese valor no se puede recuperar
la contraseña original. Al iniciar sesión, el servidor hashea lo que ingresó el
usuario y compara los hashes; nunca necesita conocer ni guardar la contraseña
real.

Además, librerías como Werkzeug agregan un **salt** (dato aleatorio) distinto
por usuario, de modo que dos personas con la misma contraseña tienen hashes
diferentes, y se usan algoritmos deliberadamente **lentos** (scrypt, bcrypt)
que dificultan los ataques de fuerza bruta y de tablas precalculadas. Guardar
contraseñas en texto plano implicaría que cualquier filtración (o incluso un
administrador de la base) pueda ver y reutilizar las credenciales, que muchas
personas repiten en otros servicios.

### Ventajas de usar SQLite en este proyecto

- **Sin servidor aparte**: es una base embebida; no hay que instalar ni
  configurar un motor como MySQL o PostgreSQL.
- **Un solo archivo** (`tareas.db`): fácil de crear, copiar, respaldar y
  entregar junto con el proyecto.
- **Viene incluida en Python** (módulo `sqlite3`): no requiere dependencias
  extra.
- **Persistencia real**: los datos se conservan aunque se reinicie el servidor.
- **Ideal para proyectos pequeños y de aprendizaje**: tiene bajo consumo de
  recursos, soporta SQL estándar y transacciones (ACID), y es suficiente para
  la carga de este sistema.
