from enum import Enum
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field


class ResponseStatus(str, Enum):
    """Enumeration of possible response statuses"""
    SUCCESS = "success"
    FAILURE = "failure"
    SUCCESS_WITH_WARNINGS = "success_with_warnings"


class Error(BaseModel):
    """Model for error details"""
    code: int
    message: str
    details: Optional[Dict[str, Any]] = None


class CustomWarning(BaseModel):
    """Model for warning details"""
    code: int
    message: str
    details: Optional[Dict[str, Any]] = None


class NormalizeResponse(BaseModel):
    """Response model for normalization endpoints"""
    status_code: int = Field(..., description="HTTP status code")
    message: str = Field(..., description="Response message")
    status: ResponseStatus = Field(..., description="Response status")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    file_path: Optional[str] = Field(None, description="Path to processed file")
    errors: Optional[List[Error]] = Field(None, description="List of errors")
    warnings: Optional[List[CustomWarning]] = Field(None, description="List of warnings")

    class Config:
        """Pydantic model configuration"""
        json_schema_extra = {
            "example": {
                "status_code": 200,
                "message": "File processed successfully",
                "status": ResponseStatus.SUCCESS,
                "data": {"processed_rows": 100},
                "file_path": "/path/to/file.xlsx",
                "errors": None,
                "warnings": [
                    {
                        "code": "MISSING_OPTIONAL_FIELD",
                        "message": "Optional field 'description' is missing",
                        "details": {"row": 5, "field": "description"}
                    }
                ]
            }
        }

    @classmethod
    def success(cls, message: str, data: Optional[Dict[str, Any]] = None, 
                file_path: Optional[str] = None) -> 'NormalizeResponse':
        """Create a success response
        :param message:
        :param data:
        :param file_path:
        :return:
        """
        return cls(
            status_code=200,
            message=message,
            status=ResponseStatus.SUCCESS,
            data=data,
            file_path=file_path
        )

    @classmethod
    def failure(cls, message: str, errors: List[Error],
                status_code: int = 400) -> 'NormalizeResponse':
        """Create a failure response"""
        return cls(
            status_code=status_code,
            message=message,
            status=ResponseStatus.FAILURE,
            errors=errors
        )

    @classmethod
    def success_with_warnings(cls, message: str, warnings: List[CustomWarning],
                              data: Optional[Dict[str, Any]] = None,
                              file_path: Optional[str] = None) -> 'NormalizeResponse':
        """Create a success response with warnings"""
        return cls(
            status_code=299,
            message=message,
            status=ResponseStatus.SUCCESS_WITH_WARNINGS,
            data=data,
            file_path=file_path,
            warnings=warnings
        )