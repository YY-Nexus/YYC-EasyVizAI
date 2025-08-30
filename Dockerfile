FROM python:3.10-slim
WORKDIR /app
COPY . /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Python dependencies with SSL fix
RUN pip install --upgrade pip --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
RUN pip install --no-cache-dir -r requirements-docker.txt --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org

WORKDIR /app/backend
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
