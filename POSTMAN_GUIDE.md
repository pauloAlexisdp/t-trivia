# Guía de pruebas con Postman

Base URL: `http://localhost:8000`

Todas las requests autenticadas requieren el header:
```
Authorization: Token <token>
```

---

## Flujo completo de prueba

### PASO 1 — Crear un admin

`POST /users/`

> Esta request requiere autenticación de admin. Si es la primera vez, crear el admin directo desde Django shell:
> ```bash
> python manage.py shell
> from apps.users.services import UserService
> UserService.create_user("Admin Talana", "admin@talana.com", "admin123", role="admin")
> ```

---

### PASO 2 — Login como admin

`POST /login/`

**Body:**
```json
{
  "email": "admin@talana.com",
  "password": "admin123"
}
```

**Guardar el token** retornado. Se usará en los pasos siguientes como `{{admin_token}}`.

---

### PASO 3 — Crear jugadores

`POST /register/`

> No requiere autenticación.

**Jugador 1:**
```json
{
  "name": "Juan Pérez",
  "email": "juan@example.com",
  "password": "juan123"
}
```

**Jugador 2:**
```json
{
  "name": "María González",
  "email": "maria@example.com",
  "password": "maria123"
}
```

Guardar los `id` retornados. Ej: `juan_id = 2`, `maria_id = 3`.

---

### PASO 4 — Login como jugador

`POST /login/`

```json
{
  "email": "juan@example.com",
  "password": "juan123"
}
```

Guardar como `{{player_token}}`.

---

### PASO 5 — Crear preguntas (como admin)

`POST /questions/`

**Header:** `Authorization: Token {{admin_token}}`

**Pregunta fácil (1 pt):**
```json
{
  "text": "¿Qué significa RR.HH.?",
  "difficult_level": "easy",
  "answers": [
    { "text": "Recursos Humanos", "is_correct": true },
    { "text": "Relaciones Humanas", "is_correct": false },
    { "text": "Registro de Haberes", "is_correct": false }
  ]
}
```

**Pregunta media (2 pts):**
```json
{
  "text": "¿Qué es el onboarding?",
  "difficult_level": "medium",
  "answers": [
    { "text": "Proceso de incorporación de nuevos empleados", "is_correct": true },
    { "text": "Proceso de desvinculación", "is_correct": false },
    { "text": "Evaluación anual de desempeño", "is_correct": false }
  ]
}
```

**Pregunta difícil (3 pts):**
```json
{
  "text": "¿Qué es el índice de rotación de personal?",
  "difficult_level": "hard",
  "answers": [
    { "text": "Indicador que mide entradas y salidas de empleados en un período", "is_correct": true },
    { "text": "Número de empleados que trabajan en turnos rotativos", "is_correct": false },
    { "text": "Porcentaje de empleados con contrato indefinido", "is_correct": false }
  ]
}
```

Guardar los `id` de las preguntas. Ej: `q1=1`, `q2=2`, `q3=3`.

---

### PASO 6 — Crear una trivia (como admin)

`POST /trivias/`

**Header:** `Authorization: Token {{admin_token}}`

```json
{
  "name": "Trivia RR.HH. Básico",
  "description": "Pon a prueba tus conocimientos de recursos humanos",
  "question_ids": [1, 2, 3],
  "user_ids": [2, 3]
}
```

Guardar el `id` de la trivia. Ej: `trivia_id = 1`.

---

### PASO 7 — Ver detalle de la trivia (como admin)

`GET /trivias/1/`

**Header:** `Authorization: Token {{admin_token}}`

Verificar que aparecen las preguntas **con** `is_correct` y `difficult_level`, y los participantes asignados.

---

### PASO 8 — Ver trivias del jugador

`GET /trivias/my/`

**Header:** `Authorization: Token {{player_token}}`

Verificar que aparece la trivia asignada con solo `id`, `name`, `description`. Sin preguntas.

---

### PASO 9 — Jugar la trivia (como jugador)

`GET /trivias/1/play/`

**Header:** `Authorization: Token {{player_token}}`

Verificar que las preguntas **NO** muestran `is_correct` ni `difficult_level`. Solo el texto y las opciones.

---

### PASO 10 — Enviar respuestas (como jugador)

`POST /trivias/1/answers/`

**Header:** `Authorization: Token {{player_token}}`

> Usar los `id` de respuestas obtenidos en el paso 9. En el ejemplo, las respuestas correctas son `answer_id: 1, 4, 7`.

**Respuestas correctas (puntaje esperado: 1+2+3 = 6 pts):**
```json
{
  "answers": [
    { "question_id": 1, "answer_id": 1 },
    { "question_id": 2, "answer_id": 4 },
    { "question_id": 3, "answer_id": 7 }
  ]
}
```

**Respuestas incorrectas (puntaje esperado: 0 pts):**
```json
{
  "answers": [
    { "question_id": 1, "answer_id": 2 },
    { "question_id": 2, "answer_id": 5 },
    { "question_id": 3, "answer_id": 8 }
  ]
}
```

Verificar que el response retorna `score` y `completed: true`.

---

### PASO 11 — Intentar responder de nuevo (debe fallar)

`POST /trivias/1/answers/`

**Header:** `Authorization: Token {{player_token}}`

```json
{
  "answers": [
    { "question_id": 1, "answer_id": 1 }
  ]
}
```

**Esperado `400`:**
```json
{ "error": "This trivia has already been completed" }
```

---

### PASO 12 — Ver ranking

`GET /trivias/1/ranking/`

**Header:** `Authorization: Token {{admin_token}}` o `{{player_token}}`

Verificar que aparecen los participantes ordenados por puntaje descendente.

---

## Casos de error para probar

### Jugador intenta jugar una trivia que no le fue asignada

`GET /trivias/999/play/`

**Header:** `Authorization: Token {{player_token}}`

**Esperado `403`.**

---

### Admin intenta jugar una trivia

`GET /trivias/1/play/`

**Header:** `Authorization: Token {{admin_token}}`

**Esperado `403`** (solo players pueden jugar).

---

### Respuesta que no pertenece a la pregunta

`POST /trivias/1/answers/`

**Header:** `Authorization: Token {{player_token}}`

```json
{
  "answers": [
    { "question_id": 1, "answer_id": 99 }
  ]
}
```

**Esperado `400`.**

---

### Request sin token

`GET /trivias/`

**Esperado `401`** o `403`.
