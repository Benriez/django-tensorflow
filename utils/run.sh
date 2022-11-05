#!/bin/sh
python3 manage.py collectstatic --noinput && python3 manage.py migrate && gunicorn django_project.wsgi --bind=0.0.0.0:80

