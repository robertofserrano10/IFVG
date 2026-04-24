# Conexión a Supabase.
# Esta función crea y devuelve el cliente oficial de Supabase.
# Se importa desde las rutas que necesiten acceder a la base de datos.

from supabase import create_client, Client

from app.config import settings


def get_supabase_client() -> Client:
    """
    Crea y devuelve el cliente de Supabase usando las credenciales del .env.
    Lanza un error claro si faltan credenciales o si la URL tiene formato incorrecto.
    """
    if not settings.supabase_url:
        raise ValueError(
            "Falta SUPABASE_URL en el archivo .env. "
            "Cópiala desde tu proyecto en supabase.com → Settings → API."
        )

    if not settings.supabase_anon_key:
        raise ValueError(
            "Falta SUPABASE_ANON_KEY en el archivo .env. "
            "Cópiala desde tu proyecto en supabase.com → Settings → API."
        )

    # Normalizar: eliminar trailing slash para evitar errores de validacion internos
    url = settings.supabase_url.rstrip("/")

    # Rechazar URLs que incluyan rutas de API — solo se acepta la URL base del proyecto
    if "/rest/v1" in url or "/auth/v1" in url or "/storage/v1" in url:
        raise ValueError(
            "SUPABASE_URL no debe incluir rutas como /rest/v1/ o /auth/v1/. "
            "El valor correcto es solo la URL base del proyecto, por ejemplo: "
            "https://kiecdnqfnxfspmghlhdy.supabase.co"
        )

    client: Client = create_client(url, settings.supabase_anon_key)
    return client
