FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_TRUSTED_HOST=pypi.org
ENV PIP_TRUSTED_HOST=pypi.python.org
ENV PIP_TRUSTED_HOST=files.pythonhosted.org

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        libpq-dev \
        build-essential \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Update certificates
RUN update-ca-certificates

# Set work directory
WORKDIR /app

# Copy and install minimal Python dependencies first
COPY backend/requirements.minimal.txt /app/requirements.minimal.txt
RUN pip install --no-cache-dir --upgrade pip --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org \
    && pip install --no-cache-dir --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.minimal.txt

# Copy backend application code
COPY backend/ /app/

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/media

# Try to install full requirements (optional)
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt || echo "Warning: Some packages failed to install, continuing with minimal setup"

# Collect static files (for production)
RUN python manage.py collectstatic --noinput || true

# Expose port
EXPOSE 8000

# Run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
