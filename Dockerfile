# Dockerfile para aplicación Quart

# Paso 1: Usar imagen oficial de Python 3.14 slim (ligera)
FROM python:3.14-slim

# Paso 2: Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Paso 3: Instalar dependencias del sistema necesarias para PostgreSQL (libpq-dev y gcc para compilar)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Paso 4: Copiar el archivo de requerimientos para instalar dependencias de Python
COPY requirements.txt .

# Paso 5: Instalar las dependencias de Python desde requirements.txt sin usar caché
RUN pip install --no-cache-dir -r requirements.txt

# Paso 6: Copiar todo el código de la aplicación al directorio de trabajo
COPY . .

# Paso 7: Exponer el puerto 4520 para la aplicación
EXPOSE 4520

# Paso 8: Comando para ejecutar la aplicación con Hypercorn (servidor ASGI para Quart)
CMD ["hypercorn", "main:app", "--bind", "0.0.0.0:4520"]