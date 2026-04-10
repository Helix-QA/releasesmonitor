FROM python:3.12-slim

WORKDIR /app

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем скрипт
COPY monitor_1c.py .

# Папка для хранения версий
VOLUME /data

CMD ["python", "monitor_1c.py"]