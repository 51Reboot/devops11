# Makefile for project

APP = ops11
STATIC_DIR = static/

migrate:
	@python manage.py makemigrations
	@python manage.py migrate

run:
	@python manage.py runserver 0.0.0.0:9000