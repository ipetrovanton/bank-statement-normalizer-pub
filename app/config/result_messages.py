from enum import Enum


class ResultMessages(Enum):
    OK = ("OK", 200)
    FILE_PARSED = ("Файл успешно распарсен.", 200)
    WARNING_FILE_PARSED_INCORRECTLY = ("В распознанном файле есть некорректные данные.", 201)
    WARNING_HEADERS_NOT_CORRECT = ("Заголовки не корректны.", 299)
    ERROR_PARSING_FAILED = ("Файл невозможно распарсить. Проверьте содержимое.", 400)
    ERROR_FILE_READ_FAILED = ("Файл невозможно прочитать.", 404)
    ERROR_FILE_CONVERSION_FAILED = ("Файл невозможно конвертировать.", 422)
    ERROR_FILE_NAME_INCORRECT = ("Файл невозможно распознать.", 422)
    ERROR_DATAFRAME_CLEANUP_FAILED = ("DataFrame невозможно корректно очистить.", 423)
    ERROR_HEADER_CORRECTION_FAILED = ("Заголовки невозможно корректно исправить.", 424)
    ERROR_FILE_WRITE_FAILED = ("Файл невозможно записать.", 500)
    ERROR_HTTP_FAILED = ("HTTP-запрос невозможно выполнить.", 500)
    ERROR_DF_TO_JSON_FAILED = ("DataFrame невозможно преобразовать в JSON.", 500)
    ERROR_UNEXPECTED_ERROR = ("Произошла непредвиденная ошибка.", 500)
    ERROR_DOCX_FILE_NOT_FOUND = ("Файл DOCX не найден.", 404)
    ERROR_DOCX_UNSUPPORTED_FORMAT = ("Неподдерживаемый формат файла. Требуется .docx", 415)
    ERROR_DOCX_EMPTY_DOCUMENT = ("Пустой документ DOCX.", 422)
    ERROR_DOCX_SAVE_PERMISSION_DENIED = ("Нет прав для сохранения файла DOCX.", 403)
    ERROR_DOCX_CONVERSION_FAILED = ("Критическая ошибка при конвертации DOCX.", 499)

    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code

class ResultCode(Enum):
    ERROR_PARSING_FAILED = 40