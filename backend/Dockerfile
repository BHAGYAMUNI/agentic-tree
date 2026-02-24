FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy backend code (including venv folder where main.py lives)
COPY . /app

ENV PYTHONUNBUFFERED=1

EXPOSE 8000
RUN apt-get update && apt-get install -y netcat-openbsd
CMD ["sh", "-c", "until nc -z db 5432; do echo waiting for db; sleep 2; done; uvicorn main:app --host 0.0.0.0 --port 8000"]