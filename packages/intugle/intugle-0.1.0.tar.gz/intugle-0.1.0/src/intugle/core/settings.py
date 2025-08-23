#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

from intugle.core.utilities.configs import load_model_configuration

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")


BASE_PATH = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Global Configuration"""

    UPSTREAM_SAMPLE_LIMIT: int = 10
    MODEL_DIR_PATH: str = str(Path(os.path.split(os.path.abspath(__file__))[0]).parent.joinpath("artifacts"))
    MODEL_RESULTS_PATH: str = os.path.join("model", "model_results")

    DI_CONFIG: dict = load_model_configuration("DI", {})
    KI_CONFIG: dict = load_model_configuration("KI", {})
    LP_CONFIG: dict = load_model_configuration("LP", {})
    BG_CONFIG: dict = load_model_configuration("BG", {})

    DI_MODEL_VERSION: str = "13052023"

    PROJECT_BASE: str = str(Path(os.getenv("VSCODE_WORKSPACE", os.getcwd())))

    MCP_SERVER_NAME: str = "intugle"
    MCP_SERVER_DESCRIPTION: str = "Data Tools for MCP"
    MCP_SERVER_VERSION: str = "1.0.0"
    MCP_SERVER_AUTHOR: str = "Intugle"
    MCP_SERVER_STATELESS_HTTP: bool = True

    MCP_SERVER_HOST: str = "0.0.0.0"
    MCP_SERVER_PORT: int = 8080
    MCP_SERVER_LOG_LEVEL: str = "info"

    SQL_DIALECT: str = "postgresql"
    DOMAIN: str = "ecommerce"
    UNIVERSAL_INSTRUCTIONS: str = ""
    L2_SAMPLE_LIMIT: int = 10

    # LLM CONFIGS
    LLM_PROVIDER: str
    LLM_SAMPLE_LIMIT: int = 15
    STRATA_SAMPLE_LIMIT: int = 4
    MAX_RETRIES: int = 5
    SLEEP_TIME: int = 25
    ENABLE_RATE_LIMITER: bool = False

    # LP
    HALLUCINATIONS_MAX_RETRY: int = 2
    UNIQUENESS_THRESHOLD: float = 0.9

    # DATETIME
    DATE_TIME_FORMAT_LIMIT: int = 25
    REMOVE_DATETIME_LP: bool = True

    model_config = SettingsConfigDict(
        env_file=f"{BASE_PATH}/.env",
        env_file_encoding="utf-8",
        extra="allow",
        case_sensitive=True,
    )
    L2_SAMPLE_LIMIT: int = 10

    # LLM CONFIGS
    LLM_TYPE: str = "azure"
    LLM_SAMPLE_LIMIT: int = 15
    STRATA_SAMPLE_LIMIT: int = 4

    # LP
    HALLUCINATIONS_MAX_RETRY: int = 2
    UNIQUENESS_THRESHOLD: float = 0.9

    # DATETIME
    DATE_TIME_FORMAT_LIMIT: int = 25
    REMOVE_DATETIME_LP: bool = True

    # Adapter
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432
    POSTGRES_SCHEMA: str = "public"


@lru_cache
def get_settings() -> Settings:
    """Get the global configuration singleton"""
    return Settings()


# Create a global configuration instance
settings = get_settings()
