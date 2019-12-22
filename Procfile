web: waitress-serve --port=$PORT analysts_toolbox:app
worker: celery worker -A celery_worker.celery --loglevel=info