#!/bin/bash
cd /srv/tebesoi/restaurant_reviews/

# Create media directories if needed
media_csv_path="/srv/tebesoi/restaurant_reviews/media/csv"
media_images_path="/srv/tebesoi/restaurant_reviews/media/restaurants/images"
if [ ! -d $media_csv_path ]
then
  mkdir -p $media_csv_path
  chmod +x $media_csv_path
fi
if [ ! -d $media_images_path ]
then
  mkdir -p $media_images_path
  chmod +x $media_images_path
fi

# Apply database migrations
python manage.py makemigrations --noinput
python3 manage.py migrate auth
python3 manage.py migrate --noinput

# Start server
python manage.py runserver 0.0.0.0:80