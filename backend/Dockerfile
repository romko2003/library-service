FROM python:3.12-slim

WORKDIR /app

# Install system deps if needed (psycopg2, etc.)
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

COPY ../requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY . /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["gunicorn", "library.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
, "-b"]