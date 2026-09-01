from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-5.6-terra"
    it_agent_db_path: Path = Path("it_agent_platform.db")
    it_agent_execution_mode: Literal["mock", "live"] = "mock"
    it_agent_analysis_mode: Literal["deterministic", "openai"] = "deterministic"


@lru_cache
def get_settings() -> Settings:
    return Settings()
