# Zebra Crossing

Traffic management application for the radio industry.

# Building

Zebra Crossing is built using Django. A development environment can be set up using:

```
$ virtualenv -p python3 pyenv
$ pyenv/bin/pip install -r requirements.txt
$ yarn install
$ pyenv/bin/python manage.py migrate
$ pyenv/bin/python manage.py createsuperuser
$ pyenv/bin/python manage.py runserver
```

This will start a development web server on http://127.0.0.1:8000/
