from celery import Celery
from flask import Flask, request
from werkzeug.utils import secure_filename

import os
from requests import Request, Session
import urllib.parse as urlparse
from urllib.parse import urlencode
import uuid


UPLOAD_FOLDER = '/tmp/apimux'
METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD']
ENDPOINTS = (
    'http://localhost:8000/',
    #'http://localhost:8001/'
)


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


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
    CELERY_BROKER_URL='redis://localhost:6379',
    result_backend='redis://localhost:6379',
)
celery = make_celery(flask_app)


@celery.task()
def send_apimux(endpoint, id, method, path, args, form, files):

    # add args to endpoint URL
    # https://stackoverflow.com/a/2506477
    url_parts = list(urlparse.urlparse(endpoint + path))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update(args)
    url_parts[4] = urlencode(query)
    url = urlparse.urlunparse(url_parts)

    upload_files = []
    for key, file in files:
        head, tail = os.path.split(file)
        upload_files.append(
            (key, (tail, open(file, 'rb')))
        )

    sess = Session()
    req = Request(method, url, data=form, files=files)
    prepped = req.prepare()
    resp = sess.send(prepped)
    return resp.status_code

    #return "--ENDPOINT-- {} --METHOD-- {} --PATH-- {} --ARGS-- {} --FORM-- {} --FILES-- {}".format(endpoint, 
    #    method, path,  args,  form, files)


@app.route("/", defaults={"path": ""}, methods=METHODS)
@app.route("/<path:path>", methods=METHODS)
def apimux(path):
    """
    For 'reflecting' all content sent, we need to retain a bunch of
    information and data:
    - Request type (request.method)
    - Request path (path)
    - GET args (request.args)
    - FORM data (request.form)
    - Files data (request.files)
    """
    id = uuid.uuid4()

    files = []
    if request.method in ['POST', 'PUT', 'PATCH']:
        for key in request.files.keys():
            for file in request.files.getlist(key):
                directory = '{}/{}'.format(app.config['UPLOAD_FOLDER'], id)
                os.makedirs(directory, exist_ok=True)
                filename = secure_filename(file.filename)
                location = os.path.join(directory, filename)
                file.save(location)
                files.append((key, location))

    first_endpoint = None
    for endpoint in ENDPOINTS:
        result = send_apimux.delay(
                endpoint=endpoint,
                id=id,
                method=request.method,
                path=path,
                args=request.args,
                form=request.form,
                files=files,
        )
        if not first_endpoint:
            first_endpoint = result

    return str(first_endpoint.wait())
