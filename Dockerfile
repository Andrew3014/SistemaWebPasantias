FROM python:3.11-slim

# 1. Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. Copiar requirements primero para cachear la instalación
COPY requirements.txt .

# 3. Instalar dependencias de Python
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 4. Copiar el resto de la aplicación
COPY . .

CMD ["python", "app.py"]
