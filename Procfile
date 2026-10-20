release: cd django_app && python manage.py migrate --noinput && python manage.py collectstatic --noinput
web: cd django_app && gunicorn decision_lab.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 60
