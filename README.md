# Veganwinners backend

## Prerequisites

First, create a file config.py in 'app/' with content:

```
DATABASE_URI = 'mysql://<user>:<password>@localhost:<port>/<database-name>'
CLARIFAI_KEY = '<the key>'
APPROVE_KEY = '<the approve password>'
API_KEY = '<the cloudinary api key>'
API_SECRET = '<the cloudinary api secret>'
CLOUD_NAME = '<the cloudinary name>'
```

## How to run this API locally

First, make sure you have a database running on mysql for the user and password specified.

### requirements
```txt
git
pip
direnv
```

### direnv

direnv makes sure the virtualenv is set up when you enter this directory
it is responsible for installing the relevant python packages and for setting environmental variables needed

### hook
To enable the direnv hook in bash:
```bash
echo 'eval "$(direnv hook bash)"'>> ~/.bashrc
. ~/.bashrc
```

### enable direnv
```bash
direnv allow
```

Check out your localhost:8000

## How to deploy this API on our GCP Compute Engine VM

```
# within a dedicated screen:
gunicorn --workers=3 --bind 0.0.0.0:8000 run
```
