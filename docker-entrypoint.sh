#!/bin/bash

# Apply database migrations
echo "Database migrations"
python manage.py makemigrations
python manage.py makemigrations poc
python manage.py migrate

# wait for DB came up first
sleep 10
# Start server
echo "Starting server"
python manage.py runserver 0.0.0.0:8080