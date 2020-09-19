#
# https://hub.docker.com/_/python?tab=description&page=1&name=3
#
FROM python:3.8.5-buster
ENV PYTHONUNBUFFERED 1

# Project location
RUN mkdir -p /srv/tebesoi/restaurants/
WORKDIR /srv/tebesoi/restaurants/

# Install requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Application config
COPY . .
ARG ENV_SETTINGS=prod
RUN cp /srv/tebesoi/restaurants/restaurant_reviews/settings_$ENV_SETTINGS.py /srv/tebesoi/restaurants/restaurant_reviews/settings.py

# Change DB host
ARG DB_HOST=postgres.restaurants
RUN find ./scripts/ -type f -exec sed -i -r "s/localhost/${DB_HOST}/g" {} \;
RUN find ./scripts/ -type f -exec sed -i -r "s/postgrespass/reviews/g" {} \;

EXPOSE 80
ENTRYPOINT ["docker-entrypoint.sh"]