# Используем официальный образ Python
FROM python:3.11-slim

# Установка зависимостей системы
RUN apt-get update && apt-get install -y \
    libpq-dev gcc

# Установка рабочей директории
WORKDIR /app

# Копируем файлы проекта
COPY . /app

# Устанавливаем зависимости
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Собираем статику
RUN python manage.py collectstatic --noinput

# Открываем порт
EXPOSE 8000

# Команда запуска
CMD ["gunicorn", "inhouse_site.wsgi:application", "--bind", "0.0.0.0:8000"]
