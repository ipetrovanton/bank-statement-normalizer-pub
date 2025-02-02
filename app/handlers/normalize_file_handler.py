import json
import logging
import os
from pathlib import Path

from app.config import result_messages
from app.config.config import settings
from app.config.result_table_config_processor import create_excel_from_config, load_config, append_df_to_excel
from app.converters.docx_to_xlsx_converter import docx_to_xlsx
from app.preprocessor.preprocessor import parse_xlsx_to_df, ErrorSeverity
from app.routers.normalize_response import NormalizeResponse, Error, CustomWarning

logger = logging.getLogger(__name__)

def process_file(file_path: Path) -> NormalizeResponse:
    response = select_flow_depends_on_file_extension(file_path)
    return response


def select_flow_depends_on_file_extension(file_name: Path) -> NormalizeResponse:
    if file_name.suffix == ".docx":
        converted_file_path = Path(os.path.dirname(file_name) + "/" + os.path.splitext(os.path.basename(file_name))[0] + ".xlsx")
        is_ok, errors = docx_to_xlsx(file_name, converted_file_path)
        if is_ok:
            return parse_excel_file(converted_file_path)
        else:
            return NormalizeResponse.failure(
                message=result_messages.ResultMessages.ERROR_DOCX_CONVERSION_FAILED.message,
                errors=[Error(code=error.code, message=error.message, details=error.details) for error in errors],
                status_code=result_messages.ResultMessages.ERROR_DOCX_CONVERSION_FAILED.status_code,
            )
    if file_name.suffix in [".xlsx", ".xls"]:
        return parse_excel_file(file_name)

def parse_excel_file(file_path: Path) -> NormalizeResponse:
    try:
        file_path_str = str(file_path)
        logger.info(f"Processing file: {file_path_str}")
        
        # New processing method with ProcessingError
        df, processing_errors = parse_xlsx_to_df(file_path_str)
        
        # Check for critical errors first
        critical_errors = [error for error in processing_errors if error.severity == ErrorSeverity.CRITICAL]
        if critical_errors:
            logger.error(f"Critical errors processing file: {critical_errors}")
            return NormalizeResponse.failure(
                message=result_messages.ResultMessages.ERROR_FILE_READ_FAILED.message,
                errors=[Error(code=error.code, message=error.message, details=error.details) for error in critical_errors],
                status_code=result_messages.ResultMessages.ERROR_FILE_READ_FAILED.status_code,
            )

        # If no data was processed
        if df.empty:
            logger.warning("No data could be processed from the file")
            return NormalizeResponse.failure(
                status_code=result_messages.ResultMessages.ERROR_FILE_READ_FAILED.status_code,
                message=result_messages.ResultMessages.ERROR_FILE_READ_FAILED.message,
                errors=[Error(code=500, message="No data could be processed from the file")]
            )

        try:
            converted_file_path = create_excel_from_config(load_config(settings.PATH_TO_CONFIG_RESULT_TABLE), file_path)
            append_df_to_excel(converted_file_path, df, sheet_name='Report', start_row=4, start_col=2)
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            return NormalizeResponse.failure(status_code = result_messages.ResultMessages.ERROR_FILE_WRITE_FAILED.status_code, message=result_messages.ResultMessages.ERROR_FILE_WRITE_FAILED.message, errors=[Error(code=result_messages.ResultMessages.ERROR_FILE_WRITE_FAILED.status_code, message=str(e))])

        try:
            result_json = df.to_json(orient="table")
            result_json = json.loads(result_json)
        except Exception as e:
            logger.error(f"Error converting dataframe to json: {str(e)}")
            return NormalizeResponse.failure(status_code=result_messages.ResultMessages.ERROR_DF_TO_JSON_FAILED.status_code, message=result_messages.ResultMessages.ERROR_DF_TO_JSON_FAILED.message, errors=[Error(code=result_messages.ResultMessages.ERROR_DF_TO_JSON_FAILED.status_code, message=str(e))])

        # Handle warnings separately
        warnings = [error for error in processing_errors if error.severity == ErrorSeverity.WARNING]
        if warnings:
            logger.warning(f"Warnings processing file: {', '.join([w.message for w in warnings])}")
            return NormalizeResponse.success_with_warnings(
                message=result_messages.ResultMessages.WARNING_FILE_PARSED_INCORRECTLY.message,
                warnings=[CustomWarning(code=w.code, message=w.message, details=w.details) for w in warnings],
                data=result_json, 
                file_path=file_path_str
            )

        logger.info(f"File {file_path_str} processed successfully")
        return NormalizeResponse.success(
            message=result_messages.ResultMessages.FILE_PARSED.message, 
            data=result_json, 
            file_path=converted_file_path
        )
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return NormalizeResponse.failure(
            message=result_messages.ResultMessages.ERROR_PARSING_FAILED.message,
            status_code=result_messages.ResultMessages.ERROR_PARSING_FAILED.status_code,
            errors=[Error(code=result_messages.ResultMessages.ERROR_UNEXPECTED_ERROR.status_code, message=str(e))]
        )
