from pathlib import Path
from typing import Tuple

from pydantic_settings import BaseSettings

from app.constants.constants import (BANK_BIK, PAYER_OR_RECIPIENT_BANK,
                                     DEBTOR_ACCOUNT_NUMBER, CURRENCY_CODE, DEBTOR_NAME,
                                     DEBTOR_BANK_NAME, DOCUMENT_TYPE_CODE, DOCUMENT_NUMBER,
                                     DOCUMENT_OPERATION_DATE, PAYER_OR_RECIPIENT_NAME,
                                     PAYER_OR_RECIPIENT_INN, PAYER_OR_RECIPIENT_KPP, ACCOUNT_NUMBER,
                                     DEBIT_AMOUNT, CREDIT_AMOUNT, PAYMENT_PURPOSE,
                                     CORESPONDENT_ACCOUNT_NUMBER)


class Settings(BaseSettings):
    # Basic settings
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    PORT: int = 8000
    TITLE: str = "Bank Statement Normalizer"
    
    # File settings
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: Tuple[str, ...] = ('docx', 'doc', 'xlsx', 'xls')
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    PATH_TO_UPLOAD_DIRECTORY: Path = BASE_DIR / "uploads"
    PATH_TO_LOGS: Path = BASE_DIR.parent / "logs"
    PATH_TO_CONFIG_RESULT_TABLE: Path = BASE_DIR / "config/result_table_config.json"
    PATH_TO_CONFIG_LOGS: Path = BASE_DIR / "config/logging_config.json"
    
    # Security
    MAX_REQUESTS_PER_MINUTE: int = 100
    CORS_ORIGINS: Tuple[str, ...] = ("*",)

    # Column configuration
    COLUMN_ORDER: tuple = (
        DEBTOR_ACCOUNT_NUMBER,
        CURRENCY_CODE,
        DEBTOR_NAME,
        DEBTOR_BANK_NAME,
        DOCUMENT_TYPE_CODE,
        DOCUMENT_NUMBER,
        DOCUMENT_OPERATION_DATE,
        PAYER_OR_RECIPIENT_NAME,
        PAYER_OR_RECIPIENT_INN,
        PAYER_OR_RECIPIENT_KPP,
        ACCOUNT_NUMBER,
        DEBIT_AMOUNT,
        CREDIT_AMOUNT,
        PAYMENT_PURPOSE,
        CORESPONDENT_ACCOUNT_NUMBER,
        PAYER_OR_RECIPIENT_BANK,
        BANK_BIK
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    def is_file_allowed(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS

    def get_file_extension(self, filename: str) -> str:
        """Get file extension"""
        return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''


# Create settings instance
settings = Settings()

# Create required directories
settings.PATH_TO_UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)
settings.PATH_TO_LOGS.mkdir(parents=True, exist_ok=True)