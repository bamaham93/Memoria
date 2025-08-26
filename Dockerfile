# Use slim Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies (SQLite, etc.)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Collect static files (for Django Admin CSS/JS, etc.)
RUN python manage.py collectstatic --noinput

# Expose Django on port 8000
EXPOSE 8000

# Run migrations, then start Gunicorn
CMD ["sh", "-c", "python manage.py migrate && gunicorn memoria.wsgi:application --bind 0.0.0.0:8000"]
