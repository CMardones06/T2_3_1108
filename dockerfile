# Usamos una imagen oficial de Python ligera
FROM python:3.11-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalar dependencias del sistema necesarias si alguna librería lo requiere
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar 'uv' globalmente en el contenedor para manejar dependencias rápido
RUN pip install --no-cache-dir uv

# Copiar archivos de configuración de dependencias
COPY pyproject.toml uv.lock* ./

# Instalar las dependencias del proyecto usando uv
RUN uv sync --frozen --no-dev || uv pip install --system .

# Copiar el resto del código del proyecto al contenedor
COPY . .

# Exponer el puerto en el que corre FastAPI
EXPOSE 8000

# Comando por defecto para iniciar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]