from flask import Flask, Response, request


METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD']


app = Flask(__name__)


@app.route("/", defaults={"path": ""}, methods=METHODS)
@app.route("/<path:path>", methods=METHODS)
def api_server(path):

    content = """METHOD: {}
PATH: {}
HEADERS: {}
GET ARGS: {}
FORM DATA: {}
FILES: {}""".format(
        request.method,
        path,
        request.headers,
        request.args,
        request.form,
        request.files,
    )

    print(content)
    return Response(content, mimetype='text/plain')
