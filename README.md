# Bank Statement Normalizer

## 1. Prerequisites
- Python 3.13+
- Conda (рекомендуется)
- Docker (опционально)
- Git

## 2. Клонирование репозитория
```bash
git clone https://github.com/ipetrovanton/bank-statement-normalizer-pub.git
cd bank-statement-normalizer-pub
```

## 3. Настройка виртуального окружения

### 3.1 Conda
```bash
# Создание окружения
conda env create -f environment.yml
conda activate app_env

# Активация окружения
conda activate app_env
```

## 4. Конфигурация

### 4.1 Переменные окружения
Отредактируйте `.env` файл:

Основные параметры:
- `MAX_UPLOAD_SIZE`: Максимальный размер загружаемого файла (байты)
- `CORS_ORIGINS`: Разрешенные домены
- `LOG_LEVEL`: Уровень логирования

### 4.2 Логирование
Настройте `app/config/logging_config.json`:
Главное, корректно указать путь к логам.
```json
{
     "file": {
      "class": "logging.handlers.TimedRotatingFileHandler",
      "level": "DEBUG",
      "formatter": "detailed",
      "filename": "../logs/app.log", 
      "when": "M",
      "interval": 1,
      "backupCount": 2,
      "encoding": "utf8"
    }
}
```

## 5. Запуск приложения

### 5.1 Локальный запуск
```bash
# Запуск через uvicorn
uvicorn app.main:app_api --reload --host 0.0.0.0 --port 8000
```

### 5.2 Docker
```bash
# Сборка образа
docker build -t bank-statement-normalizer .

# Запуск контейнера
docker run -p 8000:8000 \
    -v /path/to/uploads:/app/uploads \
    bank-statement-normalizer
```

## 6 Эндпоинты 
Эндпоинты описаны в документации swagger:
- `/docs` - Swagger UI
- `/redoc` - ReDoc документация
