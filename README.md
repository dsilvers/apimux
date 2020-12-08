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

APIMUX is a simple flask app used to broadcast a HTTP request to multiple endpoints. Useful for sending the same data from one API to several, if you're doing weird 


### Development Env

Start the celery worker, main Flask app, and a couple of test server receivers. Make a request to the main Flask app and it should be forwarded to both of the test receivers on 8001/8002.

```
celery -A app_celery.celery worker -l INFO
FLASK_APP=app.py FLASK_ENV=development flask run
FLASK_APP=test_server.py FLASK_ENV=development flask run -p 8001
FLASK_APP=test_server.py FLASK_ENV=development flask run -p 8002
```