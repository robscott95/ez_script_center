web: waitress-serve --port=$PORT ez_script_center:app
worker: celery worker -A ez_script_center.celery_worker --loglevel=info