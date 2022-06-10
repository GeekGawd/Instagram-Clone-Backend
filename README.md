# Instagram-Clone-Backend

### This is a photo-sharing clone whose backend is made in Django Rest Framework.

## Tech-Stack:

- Android (Kotlin) app as the frontend.
- API Endpoints written in Django and Django Rest Framework, written following the best practices.
- PostgreSQL for the DB because of its open source nature and several useful features.
- JWT Authentication with complete integration of Refresh and Access tokens.
- Dockerise the Django App for easy deployment and testing.
- Celery for background tasking (Sending Emails in the Backgroud)
- Redis to act as a broker and task queue
- Was Deployed on AWS EC2 instance. (had to disable it for pricing reasons)
- Used Gunicorn as Forward Proxy
- Nginx for Reverse Proxy
- Django Signals for asynchronous programming like Instagram Notifications etc.
- Django Websockets used for Instagram Chat.

## Installation:

Checkout and Clone the docker branch and run the following command:

`docker-compose up --build -d`
