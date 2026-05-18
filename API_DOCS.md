# TalaTrivia API Documentation

API REST para gestionar un juego de trivia sobre temas de recursos humanos. Permite crear usuarios, preguntas, trivias y registrar participaciones con puntajes.

---

## Autenticación

La API usa **Token Authentication**. Luego de hacer login, incluir el token en el header de cada request:

```
Authorization: Token <token>
```

---

## Roles

| Rol | Descripción |
|-----|-------------|
| `admin` | Gestiona usuarios, preguntas y trivias |
| `player` | Participa en trivias asignadas |

---

## Usuarios

### `POST /register/`
Registra un nuevo jugador. El rol siempre es `player`.

**Body:**
```json
{
  "name": "Juan Pérez",
  "email": "juan@example.com",
  "password": "segura123"
}
```

**Response `201`:**
```json
{
  "id": 1,
  "name": "Juan Pérez",
  "email": "juan@example.com",
  "role": "player"
}
```

---

### `POST /login/`
Autentica un usuario y retorna su token.

**Body:**
```json
{
  "email": "juan@example.com",
  "password": "segura123"
}
```

**Response `200`:**
```json
{
  "token": "abc123def456..."
}
```

**Response `401`:** Credenciales inválidas.

---

### `GET /users/` — Admin
Lista todos los usuarios.

**Response `200`:**
```json
[
  { "id": 1, "name": "Juan Pérez", "email": "juan@example.com", "role": "player" }
]
```

---

### `POST /users/` — Admin
Crea un usuario con rol específico.

**Body:**
```json
{
  "name": "Admin Talana",
  "email": "admin@talana.com",
  "password": "admin123",
  "role": "admin"
}
```

---

### `GET /users/players/` — Admin
Lista solo usuarios con rol `player`.

---

### `GET /users/admins/` — Admin
Lista solo usuarios con rol `admin`.

---

### `GET /users/<id>/` — Admin o el propio usuario
Retorna el detalle de un usuario.

---

### `PUT /users/<id>/` — Admin o el propio usuario
Actualiza parcialmente un usuario.

**Body (todos opcionales):**
```json
{
  "name": "Nuevo Nombre",
  "email": "nuevo@email.com",
  "password": "nuevapass"
}
```

---

### `DELETE /users/<id>/` — Admin
Elimina un usuario.

---

## Preguntas

### `GET /questions/` — Admin
Lista todas las preguntas con sus opciones de respuesta.

**Response `200`:**
```json
[
  {
    "id": 1,
    "text": "¿Qué es el onboarding?",
    "difficult_level": "easy",
    "answers": [
      { "id": 1, "text": "Proceso de incorporación", "is_correct": true },
      { "id": 2, "text": "Proceso de desvinculación", "is_correct": false }
    ]
  }
]
```

---

### `POST /questions/` — Admin
Crea una pregunta, opcionalmente con sus respuestas.

**Body:**
```json
{
  "text": "¿Qué es el onboarding?",
  "difficult_level": "easy",
  "answers": [
    { "text": "Proceso de incorporación", "is_correct": true },
    { "text": "Proceso de desvinculación", "is_correct": false },
    { "text": "Evaluación de desempeño", "is_correct": false }
  ]
}
```

> `difficult_level` acepta: `easy`, `medium`, `hard`. Por defecto `easy`.
> Solo una respuesta puede tener `is_correct: true`.

---

### `GET /questions/<id>/` — Admin
Retorna el detalle de una pregunta con sus respuestas.

---

### `PUT /questions/<id>/` — Admin
Actualiza parcialmente una pregunta.

**Body (todos opcionales):**
```json
{
  "text": "Nuevo enunciado",
  "difficult_level": "medium"
}
```

---

### `DELETE /questions/<id>/` — Admin
Elimina una pregunta y sus respuestas.

---

### `POST /questions/<question_id>/answers/` — Admin
Agrega una respuesta a una pregunta existente.

**Body:**
```json
{
  "text": "Nueva opción",
  "is_correct": false
}
```

---

### `PUT /questions/<question_id>/answers/<answer_id>/` — Admin
Actualiza el texto de una respuesta.

**Body:**
```json
{
  "text": "Texto actualizado"
}
```

---

### `DELETE /questions/<question_id>/answers/<answer_id>/` — Admin
Elimina una respuesta.

---

## Trivias

### `GET /trivias/` — Admin
Lista todas las trivias (sin preguntas ni participantes).

**Response `200`:**
```json
[
  {
    "id": 1,
    "name": "Trivia RR.HH. Básico",
    "description": "Preguntas básicas sobre recursos humanos",
    "created_by": { "id": 2, "name": "Admin", "email": "admin@talana.com", "role": "admin" }
  }
]
```

---

### `POST /trivias/` — Admin
Crea una trivia, asignando preguntas y jugadores.

**Body:**
```json
{
  "name": "Trivia RR.HH. Básico",
  "description": "Preguntas básicas sobre recursos humanos",
  "question_ids": [1, 2, 3],
  "user_ids": [3, 4]
}
```

> `question_ids` y `user_ids` son opcionales. Se pueden agregar luego con `PUT`.

**Response `201`:**
```json
{
  "id": 1,
  "name": "Trivia RR.HH. Básico",
  "description": "Preguntas básicas sobre recursos humanos",
  "created_by": { "id": 2, "name": "Admin", "email": "admin@talana.com", "role": "admin" },
  "questions": [...],
  "participants": [...]
}
```

---

### `GET /trivias/<id>/` — Admin
Retorna el detalle completo: preguntas con respuestas correctas y participantes asignados.

**Response `200`:**
```json
{
  "id": 1,
  "name": "Trivia RR.HH. Básico",
  "description": "Preguntas básicas sobre recursos humanos",
  "created_by": { "id": 2, "name": "Admin", "email": "admin@talana.com", "role": "admin" },
  "questions": [
    {
      "id": 1,
      "text": "¿Qué es el onboarding?",
      "difficult_level": "easy",
      "answers": [
        { "id": 1, "text": "Proceso de incorporación", "is_correct": true },
        { "id": 2, "text": "Proceso de desvinculación", "is_correct": false }
      ]
    }
  ],
  "participants": [
    { "id": 1, "user": { "id": 3, "name": "Juan", "email": "juan@example.com", "role": "player" }, "score": 0, "completed": false }
  ]
}
```

---

### `PUT /trivias/<id>/` — Admin
Actualiza parcialmente una trivia.

**Body (todos opcionales):**
```json
{
  "name": "Nuevo nombre",
  "description": "Nueva descripción",
  "question_ids": [1, 2, 4],
  "user_ids": [3, 5]
}
```

> `question_ids` reemplaza el set completo de preguntas.
> `user_ids` agrega nuevos participantes sin eliminar los existentes.

---

### `DELETE /trivias/<id>/` — Admin
Elimina una trivia y sus participaciones asociadas.

---

### `GET /trivias/my/` — Player
Lista las trivias asignadas al jugador autenticado (sin preguntas).

**Response `200`:**
```json
[
  { "id": 1, "name": "Trivia RR.HH. Básico", "description": "Preguntas básicas sobre recursos humanos" }
]
```

---

### `GET /trivias/<id>/play/` — Player
Retorna la trivia con sus preguntas y opciones de respuesta. **No muestra cuál es la correcta ni la dificultad.**

**Response `200`:**
```json
{
  "id": 1,
  "name": "Trivia RR.HH. Básico",
  "description": "Preguntas básicas sobre recursos humanos",
  "questions": [
    {
      "id": 1,
      "text": "¿Qué es el onboarding?",
      "answers": [
        { "id": 1, "text": "Proceso de incorporación" },
        { "id": 2, "text": "Proceso de desvinculación" },
        { "id": 3, "text": "Evaluación de desempeño" }
      ]
    }
  ]
}
```

**Response `403`:** El jugador no está asignado a esta trivia.

---

### `POST /trivias/<id>/answers/` — Player
Envía las respuestas del jugador. Calcula el puntaje y marca la trivia como completada.

**Puntaje por dificultad:** `easy = 1 pt`, `medium = 2 pts`, `hard = 3 pts`.

**Body:**
```json
{
  "answers": [
    { "question_id": 1, "answer_id": 1 },
    { "question_id": 2, "answer_id": 5 },
    { "question_id": 3, "answer_id": 8 }
  ]
}
```

**Response `200`:**
```json
{
  "id": 1,
  "user": { "id": 3, "name": "Juan", "email": "juan@example.com", "role": "player" },
  "score": 4,
  "completed": true
}
```

**Response `400`:** Si la trivia ya fue completada, o una pregunta/respuesta no pertenece a la trivia.
**Response `403`:** El jugador no está asignado a esta trivia.

---

### `GET /trivias/<id>/ranking/` — Autenticado
Retorna el ranking de participantes de una trivia ordenado por puntaje descendente.

**Response `200`:**
```json
[
  { "user": { "id": 3, "name": "Juan", "email": "juan@example.com", "role": "player" }, "score": 5, "completed": true },
  { "user": { "id": 4, "name": "María", "email": "maria@example.com", "role": "player" }, "score": 3, "completed": true }
]
```

---

## Códigos de respuesta

| Código | Significado |
|--------|-------------|
| `200` | OK |
| `201` | Creado |
| `204` | Sin contenido (eliminación exitosa) |
| `400` | Error de validación |
| `401` | No autenticado |
| `403` | Sin permisos |
| `404` | No encontrado |
