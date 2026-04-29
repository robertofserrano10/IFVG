# Conexión a Supabase.
# Esta función crea y devuelve el cliente oficial de Supabase.
# Se importa desde las rutas que necesiten acceder a la base de datos.

from supabase import create_client, Client

from app.config import settings


def _get_url() -> str:
    if not settings.supabase_url:
        raise ValueError(
            "Falta SUPABASE_URL en el archivo .env. "
            "Cópiala desde tu proyecto en supabase.com → Settings → API."
        )
    url = settings.supabase_url.rstrip("/")
    if "/rest/v1" in url or "/auth/v1" in url or "/storage/v1" in url:
        raise ValueError(
            "SUPABASE_URL no debe incluir rutas como /rest/v1/ o /auth/v1/. "
            "El valor correcto es solo la URL base del proyecto, por ejemplo: "
            "https://kiecdnqfnxfspmghlhdy.supabase.co"
        )
    return url


def get_supabase_client() -> Client:
    """Returns a service_role client when available (bypasses RLS for server-side ops), falls back to anon_key."""
    url = _get_url()
    key = settings.supabase_service_role_key or settings.supabase_anon_key
    if not key:
        raise ValueError(
            "Falta SUPABASE_ANON_KEY en el archivo .env. "
            "Cópiala desde tu proyecto en supabase.com → Settings → API."
        )
    return create_client(url, key)


def get_storage_client() -> Client:
    url = _get_url()
    key = settings.supabase_service_role_key or settings.supabase_anon_key
    if not key:
        raise ValueError("Falta SUPABASE_ANON_KEY o SUPABASE_SERVICE_ROLE_KEY en el .env.")
    return create_client(url, key)
