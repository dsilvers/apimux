# Rename to config.py for local config.
# This file is in git.

# Destination folder for uploads
UPLOAD_FOLDER = '/tmp/apimux'

# Allowed HTTP request types
METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD']

# A list of endpoints that the HTTP request will be broadcast to.
# The first endpoint is the one where we return the request.
ENDPOINTS = (
    'http://localhost:8001/',
    'http://localhost:8002/'
)

RESULT_BACKEND = "redis://localhost:6379"
CELERY_BROKER_URL = "redis://localhost:6379"
