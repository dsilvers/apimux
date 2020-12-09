from celery import Celery
from flask import Flask

from requests import Request, Session
import urllib.parse as urlparse
from urllib.parse import urlencode

from config.config import CELERY_BROKER_URL, RESULT_BACKEND


def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['result_backend'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


flask_app = Flask(__name__)
flask_app.config.update(
    CELERY_BROKER_URL=CELERY_BROKER_URL,
    result_backend=RESULT_BACKEND,
)
celery = make_celery(flask_app)


@celery.task()
def send_apimux(endpoint, id, method, headers, path, args, form, files):
    # Add args to endpoint URL
    # https://stackoverflow.com/a/2506477
    url_parts = list(urlparse.urlparse(endpoint + path))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update(args)
    url_parts[4] = urlencode(query)
    url = urlparse.urlunparse(url_parts)

    # Attach uploaded files to the request
    upload_files = {}
    for key, file in files:
        head, tail = os.path.split(file)
        upload_files[key] = (tail, open(file, 'rb'))

    sess = Session()
    req = Request(method, url, data=form, headers=headers, files=upload_files)
    prepped = sess.prepare_request(req)
    resp = sess.send(prepped)
    return resp.content
