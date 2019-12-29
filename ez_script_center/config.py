import os

# Might be better to downlod it from google openid-configuration
ACCESS_TOKEN_URI = 'https://oauth2.googleapis.com/token'
AUTHORIZATION_URL = 'https://accounts.google.com/o/oauth2/v2/auth?access_type=offline&prompt=consent'
GOOGLE_AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_USERINFO_ENDPOINT = "https://openidconnect.googleapis.com/v1/userinfo"

GOOGLE_AUTH_REDIRECT_URI = os.environ.get("GOOGLE_AUTH_REDIRECT_URI", default=False)
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", default=False)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", default=False)

AUTHORIZATION_SCOPE = ['openid', 'email', 'profile']

CELERY_BROKER_URL = os.environ.get("REDIS_URL")
CELERY_ACCEPT_CONTENT = os.environ.get("CELERY_ACCEPT_CONTENT",
                                       ["json", "yaml", "pickle"])
CELERYD_TASK_SOFT_TIME_LIMIT = os.environ.get("CELERYD_TASK_SOFT_TIME_LIMIT", 300)

APP_SECRET_KEY = os.environ.get("APP_SECRET_KEY")
DATABASE_URL = os.environ.get("DATABASE_URL")

S3_BUCKET = os.environ.get("S3_BUCKET")
