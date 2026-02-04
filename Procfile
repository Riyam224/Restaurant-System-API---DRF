web: python manage.py migrate && python manage.py create_superuser_if_not_exists && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
