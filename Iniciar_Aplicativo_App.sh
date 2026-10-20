#!/bin/sh
set -eu
cd "$(dirname "$0")"
if [ ! -x ".venv-app/bin/python" ]; then
  python3 -m venv .venv-app
fi
. .venv-app/bin/activate
python -m pip install -r django_app/requirements.txt
cd django_app
python manage.py migrate --noinput
printf '\nAplicativo App: http://127.0.0.1:8000/aplicativo-app/\n'
python manage.py runserver 127.0.0.1:8000
