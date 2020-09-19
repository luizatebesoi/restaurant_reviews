# Restaurants reviews project
## Local Setup
### IDE
- Install [Anaconda](https://www.anaconda.com/products/individual)
### Database
- Download and install [Postgresql](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads) for windows
- Once Postgresql installed, open SQL Shell. User - ‘postgres’, password - ‘postgrespass’
- Create the database using the following command: “CREATE DATABASE restaurants;”
- Download and install the [pgAdmin](https://www.pgadmin.org/download/ ) tool

### Django
- Using Powershell install django with: “pip install django”
- Using Powershell, go to Desktop and create a new project with the command: “django-admin startproject restaurant_reviews”. This command creates a new folder on desktop called restaurants_project.  
- Go to the restaurants_project folder with the:  “cd restaurant_reviews” command
- Create a django app using: “python manage.py startapp restaurants” 
- Install libraries
```bash
pip install -r requirements.txt
```
- Start application with 
```bash
python manage.py runserver
```

### Debug
#### Test db connection
```bash
psql -U postgres -d restaurants
psql -h postgres.restaurants -U postgres -d restaurants
```
#### Restore DB dump
```bash
pg_restore -U postgres -d restaurants -1 /var/lib/postgresql/data/<db_dump_file>
```

#### Test app image
```bash
docker image build -t restaurant-reviews .
docker run --rm -it --entrypoint /bin/bash --name restaurant-reviews restaurant-reviews
```

### Crons
