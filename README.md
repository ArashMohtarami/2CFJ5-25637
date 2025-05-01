# Restaurant Booking System


## Setup (Development)

### 1. Clone the repository and go into the directory


```bash
# with ssh
git clone git@github.com:ArashMohtarami/2CFJ5-25637.git

# with user token
git clone https://github.com/ArashMohtarami/2CFJ5-25637.git

cd 2CFJ5-25637/
```

### 2. Create and activate virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Prepare Settings:
### 4. Set up `settings.ini` ( two options )

#### option 1:
- Create a `settings.ini` file and add the content of the `settings.dev.ini`

#### option 2:

```bash
cp settings.dev.ini settings.ini
```

### 5. Secret Key Configuration

Add a secret key to `settings.ini` file.

```py
import secrets

print(secrets.token_urlsafe(50))
```

**TIP:** Copy generated secret key to `settings.ini` with `SECRET_KEY`.

```ini
SECRET_KEY=<your-strong-password>
```

### 6. Database Configuration

Now you need to config your database configuration.

```ini
# your database name that is created on postgreSQL
DB_NAME=

# Enter your database user and it must have access to the created db.
DB_USER=

# Enter your specified user's database password.
DB_PASSWORD=

# Accessible port of the installed database (default is `5432`)
DB_PORT=

# Local Database is `localhost` if you are using docker must enter `docker-service-name`
DB_HOST=

# Select a test database name for the created user.
DB_TEST=
```

## Prepare Development Environment:

Before project running, you must run tests to check project is work correctly. To run the tests, `cd` into the directory where `manage.py` is already exist:

#### Run Unit Tests:

```bash
python manage.py test
```

### Run migrations to database

```bash
python manage.py makemigrations
python manage.py migrate
```

#### Run Project

You can now run the development server:

```bash
python manage.py runserver 8000
```

### 7. Access the system

- Django Admin: http://localhost:8000/admin
- API docs URL: http://localhost:8000/api/docs/


#  Testing the API

#### 1. Create Superuser
Before accessing the Django Admin, you need to create a superuser account:

```bash
python manage.py createsuperuser
```
#### 2. Create data
to work with API at first it's needed to add some table for restaurant, so you can do it on the [Django admin](http://localhost:8000/admin) `table section`

then you can work with APIs
