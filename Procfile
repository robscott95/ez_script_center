web: waitress-serve --port=$PORT run:app
worker: celery worker -A ez_script_center.celery_worker --loglevel=info