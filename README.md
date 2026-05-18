# TalaTrivia

API REST para gestionar un juego de trivia sobre temas de recursos humanos. Permite crear usuarios, preguntas y trivias, gestionar participaciones y generar rankings.

## Tecnologías

- Python 3.11
- Django 4.2
- Django REST Framework
- PostgreSQL (Docker) / SQLite (local)
- Docker + Docker Compose

## Estructura del proyecto

```
talana-trivia/
├── apps/
│   ├── users/        # Gestión de usuarios y autenticación
│   ├── questions/    # Preguntas y respuestas
│   └── trivias/      # Trivias, participación y ranking
├── talana_trivia/    # Configuración del proyecto
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── requirements.txt
```

## Roles

| Rol | Descripción |
|-----|-------------|
| `admin` | Gestiona usuarios, preguntas y trivias |
| `player` | Participa en trivias asignadas |

## Levantar el proyecto

### Con Docker (recomendado)

1. Crea tu archivo de variables de entorno a partir de la plantilla:
   ```bash
   cp .env.example .env
   ```
   > `.env.example` es una plantilla que se incluye en el repositorio. El archivo `.env` es el que la aplicación realmente lee, y **no se sube al repo** porque contiene secretos. Por eso debes crearlo localmente a partir de la plantilla.

   Luego genera una `SECRET_KEY` segura y reemplaza el valor en tu `.env`:

   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

2. Levanta los contenedores:
   ```bash
   docker compose up --build
   ```

3. La API estará disponible en `http://localhost:8000`

Las migraciones y el seed de datos iniciales se ejecutan automáticamente al iniciar el contenedor.

---

### Sin Docker (local)

1. Crea y activa un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Configura las variables de entorno. Copia el `.env.example`:
   ```bash
   cp .env.example .env
   ```

   > **Importante:** para correr en local con SQLite, deja `DB_HOST` vacío en el `.env`:
   > ```
   > DB_HOST=
   > ```
   > Esto hace que Django ignore la configuración de PostgreSQL y use SQLite por defecto.

4. Aplica las migraciones:
   ```bash
   python manage.py migrate
   ```

5. Carga los datos iniciales:
   ```bash
   python manage.py seed
   ```

6. Levanta el servidor:
   ```bash
   python manage.py runserver
   ```

7. La API estará disponible en `http://localhost:8000`

---

## Datos precargados

El comando `seed` (ejecutado automáticamente con Docker, o manualmente en local) crea:

| Rol    | Email                  | Contraseña |
| ------ | ---------------------- | ---------- |
| Admin  | `admin@talana.com`     | admin123   |
| Player | `ussop@onepiece.com`   | ussop123   |
| Player | `nami@onepiece.com`    | nami123    |

También crea una trivia **"Trivia One Piece"** con 3 preguntas (fácil, media y difícil) asignada a ambos jugadores, lista para probar el flujo completo.

El comando es idempotente — si los datos ya existen, los omite sin error.

---

## Correr los tests

```bash
pytest
```

Los tests usan SQLite en memoria, por lo que no requieren Docker ni configuración adicional.

---

## Documentación de endpoints

Ver [API_DOCS.md](API_DOCS.md) para la documentación completa de todos los endpoints.
