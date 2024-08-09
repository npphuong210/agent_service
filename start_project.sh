#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    set -o allexport
    source .env
    set +o allexport
    echo "Environment variables loaded."
else
    echo ".env file not found!"
    exit 1
fi

# Check if environment variables are set
if [ -z "${DB_NAME}" ] || [ -z "${DB_USERNAME}" ] || [ -z "${DB_PASSWORD}" ]; then
    echo "Please set DB_NAME, DB_USERNAME, and DB_PASSWORD environment variables."
    exit 1
fi

# Check if the container exists
if [ "$(docker ps -a -q -f name=llm-service-web-1)" ]; then
    echo "Container 'llm-service-web-1' already exists."
    # Check if the container is running
    if [ "$(docker ps -q -f name=llm-service-web-1)" ]; then
        echo "Container web is already running. Stopping the old container."
        docker-compose down
    fi
    # Start the containers using the existing image
    echo "Starting containers with existing images..."
    docker-compose --env-file .env up -d
else
    echo "Container does not exist. Building and starting the containers."
    # Build and start the containers
    echo "Building and starting containers..."
    docker-compose --env-file .env build
    docker-compose --env-file .env up -d
fi

# Wait for the services to start
echo "Waiting for services to start..."
sleep 40

# Migrate the database
echo "Running database migrations..."
docker-compose exec web python manage.py migrate

# Create superuser if not exists
echo "Checking for existing superuser..."
if docker-compose exec web python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print(User.objects.filter(username='admin').exists())" | grep -q "False"; then
    echo "Creating superuser for Django..."
    docker-compose exec web python manage.py createsuperuser --email admin@example.com --username admin --noinput
    docker-compose exec web python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); user = User.objects.get(username='admin'); user.set_password('admin'); user.save()"
else
    echo "Superuser already exists. Skipping creation."
fi

echo "Done!"
