# Imagen base de Python
FROM python:3.10-slim

# Crear directorio de la app
WORKDIR /app

# Copiar archivos del repo al contenedor
COPY . /app

# Instalar dependencias
RUN pip install --no-cache-dir requests

# Comando para ejecutar tu bot
CMD ["python", "main.py"]