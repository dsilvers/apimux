```
     /\  \         /\  \                   /\  \         /\  \         /|  |     
    /::\  \       /::\  \     ___         |::\  \        \:\  \       |:|  |     
   /:/\:\  \     /:/\:\__\   /\__\        |:|:\  \        \:\  \      |:|  |     
  /:/ /::\  \   /:/ /:/  /  /:/__/      __|:|\:\  \   ___  \:\  \   __|:|__|     
 /:/_/:/\:\__\ /:/_/:/  /  /::\  \     /::::|_\:\__\ /\  \  \:\__\ /::::\__\_____
 \:\/:/  \/__/ \:\/:/  /   \/\:\  \__  \:\~~\  \/__/ \:\  \ /:/  / ~~~~\::::/___/
  \::/__/       \::/__/     ~~\:\/\__\  \:\  \        \:\  /:/  /      |:|~~|    
   \:\  \        \:\  \        \::/  /   \:\  \        \:\/:/  /       |:|  |    
    \:\__\        \:\__\       /:/  /     \:\__\        \::/  /        |:|__|    
     \/__/         \/__/       \/__/       \/__/         \/__/         |/__/     
```

APIMUX is a simple flask app used to broadcast a HTTP request to multiple endpoints. Useful for sending the same data from one API to several endpoints at the same time.

Caveats currently:

- No retries on the celery job. If your request to an endpoint fails, it's gone.
- No error reporting. Do it server side on your endpoints.
- Likely bugs with relaying header information, content types, form parameters with the same name, and other oddities.
- File uploads are stored by default at `/tmp/apimux`. Guess what? You'll probably want a cronjob or a celery task after a request completes or something to clean them out.

This app was developed to relay remote camera images to multiple API's at the same time.

### Development Env

Start the celery worker, main Flask app, and a couple of test server receivers. Make a request to the main Flask app and it should be forwarded to both of the test receivers on 8001/8002.

```
celery -A app_celery.celery worker -l INFO
FLASK_APP=app.py FLASK_ENV=development flask run
FLASK_APP=test_server.py FLASK_ENV=development flask run -p 8001
FLASK_APP=test_server.py FLASK_ENV=development flask run -p 8002
```
