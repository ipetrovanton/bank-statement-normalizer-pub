import logging
import os

from fastapi import APIRouter, File, Request, UploadFile, HTTPException, Response

from app.config.config import settings
from app.config.result_messages import ResultMessages
from app.handlers.normalize_file_handler import process_file
from app.routers.normalize_response import NormalizeResponse, Error, CustomWarning

file_normalize_router = APIRouter(
    prefix="/normalize",
    tags=["normalize"],
    responses={
        200: {"description": "Successful operation"},
        400: {"description": "Invalid input"},
        500: {"description": "Internal server error"}
    }
)

logger = logging.getLogger(__name__)


@file_normalize_router.get("/health")
async def health_check() -> Response:
    """Health check endpoint"""
    logger.info("Health check request received")
    return Response(
        status_code=200,
        content=NormalizeResponse.success(
            message="Service is healthy",
            data={"status": "UP"}
        ).model_dump_json(),
        media_type="application/json",
    )

async def validate_file(file: UploadFile) -> None:
    """Validate uploaded file"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    if not settings.is_file_allowed(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {settings.ALLOWED_EXTENSIONS}"
        )

    # Check file size
    file_size = 0
    chunk_size = 8192  # 8KB chunks

    while chunk := await file.read(chunk_size):
        file_size += len(chunk)
        if file_size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
            )

    # Reset file position for future reading
    await file.seek(0)


@file_normalize_router.post(
    "/parse",
    summary="Нормализация банковской выписки",
    description="Загрузка и обработка банковской выписки",
    response_description="Нормализованные данные банковской выписки",
    response_model=None,
    responses={
        200: {
            "description": "Успешная нормализация банковской выписки",
            "content": {
                "application/json": {
                    "example": {
                        "status_code": 200,
                        "message": "File processed successfully",
                        "status": "success",
                        "data": {
                            "schema": {
                                "fields": [
                                    {
                                        "name": "index",
                                        "type": "integer"
                                    },
                                    {
                                        "name": "No",
                                        "type": "string"
                                    },
                                    {
                                        "name": "document_operation_date",
                                        "type": "string"
                                    },
                                    {
                                        "name": "document_type_code",
                                        "type": "string"
                                    },
                                    {
                                        "name": "document_number",
                                        "type": "string"
                                    },
                                    {
                                        "name": "document_date",
                                        "type": "string"
                                    },
                                    {
                                        "name": "correspondent_account_number",
                                        "type": "string"
                                    },
                                    {
                                        "name": "payer_or_recipient_bank",
                                        "type": "string"
                                    },
                                    {
                                        "name": "bank_bik",
                                        "type": "string"
                                    },
                                    {
                                        "name": "payer_or_recipient_name",
                                        "type": "string"
                                    },
                                    {
                                        "name": "payer_or_recipient_inn",
                                        "type": "string"
                                    },
                                    {
                                        "name": "payer_or_recipient_kpp",
                                        "type": "string"
                                    },
                                    {
                                        "name": "account_number",
                                        "type": "string"
                                    },
                                    {
                                        "name": "debit_amount",
                                        "type": "string"
                                    },
                                    {
                                        "name": "credit_amount",
                                        "type": "string"
                                    },
                                    {
                                        "name": "payment_purpose",
                                        "type": "string"
                                    },
                                    {
                                        "name": "debtor_account_number",
                                        "type": "string"
                                    },
                                    {
                                        "name": "currency_code",
                                        "type": "string"
                                    },
                                    {
                                        "name": "debtor_bank_name",
                                        "type": "string"
                                    },
                                    {
                                        "name": "debtor_name",
                                        "type": "string"
                                    }
                                ],
                                "primaryKey": [
                                    "index"
                                ],
                                "pandas_version": "1.4.0"
                            },
                            "data": [
                                {
                                    "index": 0,
                                    "No": "1",
                                    "document_operation_date": "05.04.2022",
                                    "document_type_code": "01",
                                    "document_number": "695",
                                    "document_date": "04.04.2022",
                                    "correspondent_account_number": "30101810300000000881",
                                    "payer_or_recipient_bank": "Ф-л Приволжский ПАО Банк \"ФК Открытие\"",
                                    "bank_bik": "042282881",
                                    "payer_or_recipient_name": "ООО \"АЭС ИНВЕСТ\"",
                                    "payer_or_recipient_inn": "7453169760",
                                    "payer_or_recipient_kpp": "745101001",
                                    "account_number": "40702810602700003531",
                                    "debit_amount": "0-00",
                                    "credit_amount": "163955130-53",
                                    "payment_purpose": "Перевод остатка согласно заявления клиента на закрытие счета. Без НДС.",
                                    "debtor_account_number": "40702810101220500676",
                                    "currency_code": "810",
                                    "debtor_bank_name": "ФИЛИАЛ ПАО \"БАНК УРАЛСИБ\" В Г.УФА",
                                    "debtor_name": "ООО \"АЭС ИНВЕСТ\""
                                }
                            ]
                        },
                        "file_path": "/app/uploads/40702810101220500676  с 30.03.2022/40702810101220500676  с 30.03.2022-output.xlsx",
                        "errors": "null",
                        "warnings": "null"
                    }
                }
            }
        },
        299: {
            "description": "Файл обработан с предупреждениями",
            "content": {
                "application/json": {
                    "example":
                        {
                            "status_code": 299,
                            "message": "File processed with warnings",
                            "status": "success_with_warnings",
                            "data": {
                                "schema": {
                                    "fields": [
                                        {
                                            "name": "index",
                                            "type": "integer"
                                        },
                                        {
                                            "name": "document_operation_date",
                                            "type": "string"
                                        },
                                        {
                                            "name": "document_type_code",
                                            "type": "string"
                                        },
                                        {
                                            "name": "document_number",
                                            "type": "string"
                                        },
                                        {
                                            "name": "document_date",
                                            "type": "string"
                                        },
                                        {
                                            "name": "correspondent_account_number",
                                            "type": "string"
                                        },
                                        {
                                            "name": "payer_or_recipient_bank",
                                            "type": "string"
                                        },
                                        {
                                            "name": "bank_bik",
                                            "type": "string"
                                        },
                                        {
                                            "name": "payer_or_recipient_name",
                                            "type": "string"
                                        },
                                        {
                                            "name": "payer_or_recipient_inn",
                                            "type": "string"
                                        },
                                        {
                                            "name": "payer_or_recipient_kpp",
                                            "type": "string"
                                        },
                                        {
                                            "name": "account_number",
                                            "type": "string"
                                        },
                                        {
                                            "name": "debit_amount",
                                            "type": "string"
                                        },
                                        {
                                            "name": "credit_amount",
                                            "type": "string"
                                        },
                                        {
                                            "name": "payment_purpose",
                                            "type": "string"
                                        },
                                        {
                                            "name": "No",
                                            "type": "string"
                                        },
                                        {
                                            "name": "debtor_account_number",
                                            "type": "string"
                                        },
                                        {
                                            "name": "currency_code",
                                            "type": "string"
                                        },
                                        {
                                            "name": "debtor_bank_name",
                                            "type": "string"
                                        },
                                        {
                                            "name": "debtor_name",
                                            "type": "string"
                                        }
                                    ],
                                    "primaryKey": [
                                        "index"
                                    ],
                                    "pandas_version": "1.4.0"
                                },
                                "data": [
                                    {
                                        "index": 0,
                                        "document_operation_date": "01.04.2024",
                                        "document_type_code": "17",
                                        "document_number": "335248",
                                        "document_date": "01.04.2024",
                                        "correspondent_account_number": "30101810600000000770",
                                        "payer_or_recipient_bank": "ФИЛИАЛ ПАО \"БАНК УРАЛСИБ\" В Г.УФА",
                                        "bank_bik": "048073770",
                                        "payer_or_recipient_name": "ФИЛИАЛ ПАО \"БАНК УРАЛСИБ\" В Г.УФА",
                                        "payer_or_recipient_inn": "0274062111",
                                        "payer_or_recipient_kpp": "027802001",
                                        "account_number": "47426810400004070904",
                                        "debit_amount": "0-00",
                                        "credit_amount": "7039560-14",
                                        "payment_purpose": "Выплата начисленных процентов за п-д с 13.03.2024 по 31.03.2024 по счету '40702810101220500676' согласно договору банковского счета №40702810101220500676 от '30/03/2022' НДС не предусмотрен.",
                                        "No": "Заголовок не найден в выписке",
                                        "debtor_account_number": "40702810101220500676",
                                        "currency_code": "Значение не найдено в выписке",
                                        "debtor_bank_name": "ФИЛИАЛ ПАО \"БАНК УРАЛСИБ\" В Г.УФА",
                                        "debtor_name": "ООО \"АЭС ИНВЕСТ\""
                                    }
                                ]
                            },
                            "file_path": "app/uploads/40702810101220500676  с 30.03.2022(2)/40702810101220500676  с 30.03.2022(2).xlsx",
                            "errors": "null",
                            "warnings": [
                                {
                                    "code": 299,
                                    "message": "Значение заголовка: currency_code не найдено в выписке",
                                    "details": {}
                                }
                            ]
                        }
                }
            }
        },
        422: {
            "description": "Invalid input",
            "content": {
                "application/json": {
                    "status_code": 422,
                    "message": "Файл невозможно конвертировать.",
                    "status": "failure",
                    "data": "null",
                    "file_path": "null",
                    "errors": [
                        {
                            "code": 500,
                            "message": "No data could be processed from the file",
                            "details": "null"
                        }
                    ],
                    "warnings": "null"
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {"application/json": {}}
        }
    }
)
async def parse_file(
        request: Request,
        file: UploadFile = File(..., description="Файл банковской выписки")) -> Response:
    """
    Parse and normalize uploaded file
    
    Args:
        request: FastAPI request object
        file: Uploaded file
        
    Returns:
        Response object with processing results
    """
    temp_file_path = None
    try:
        client_host = request.client.host
        logger.info(f"File parse request received from {client_host} with file {file.filename}")

        # Validate file
        await validate_file(file)

        # Save file to temp directory
        file_process_dir = settings.PATH_TO_UPLOAD_DIRECTORY / os.path.splitext(os.path.basename(file.filename))[0]
        file_process_dir.mkdir(parents=True, exist_ok=True)
        temp_file_path = settings.PATH_TO_UPLOAD_DIRECTORY / file_process_dir / file.filename
        try:
            content = await file.read()
            with open(temp_file_path, "wb") as f:
                f.write(content)
            logger.info(f"File {file.filename} saved to {temp_file_path}")
        except Exception as e:
            logger.error(f"Failed to save file: {str(e)}")
            return Response(
                content=NormalizeResponse.failure(
                    message="Failed to save file",
                    errors=[Error(code=500, message=str(e))]
                ).model_dump_json(),
                status_code=500,
                media_type="application/json"
            )

        # Process file
        try:
            result = process_file(temp_file_path)
            if result.errors and len(result.errors) > 0:
                return Response(
                    content=NormalizeResponse.failure(
                        message=ResultMessages.ERROR_FILE_CONVERSION_FAILED.message,
                        errors=[Error(code=err.code, message=err.message, details=err.details) for err in
                                result.errors],
                        status_code=ResultMessages.ERROR_FILE_CONVERSION_FAILED.status_code
                    ).model_dump_json(),
                    status_code=ResultMessages.ERROR_FILE_CONVERSION_FAILED.status_code
                )
            if result.warnings and len(result.warnings) > 0:
                return Response(
                    content=NormalizeResponse.success_with_warnings(
                        message="File processed with warnings",
                        data=result.data,
                        file_path=str(result.file_path),
                        warnings=[
                            CustomWarning(
                                code=warn.code,
                                message=warn.message,
                                details=warn.details
                            ) for warn in result.warnings
                        ]
                    ).model_dump_json(),
                    status_code=299,
                    media_type="application/json"
                )

            return Response(
                content=NormalizeResponse.success(
                    message="File processed successfully",
                    data=result.data,
                    file_path=str(result.file_path)
                ).model_dump_json(),
                status_code=200,
                media_type="application/json"
            )
        except Exception as e:
            logger.error(f"Failed to process file: {str(e)}")
            return Response(
                content=NormalizeResponse.failure(
                    message="Failed to process file",
                    errors=[Error(code=ResultMessages.ERROR_FILE_CONVERSION_FAILED.status_code,
                                  message=ResultMessages.ERROR_FILE_CONVERSION_FAILED.message,
                                  details={"error": str(e)})]
                ).model_dump_json(),
                status_code=500,
                media_type="application/json"
            )

    except HTTPException as e:
        logger.error(f"HTTP error processing file: {str(e.detail)}")
        return Response(
            content=NormalizeResponse.failure(
                message=str(e.detail),
                errors=[Error(code=ResultMessages.ERROR_HTTP_FAILED.status_code,
                              message=ResultMessages.ERROR_HTTP_FAILED.message,
                              details={"error": str(e)})]
            ).model_dump_json(),
            status_code=e.status_code,
            media_type="application/json"
        )
    except Exception as e:
        logger.error(f"Unexpected error processing file: {str(e)}")
        return Response(
            content=NormalizeResponse.failure(
                message="Internal server error",
                errors=[Error(code=ResultMessages.ERROR_PARSING_FAILED.status_code,
                              message=ResultMessages.ERROR_PARSING_FAILED.message,
                              details={"error": str(e)})]
            ).model_dump_json(),
            status_code=500,
            media_type="application/json"
        )
