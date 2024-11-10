FROM python:3.12.1 as builder

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de requerimientos y los instala
COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código de la aplicación
COPY . /app

# Variables de entorno para la conexión de base de datos
ENV DB_HOST="ColeXpertDB"
ENV DB_PORT="3306"
ENV DB_NAME="ColeXpertDB"
ENV DB_USER="admin"
ENV DB_PASSWORD="admin"

EXPOSE 8000

FROM nginx:alpine

# Copiar el archivo de configuración de NGINX
COPY nginx.conf /etc/nginx/nginx.conf

# Copiar la aplicación FastAPI construida 
COPY --from=builder /app /app

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias necesarias para crear un entorno virtual y pip
RUN apk add --no-cache python3 py3-pip bash

# Crear entorno virtual
RUN python3 -m venv /venv

# Activar el entorno virtual y luego instalar las dependencias
RUN /venv/bin/pip install --no-cache-dir -r /app/requirements.txt

# Variables de entorno para la conexión de base de datos
ENV DB_HOST="ColeXpertDB"
ENV DB_PORT="3306"
ENV DB_NAME="ColeXpertDB"
ENV DB_USER="admin"
ENV DB_PASSWORD="admin"

# Exponer el puerto de NGINX (80)
EXPOSE 80

# Comando para iniciar NGINX y Uvicorn
CMD ["sh", "-c", "source /venv/bin/activate && uvicorn app:app --host 0.0.0.0 --port 8000 & nginx -g 'daemon off;'"]

