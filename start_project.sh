#!/bin/bash

# Check if environment variables are set
if [ -z "${DB_NAME}" ] || [ -z "${DB_USERNAME}" ] || [ -z "${DB_PASSWORD}" ]; then
    echo "Please set DB_NAME, DB_USERNAME, and DB_PASSWORD environment variables."
    exit 1
fi

# Check if the container is already running
if [ "$(docker ps -q -f name=llm-service-web-1)" ]; then
    echo "Container web is already running. Stopping and removing the old container."
    docker-compose down -v
fi

# Build and start the containers
docker-compose up --build -d

# Wait for the services to start
echo "Waiting for services to start..."
sleep 40

# Migrate the database
docker-compose exec web python manage.py migrate

# Create superuser if not exists
if docker-compose exec web python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print(User.objects.filter(username='admin').exists())" | grep -q "False"; then
    echo "Creating superuser for Django..."
    docker-compose exec web python manage.py createsuperuser --email admin@example.com --username admin --noinput
    docker-compose exec web python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); user = User.objects.get(username='admin'); user.set_password('admin'); user.save()"
else
    echo "Superuser already exists. Skipping creation."
fi

echo "Done!"
