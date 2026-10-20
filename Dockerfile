FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY django_app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY . /app
WORKDIR /app/django_app
RUN DJANGO_DEBUG=0 DJANGO_SECRET_KEY=build-only-static-secret-not-for-runtime DJANGO_ALLOWED_HOSTS=localhost DJANGO_SECURE_SSL_REDIRECT=0 python manage.py collectstatic --noinput
EXPOSE 8000
CMD ["gunicorn","decision_lab.wsgi:application","--bind","0.0.0.0:8000","--workers","3","--timeout","60"]
