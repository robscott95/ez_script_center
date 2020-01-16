web: waitress-serve --port=$PORT run:app -url-scheme=https
worker: celery worker -A ez_script_center.celery_worker --loglevel=info