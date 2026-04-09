"""Configuration management for the MCP SQL Server."""

import os
import pyodbc
from typing import Optional
from pydantic import BaseModel


class DatabaseConfig(BaseModel):
    """Database connection configuration."""
    server: str
    database: str
    user: Optional[str] = None
    password: Optional[str] = None
    port: int = 1433
    windows_auth: bool = False
    encrypt: bool = False


class LLMConfig(BaseModel):
    """LLM configuration for OpenAI."""
    provider: str = "openai"
    api_key: str = ""
    model: str = "gpt-3.5-turbo"
    endpoint: Optional[str] = None
    temperature: float = 0.3
    max_tokens: int = 500


class SpeechConfig(BaseModel):
    """Speech-to-text configuration."""
    provider: str = "azure"  # azure, google
    api_key: str = ""
    region: str = "eastus"
    language: str = "en-US"


class RLConfig(BaseModel):
    """Reinforcement learning configuration."""
    enabled: bool = True
    learning_rate: float = 0.1
    discount_factor: float = 0.9
    epsilon: float = 0.1  # exploration rate
    epsilon_decay: float = 0.995
    min_epsilon: float = 0.01


class OptimizerConfig(BaseModel):
    """Query optimizer configuration."""
    num_candidates: int = 3
    timeout_seconds: int = 30
    cost_weight: float = 0.5
    latency_weight: float = 0.5


class Config:
    """Global configuration manager."""
    
    def __init__(self):
        self.database = self._load_database_config()
        self.llm = self._load_llm_config()
        self.speech = self._load_speech_config()
        self.rl = self._load_rl_config()
        self.optimizer = self._load_optimizer_config()
    
    def _load_database_config(self) -> DatabaseConfig:
        return DatabaseConfig(
            server=os.getenv("MSSQL_SERVER", "localhost"),
            database=os.getenv("MSSQL_DATABASE", "master"),
            user=os.getenv("MSSQL_USER"),
            password=os.getenv("MSSQL_PASSWORD"),
            port=int(os.getenv("MSSQL_PORT", "1433")),
            windows_auth=os.getenv("MSSQL_WINDOWS_AUTH", "false").lower() == "true",
            encrypt=os.getenv("MSSQL_ENCRYPT", "false").lower() == "true"
        )
    
    def _load_llm_config(self) -> LLMConfig:
        return LLMConfig(
            provider=os.getenv("LLM_PROVIDER", "openai"),
            api_key=os.getenv("LLM_API_KEY", ""),
            model=os.getenv("LLM_MODEL", "gpt-4"),
            endpoint=os.getenv("LLM_ENDPOINT"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.3")),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "500"))
        )
    
    def _load_speech_config(self) -> SpeechConfig:
        return SpeechConfig(
            provider=os.getenv("SPEECH_PROVIDER", "azure"),
            api_key=os.getenv("SPEECH_API_KEY", ""),
            region=os.getenv("SPEECH_REGION", "eastus"),
            language=os.getenv("SPEECH_LANGUAGE", "en-US")
        )
    
    
    def _load_rl_config(self) -> RLConfig:
        return RLConfig(
            enabled=os.getenv("RL_ENABLED", "true").lower() == "true",
            learning_rate=float(os.getenv("RL_LEARNING_RATE", "0.1")),
            discount_factor=float(os.getenv("RL_DISCOUNT_FACTOR", "0.9")),
            epsilon=float(os.getenv("RL_EPSILON", "0.1")),
            epsilon_decay=float(os.getenv("RL_EPSILON_DECAY", "0.995")),
            min_epsilon=float(os.getenv("RL_MIN_EPSILON", "0.01"))
        )
    
    def _load_optimizer_config(self) -> OptimizerConfig:
        return OptimizerConfig(
            num_candidates=int(os.getenv("OPTIMIZER_NUM_CANDIDATES", "3")),
            timeout_seconds=int(os.getenv("OPTIMIZER_TIMEOUT", "30")),
            cost_weight=float(os.getenv("OPTIMIZER_COST_WEIGHT", "0.5")),
            latency_weight=float(os.getenv("OPTIMIZER_LATENCY_WEIGHT", "0.5"))
        )


def connect(server: str, database: str):
    """Create a database connection using pyodbc.
    
    Usage:
        conn = connect(server="localhost\\SQLEXPRESS", database="testdb")
    """
    return pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        "Trusted_Connection=yes;"
    )


def get_connection():
    """Get a database connection to the configured SQL Server."""
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost\\SQLEXPRESS;"
        "DATABASE=testdb;"
        "Trusted_Connection=yes;"
    )


# Global config instance
config = Config()
