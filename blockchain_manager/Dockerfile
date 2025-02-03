# Utilizamos una imagen base ligera de Python
FROM python:3.11-slim

# Variable para especificar la versión de Poetry
ENV POETRY_VERSION=1.5.1

# Establecemos el directorio de trabajo
WORKDIR /app

# Instalamos dependencias del sistema necesarias para compilar paquetes y Poetry
RUN apt-get update && \
    apt-get install --no-install-recommends -y build-essential curl && \
    rm -rf /var/lib/apt/lists/*

# Actualizamos pip y luego instalamos Poetry
RUN pip install --upgrade pip && \
    pip install "poetry==$POETRY_VERSION"

# Copiamos los archivos de gestión de dependencias al contenedor
# Es importante copiar primero el pyproject.toml y poetry.lock para aprovechar la cache de Docker
COPY global_pydependency /app/global_pydependency
COPY pyproject.toml poetry.lock* /app/

# Configuramos Poetry para que instale las dependencias en el entorno global (sin virtualenv)
RUN poetry config virtualenvs.create false

# Instalamos las dependencias sin el paquete raíz; si lo necesitas, puedes quitar el flag --no-root
RUN poetry install --no-interaction --no-ansi

# Copiamos el resto de la aplicación
COPY . /app

# Exponemos el puerto en el que se ejecutará la aplicación (FastAPI por defecto corre en 8000)
EXPOSE 8000

# Comando para arrancar la aplicación con uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
