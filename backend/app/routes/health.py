# Ruta de health check: sirve para verificar que el backend está corriendo.
# El frontend llamará a este endpoint al pulsar el botón de prueba.

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check():
    """Devuelve un JSON simple confirmando que el backend está activo."""
    return {
        "status": "ok",
        "message": "Backend running",
    }
