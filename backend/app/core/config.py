import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "intelliparse"
    POSTGRES_URI: str = "postgresql://postgres:postgres@localhost:5432/intelliparse"
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "meta-llama/llama-3.3-70b-instruct:free"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    GEMINI_API_KEY: str = "your_gemini_api_key_here"
    GEMINI_MODEL: str = "gemini-2.5-flash"
    SECRET_KEY: str = "9f8a3b7c4d1e2f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a"
    KMS_KEY_ID: str = "d3b07384d113edec49eaa6238ad5ff00123456789abcdef0123456789abcdef"
    UPLOAD_DIR: str = "./storage/uploads"
    PIPELINE_MAX_RETRIES: int = 3
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ML_SERVICE_URL: str = "http://127.0.0.1:8000"

    # Oracle NetSuite SuiteTalk TBA Credentials
    NETSUITE_ACCOUNT_ID: str = "TSTDRV123456"
    NETSUITE_CONSUMER_KEY: str = "netsuite_consumer_key_placeholder"
    NETSUITE_CONSUMER_SECRET: str = "netsuite_consumer_secret_placeholder"
    NETSUITE_TOKEN_ID: str = "netsuite_token_id_placeholder"
    NETSUITE_TOKEN_SECRET: str = "netsuite_token_secret_placeholder"
    NETSUITE_REST_URL: str = "https://tstdrv123456.suitetalk.api.netsuite.com/services/rest/record/v1"

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
