# Carga las variables de entorno desde el archivo .env
# Así nunca hay credenciales hardcodeadas en el código.

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# load_dotenv() carga el .env antes de que BaseSettings lo lea.
# Esto garantiza que las variables estén disponibles aunque
# uvicorn se ejecute desde un directorio distinto al de backend/.
load_dotenv()


class Settings(BaseSettings):
    supabase_url: str = ""
    supabase_anon_key: str = ""
    backend_host: str = "127.0.0.1"
    backend_port: int = 8000

    # model_config es la sintaxis correcta en pydantic-settings v2
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# Instancia global que se importa en el resto del proyecto
settings = Settings()
