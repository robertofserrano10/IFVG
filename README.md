# Trading Journal App

Aplicación web personal para registro de trades. Diseñada para fomentar la disciplina, registrar la ejecución y analizar el comportamiento como trader.

---

## ¿Qué hace este proyecto?

- Permite registrar trades de forma ordenada.
- Tiene un backend en Python (FastAPI) que expone una API REST.
- Tiene un frontend en HTML + CSS + JavaScript vanilla.
- Usa Supabase como base de datos en la nube (configurado en Fase 2).

---

## Estructura de carpetas

```
fvgproyecto/
  backend/
    app/
      main.py         ← Punto de entrada de FastAPI
      config.py       ← Carga de variables de entorno
      database.py     ← Conexión a Supabase (placeholder por ahora)
      routes/
        health.py     ← Endpoint GET /health
      services/       ← Lógica de negocio (vacío en Fase 1)
      models/         ← Modelos de base de datos (vacío en Fase 1)
      schemas/        ← Esquemas Pydantic (vacío en Fase 1)
      utils/          ← Funciones auxiliares (vacío en Fase 1)
    requirements.txt  ← Dependencias Python
    .env.example      ← Plantilla de variables de entorno
  frontend/
    index.html        ← Página principal
    styles.css        ← Estilos
    app.js            ← Lógica del frontend
  README.md
```

---

## Cómo ejecutar el proyecto localmente (Windows + PowerShell)

### Paso 1 — Abrir la carpeta del proyecto en VS Code

Abre VS Code y usa **File → Open Folder** para abrir `fvgproyecto`.

Luego abre la terminal integrada con: `Ctrl + ñ` o **Terminal → New Terminal**.

---

### Paso 2 — Crear el entorno virtual de Python

Desde la terminal, navega a la carpeta `backend`:

```powershell
cd backend
```

Crea el entorno virtual:

```powershell
python -m venv venv
```

Activa el entorno virtual:

```powershell
venv\Scripts\Activate
```

> Si ves un error de permisos, ejecuta primero:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

Cuando el entorno está activo, verás `(venv)` al inicio de la línea en la terminal.

---

### Paso 3 — Instalar dependencias

Con el entorno virtual activo:

```powershell
pip install -r requirements.txt
```

---

### Paso 4 — Configurar variables de entorno

Copia el archivo de ejemplo y renómbralo:

```powershell
copy .env.example .env
```

Abre `.env` en VS Code y rellena los valores cuando tengas las credenciales de Supabase. Por ahora puedes dejarlo vacío para la conexión básica.

---

### Paso 5 — Correr el backend

> **IMPORTANTE:** uvicorn debe ejecutarse desde dentro de la carpeta `backend/`, no desde la raiz del proyecto. Si lo corres desde otro lugar obtendrás `ModuleNotFoundError: No module named 'app'`.

```powershell
# Asegurate de estar en backend/ antes de correr uvicorn
cd C:\Users\rober\Documents\fvgproyecto\backend

# Activa el entorno virtual si no esta activo
.\.venv\Scripts\Activate

# Corre el servidor
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Deberías ver algo como:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

Puedes verificar que funciona abriendo en el navegador:
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs` ← documentación automática de FastAPI

---

### Paso 6 — Abrir el frontend

Abre el archivo `frontend/index.html` directamente en el navegador.

La forma más simple en VS Code es instalar la extensión **Live Server**:
1. Ve a Extensiones (`Ctrl + Shift + X`)
2. Busca "Live Server" e instálala
3. Haz clic derecho sobre `index.html` → **Open with Live Server**

Esto abre el frontend en `http://127.0.0.1:5500`.

---

### Paso 7 — Probar la conexión

Con el backend corriendo, pulsa el botón **"Test Backend Connection"** en la página.
Deberías ver:

```json
{
  "status": "ok",
  "message": "Backend running"
}
```

---

## Variables de entorno

El archivo `.env` va dentro de la carpeta `backend/` y NUNCA debe subirse a git.
El archivo `.env.example` sí se puede subir — sirve de plantilla para otros.

| Variable           | Descripción                              |
|--------------------|------------------------------------------|
| `SUPABASE_URL`     | URL de tu proyecto en Supabase           |
| `SUPABASE_ANON_KEY`| Clave anónima pública de Supabase        |
| `BACKEND_HOST`     | Host donde corre el backend (local)      |
| `BACKEND_PORT`     | Puerto del backend (por defecto 8000)    |

---

## Errores comunes en Windows

| Error | Causa probable | Solución |
|-------|---------------|----------|
| `'uvicorn' is not recognized` | Entorno virtual no activo | Ejecuta `.\.venv\Scripts\Activate` desde `backend/` |
| `ModuleNotFoundError: No module named 'app'` | Uvicorn ejecutado desde la raiz del proyecto | Entra primero a `backend/` con `cd backend`, luego corre uvicorn |
| `ModuleNotFoundError: No module named 'fastapi'` | Dependencias no instaladas | Ejecuta `pip install -r requirements.txt` |
| `Cannot be loaded because running scripts is disabled` | Política de ejecución de PowerShell | Ejecuta `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| Error CORS en el navegador | Backend no corriendo | Verifica que uvicorn esté activo en el puerto 8000 |
| `Address already in use` | Puerto 8000 ocupado | Cambia el puerto: `--port 8001` y actualiza `BACKEND_URL` en `app.js` |

---

## Fase 3 — Primera tabla real: trading_days

### Paso 1 — Crear la tabla en Supabase

1. Ve a [supabase.com](https://supabase.com) e inicia sesión.
2. Abre tu proyecto.
3. En el menú lateral izquierdo, haz clic en **SQL Editor**.
4. Haz clic en **New query**.
5. Pega el siguiente SQL y haz clic en **Run**:

```sql
CREATE TABLE trading_days (
    id          BIGSERIAL PRIMARY KEY,
    trade_date  DATE        NOT NULL,
    market      TEXT        NOT NULL,
    is_news_day BOOLEAN     NOT NULL DEFAULT FALSE,
    is_ath_context BOOLEAN  NOT NULL DEFAULT FALSE,
    notes       TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

6. Deberías ver `Success. No rows returned` — la tabla fue creada.

---

### Paso 2 — Levantar el backend

```powershell
cd C:\Users\rober\Documents\fvgproyecto\backend
.\.venv\Scripts\Activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

---

### Paso 3 — Probar GET /trading-days

Abre en el navegador:

```
http://127.0.0.1:8000/trading-days
```

Respuesta esperada si la tabla está vacía:

```json
[]
```

---

### Paso 4 — Probar POST /trading-days desde /docs

1. Abre `http://127.0.0.1:8000/docs` en el navegador.
2. Busca el endpoint **POST /trading-days**.
3. Haz clic en **Try it out**.
4. En el campo **Request body**, pega este ejemplo:

```json
{
  "trade_date": "2026-04-22",
  "market": "NQ",
  "is_news_day": false,
  "is_ath_context": true,
  "notes": "Primer día de prueba"
}
```

5. Haz clic en **Execute**.
6. Respuesta esperada (201 Created):

```json
{
  "id": 1,
  "trade_date": "2026-04-22",
  "market": "NQ",
  "is_news_day": false,
  "is_ath_context": true,
  "notes": "Primer día de prueba",
  "created_at": "2026-04-22T..."
}
```

7. Vuelve a `http://127.0.0.1:8000/trading-days` — ahora debe aparecer el registro.

---

### Errores comunes en esta fase

| Error | Causa | Solución |
|-------|-------|----------|
| `relation "trading_days" does not exist` | La tabla no fue creada en Supabase | Ejecuta el SQL del Paso 1 en el SQL Editor de Supabase |
| `500 Internal Server Error` con mensaje de credenciales | `.env` mal configurado | Verifica `SUPABASE_URL` y `SUPABASE_ANON_KEY` en `backend/.env` |
| `422 Unprocessable Entity` | JSON del POST con formato incorrecto | Verifica que `trade_date` sea `"YYYY-MM-DD"` entre comillas |
| `[]` en GET después del POST | El POST falló silenciosamente | Revisa la respuesta del POST en `/docs` para ver el error real |

---

## Fase 4 — Segunda tabla: daily_bias

### Paso 1 — Crear la tabla en Supabase

Abre el **SQL Editor** en Supabase, pega y ejecuta:

```sql
CREATE TABLE daily_bias (
    id                          BIGSERIAL PRIMARY KEY,
    trading_day_id              BIGINT NOT NULL REFERENCES trading_days(id),
    daily_high                  NUMERIC NOT NULL,
    daily_low                   NUMERIC NOT NULL,
    daily_eq                    NUMERIC NOT NULL,
    current_price               NUMERIC NOT NULL,
    zone_position               TEXT NOT NULL,
    asia_high                   NUMERIC NOT NULL,
    asia_low                    NUMERIC NOT NULL,
    london_high                 NUMERIC NOT NULL,
    london_low                  NUMERIC NOT NULL,
    pending_liquidity_direction TEXT NOT NULL,
    premium_discount_direction  TEXT NOT NULL,
    bias_alignment              BOOLEAN NOT NULL DEFAULT FALSE,
    bias_direction              TEXT NOT NULL,
    bias_active                 BOOLEAN NOT NULL DEFAULT TRUE,
    chop_equilibrium            BOOLEAN NOT NULL DEFAULT FALSE,
    invalidated                 BOOLEAN NOT NULL DEFAULT FALSE,
    invalidation_reason         TEXT,
    comments                    TEXT,
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

Deberías ver `Success. No rows returned`.

---

### Paso 2 — Probar GET /daily-bias

```
http://127.0.0.1:8000/daily-bias
```

Respuesta esperada si la tabla está vacía: `[]`

---

### Paso 3 — Probar POST /daily-bias desde /docs

1. Abre `http://127.0.0.1:8000/docs`
2. Busca **POST /daily-bias** → **Try it out**
3. Pega este ejemplo (cambia `trading_day_id` por un id real de tu tabla):

```json
{
  "trading_day_id": 1,
  "daily_high": 21500.00,
  "daily_low": 21200.00,
  "daily_eq": 21350.00,
  "current_price": 21400.00,
  "zone_position": "premium",
  "asia_high": 21450.00,
  "asia_low": 21300.00,
  "london_high": 21480.00,
  "london_low": 21320.00,
  "pending_liquidity_direction": "bearish",
  "premium_discount_direction": "bearish",
  "bias_alignment": true,
  "bias_direction": "bearish",
  "bias_active": true,
  "chop_equilibrium": false,
  "invalidated": false,
  "invalidation_reason": null,
  "comments": "Primer bias de prueba"
}
```

4. Respuesta esperada: `201 Created` con el registro completo.

---

### Paso 4 — Probar desde el frontend

1. Abre `frontend/index.html` con Live Server.
2. El dropdown **Trading Day** debe mostrar tus trading days existentes.
3. Rellena el formulario y pulsa **Guardar Daily Bias**.
4. El registro aparecerá en la sección **Daily Bias Registrados**.

---

### Errores comunes en esta fase

| Error | Causa | Solución |
|-------|-------|----------|
| `relation "daily_bias" does not exist` | Tabla no creada | Ejecuta el SQL del Paso 1 |
| El dropdown de Trading Day sale vacío | No hay trading days creados, o el backend no está corriendo | Crea al menos un trading day primero; verifica que uvicorn esté activo |
| `422` al guardar bias | Campo numérico vacío o select sin seleccionar | Todos los campos numéricos y selects son requeridos |
| `foreign key violation` en el POST | `trading_day_id` no existe en `trading_days` | Usa un id real de tu tabla `trading_days` |

---

## Fase 5 — Tercera tabla: trades

### Paso 1 — Crear la tabla en Supabase

Abre el **SQL Editor** en Supabase, pega y ejecuta:

```sql
CREATE TABLE trades (
    id               BIGSERIAL    PRIMARY KEY,
    trading_day_id   BIGINT       NOT NULL REFERENCES trading_days(id),
    daily_bias_id    BIGINT       REFERENCES daily_bias(id),
    direction        TEXT         NOT NULL,
    sweep_confirmed  BOOLEAN      NOT NULL DEFAULT FALSE,
    ifvg_confirmed   BOOLEAN      NOT NULL DEFAULT FALSE,
    vshape_confirmed BOOLEAN      NOT NULL DEFAULT FALSE,
    smt_confirmed    BOOLEAN      NOT NULL DEFAULT FALSE,
    entry_price      NUMERIC      NOT NULL,
    stop_loss        NUMERIC      NOT NULL,
    take_profit      NUMERIC      NOT NULL,
    result_r         NUMERIC,
    notes            TEXT,
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);
```

Deberías ver `Success. No rows returned`.

---

### Paso 2 — Probar GET /trades

```
http://127.0.0.1:8000/trades
```

Respuesta esperada si la tabla está vacía: `[]`

---

### Paso 3 — Probar POST /trades desde /docs

1. Abre `http://127.0.0.1:8000/docs`
2. Busca **POST /trades** → **Try it out**
3. Pega este ejemplo (ajusta los ids):

```json
{
  "trading_day_id": 1,
  "daily_bias_id": 1,
  "direction": "long",
  "sweep_confirmed": true,
  "ifvg_confirmed": true,
  "vshape_confirmed": false,
  "smt_confirmed": false,
  "entry_price": 21350.00,
  "stop_loss": 21300.00,
  "take_profit": 21500.00,
  "result_r": 2.5,
  "notes": "Trade de prueba"
}
```

4. Respuesta esperada: `201 Created` con el registro completo.

---

### Paso 4 — Probar desde el frontend

1. Abre `frontend/index.html` con Live Server.
2. El dropdown **Trading Day** y **Daily Bias** deben mostrar tus registros existentes.
3. Rellena el formulario y pulsa **Guardar Trade**.
4. El registro aparecerá en la sección **Trades Registrados** con los niveles de precio y los flags de confirmación.

---

### Errores comunes en esta fase

| Error | Causa | Solución |
|-------|-------|----------|
| `relation "trades" does not exist` | Tabla no creada | Ejecuta el SQL del Paso 1 |
| Dropdowns vacíos | Backend no corriendo o sin datos previos | Crea al menos un trading day y un daily bias primero |
| `422` al guardar | `entry_price`, `stop_loss` o `take_profit` vacíos | Esos tres campos son requeridos |
| `foreign key violation` | Id de trading day o bias que no existe | Usa ids reales de tus tablas |
| `result_r` no aparece | Se dejó vacío al crear | Es opcional; se puede omitir y añadir después |
