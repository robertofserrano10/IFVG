# Deploy Guide — Trading Journal

## Backend (Render Web Service)

1. Create a new **Web Service** on Render.
2. Connect your GitHub repo.
3. Set **Root Directory**: `backend`
4. **Build command**:
   ```
   pip install -r requirements.txt
   ```
5. **Start command**:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
6. Add environment variables in Render dashboard:

| Variable | Description |
|---|---|
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_ANON_KEY` | Supabase anon/public key |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key (keep secret, never expose in frontend) |
| `FRONTEND_ORIGIN` | Full URL of the deployed frontend, e.g. `https://your-app.onrender.com` |

---

## Frontend (Render Static Site)

1. Create a new **Static Site** on Render.
2. Connect your GitHub repo.
3. Set **Root Directory**: `frontend`
4. **Build command**: *(leave empty)*
5. **Publish directory**: `frontend`

### Configure `frontend/config.js` for production

Before deploying (or via a build script), set the backend URL:

```js
window.APP_CONFIG = {
  BACKEND_URL: "https://your-backend.onrender.com"
};
```

> `config.js` is loaded **before** `app.js` in `index.html`, so `window.APP_CONFIG.BACKEND_URL` is available at startup.

> **Never** put `SUPABASE_SERVICE_ROLE_KEY` in `config.js` or any frontend file.

---

## Local Development

```bash
cd backend
uvicorn app.main:app --reload
```

Frontend: open `frontend/index.html` directly or serve with any static server.
`frontend/config.js` defaults to `http://127.0.0.1:8000` automatically.

---

## Environment Variables (.env)

Copy `backend/.env.example` to `backend/.env` and fill in values.
`.env` is gitignored and must never be committed.
