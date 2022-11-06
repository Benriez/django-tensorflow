#!/bin/sh
python3 manage.py collectstatic --noinput && python3 manage.py migrate && uvicorn django_project.asgi:application --proxy-headers --host=0.0.0.0 --port=80

