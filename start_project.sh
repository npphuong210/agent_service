#!/bin/bash

# Check if the container is already running
if [ "$(docker ps -q -f name=llm-service-web-1)" ]; then
    echo "Container web is already running. Stopping and removing the old container."
    docker-compose down -v
fi

# Build and start the containers
docker-compose up --build -d

# Wait for the services to start
echo "Waiting for services to start..."
sleep 30

# Migrate the database
docker-compose exec web python manage.py migrate

# Create superuser if not exists
if [ "$(docker-compose exec web python manage.py createsuperuser --email admin@example.com --username admin --noinput 2>&1 | grep 'Superuser created successfully.')" ]; then
    echo "Superuser already exists. Skipping creation."
else
    echo "Creating superuser for Django..."
    docker-compose exec web python manage.py createsuperuser --email admin@example.com --username admin
fi

echo "Done!"
