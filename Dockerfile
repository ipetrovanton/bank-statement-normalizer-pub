# Базовый образ Anaconda
FROM continuumio/anaconda3

# Метаданные
LABEL authors="thinkpad"
LABEL description="Bank Statement Normalizer Application"

# Рабочая директория
WORKDIR /app

# Копирование всех файлов проекта
COPY . .

# Создание conda окружения
RUN conda env create -f environment.yml

# Активация окружения
ENV PATH /opt/conda/envs/app_env/bin:$PATH

# Создание директории для загрузок и логов с правильными правами
RUN mkdir -p /app/uploads /logs && \
    touch /logs/app.log && \
    chmod 666 /logs/app.log

# Переменные окружения Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Порт приложения
EXPOSE 8000

# Команда запуска
CMD ["conda", "run", "-n", "app_env", "python", "-m", "uvicorn", "app.main:app_api", "--host", "0.0.0.0", "--port", "8000"]
