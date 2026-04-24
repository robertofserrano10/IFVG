# Punto de entrada del backend. Aquí se crea y configura la app FastAPI.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes.health import router as health_router
from app.routes.supabase_test import router as supabase_test_router
from app.routes.trading_days import router as trading_days_router
from app.routes.daily_bias import router as daily_bias_router
from app.routes.trades import router as trades_router
from app.routes.metrics import router as metrics_router
from app.routes.trade_images import router as trade_images_router

app = FastAPI(
    title="Trading Journal API",
    description="Backend para el journal de trading personal",
    version="1.0.0",
)

# CORS: permite que el frontend (en otro puerto) se comunique con este backend.
# IMPORTANTE: allow_credentials=True es incompatible con allow_origins=["*"].
# Los navegadores rechazan esa combinación con error CORS.
# En desarrollo usamos False; en producción se especifica la URL exacta del frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rutas
app.include_router(health_router)
app.include_router(supabase_test_router)
app.include_router(trading_days_router)
app.include_router(daily_bias_router)
app.include_router(trades_router)
app.include_router(metrics_router)
app.include_router(trade_images_router)
