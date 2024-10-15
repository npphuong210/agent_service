# Use the official Python slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install dependencies required for building psycopg2
RUN apt-get update \
    && apt-get install -y gcc python3-dev libpq-dev postgresql-client dos2unix \
    && apt-get clean

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy all source code into the container
COPY . /app/

# Convert .env and .sh files to Unix format
RUN find /app/ -type f \( -name "*.env" -o -name "*.sh" \) -exec dos2unix {} \;

# Command to run Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
