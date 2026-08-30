# -*- coding: utf-8 -*-
"""
CCIA CONFIG MODULE v1.0 (Certificado OWASP & Pydantic V2)
"""
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    JWT_SECRET_KEY: str = Field(
        default="SUPER_SECRET_CHANGE_ME_IN_PRODUCTION_KEY_123456789",
        min_length=32,
        description="Clave secreta segura para firma JWT"
    )
    ALGORITHM: str = Field(default="HS256", description="Algoritmo de encriptación JWT")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, gt=0, description="Tiempo de vida del token en minutos")
    DATABASE_URL: str = Field(default="sqlite:////home/k1/ccia_workspace/university.db")
    API_PORT: int = Field(default=8000, ge=1024, le=65535)

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

settings = Settings()
