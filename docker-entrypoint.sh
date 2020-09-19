#!/bin/bash
cd /srv/tebesoi/restaurants/

# Apply database migrations
python manage.py makemigrations --noinput
python3 manage.py migrate auth
python3 manage.py migrate --noinput

# Start server
python manage.py runserver 0.0.0.0:80