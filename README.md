# Veganwinners backend

## Prerequisites

First, create a file config.py in 'app/' with content:

```
DATABASE_URI = 'mysql://<user>:<password>@localhost:<port>/<database-name>'
CLARIFAI_KEY = '<the key>'
APPROVE_KEY = '<the approve password>'
```

## How to run this API locally

Make sure you have a database running on mysql for the user and password specified.
Then simply run the following.

```
pip install -r requirements.txt
python3 run.py
```

Check out your localhost:8000

## How to deploy this API on our GCP Compute Engine VM

with gunicorn in screen
```
# within a dedicated screen:
gunicorn --workers=3 --bind 0.0.0.0:8000 run
```
