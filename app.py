from flask import Flask, request
from werkzeug.utils import secure_filename

import os
import uuid

from config.config import METHODS, UPLOAD_FOLDER, ENDPOINTS
from app_celery import send_apimux

app = Flask(__name__)


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

    # Save uploaded files locally, send a dictionary of uploaded files
    files = []
    if request.method in ['POST', 'PUT', 'PATCH']:
        for key in request.files.keys():
            for file in request.files.getlist(key):
                directory = '{}/{}'.format(UPLOAD_FOLDER, id)
                os.makedirs(directory, exist_ok=True)
                filename = secure_filename(file.filename)
                location = os.path.join(directory, filename)
                file.save(location)
                files.append([key, location])

    # Copy headers from the request, but ignore the Host and Content-Length
    # headers as they will be set later when rebuilding the request.
    headers = {}
    for key, value in request.headers:
        # Ignore these headers
        if key not in ['Host', 'Content-Length', 'Content-Type']:
            headers[key] = value

    first_endpoint = None
    for endpoint in ENDPOINTS:
        result = send_apimux.delay(
                endpoint=endpoint,
                id=id,
                method=request.method,
                headers=headers,
                path=path,
                args=request.args,
                form=request.form.to_dict(),
                files=files,
        )
        if not first_endpoint:
            first_endpoint = result

    return str(first_endpoint.wait())


if __name__ == "__main__":
    app.run()
