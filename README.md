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
- Start application with python manage.py runserver
### Other tools
- Download and install [Atom](https://atom.io/)

### Debug
#### Test db connection
```bash
psql -U postgres -d restaurants
psql -h postgres.restaurants -U postgres -d restaurants
```
#### Restore DB dump
```bash
pg_restore -U postgres -d restaurants -1 /var/lib/postgresql/data/unified-restaurants
```

#### Test app image
```bash
docker image build -t restaurants-temp .
docker run --rm -it --entrypoint /bin/bash --name temp-restaurants restaurants-temp
```

## ToDo
- use relative path for image_titles of Data_processing_functions_final.py (example download from images_download.py)