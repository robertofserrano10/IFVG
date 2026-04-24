# Ruta de prueba para verificar que el cliente de Supabase se crea correctamente.
# No hace queries a tablas — solo confirma que las credenciales son válidas
# y que la librería puede inicializar la conexión sin errores.

from fastapi import APIRouter

from app.database import get_supabase_client

router = APIRouter()


@router.get("/supabase-test")
def supabase_test():
    """
    Intenta crear el cliente de Supabase y devuelve el resultado.
    Útil para verificar que SUPABASE_URL y SUPABASE_ANON_KEY están bien configuradas.
    """
    try:
        get_supabase_client()
        return {
            "status": "connected",
            "message": "Supabase client created successfully",
        }
    except Exception as e:
        # Devuelve el detalle real del error para facilitar el diagnóstico
        return {
            "status": "error",
            "message": str(e),
        }
