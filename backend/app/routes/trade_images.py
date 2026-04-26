import re
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.database import get_storage_client, get_supabase_client
from app.schemas.trade_image import TradeImageCreate, TradeImageResponse

router = APIRouter()

_ALLOWED_TYPES       = {"image/png", "image/jpeg", "image/jpg"}
_ALLOWED_IMAGE_TYPES = {"entrada", "salida", "contexto"}
_MAX_BYTES = 5 * 1024 * 1024  # 5 MB


def _safe_err(e: Exception) -> str:
    return re.sub(r'eyJ[A-Za-z0-9\-_]{10,}', '[REDACTED]', str(e))


# ─────────────────────────────────
# GET IMAGES
# ─────────────────────────────────
@router.get("/trade-images", response_model=List[TradeImageResponse])
def get_trade_images():
    try:
        client = get_supabase_client()
        response = (
            client.table("trade_images")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=_safe_err(e))


# ─────────────────────────────────
# CREATE IMAGE (URL manual)
# ─────────────────────────────────
@router.post("/trade-images", response_model=TradeImageResponse, status_code=201)
def create_trade_image(payload: TradeImageCreate):
    try:
        client = get_storage_client()  # 🔥 CAMBIO CLAVE (ANTES ANON)
        response = client.table("trade_images").insert(payload.model_dump()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=_safe_err(e))


# ─────────────────────────────────
# UPLOAD REAL A STORAGE
# ─────────────────────────────────
@router.post("/trade-images/upload", response_model=TradeImageResponse, status_code=201)
async def upload_trade_image(
    trade_id: int = Form(...),
    image_type: str = Form(...),
    file: UploadFile = File(...),
):
    if file.content_type not in _ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Solo se permiten imagenes PNG o JPEG.",
        )

    if image_type not in _ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="image_type inválido. Use: entrada, salida o contexto.",
        )

    content = await file.read()

    if len(content) > _MAX_BYTES:
        raise HTTPException(
            status_code=400,
            detail="La imagen supera el limite de 5MB.",
        )

    now = datetime.now(timezone.utc)
    year = now.strftime("%Y")
    month = now.strftime("%m")
    ts = int(now.timestamp())

    ext = "png" if file.content_type == "image/png" else "jpg"

    path = f"{year}/{month}/trade_{trade_id}/{image_type}_{ts}.{ext}"

    try:
        # 🔥 CLIENTE CON SERVICE ROLE
        client = get_storage_client()

        # ───── SUBIR A STORAGE ─────
        upload_response = client.storage.from_("trade-images").upload(
            path,
            content,
            {"content-type": file.content_type}
        )

        # Validar subida
        if hasattr(upload_response, "error") and upload_response.error:
            raise HTTPException(status_code=500, detail=str(upload_response.error))

        # ───── OBTENER URL ─────
        image_url = client.storage.from_("trade-images").get_public_url(path)

        # ───── INSERT DB (SIN RLS PROBLEM) ─────
        record = {
            "trade_id": trade_id,
            "image_url": image_url,
            "image_type": image_type
        }

        insert_response = client.table("trade_images").insert(record).execute()

        if not insert_response.data:
            raise HTTPException(status_code=500, detail="Error insertando imagen en DB")

        return insert_response.data[0]

    except Exception as e:
        raise HTTPException(status_code=500, detail=_safe_err(e))