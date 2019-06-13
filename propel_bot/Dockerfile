FROM python:3.7

ADD . /propel_bot
WORKDIR /propel_bot
RUN pip install -r requirements.txt
CMD gunicorn --bind localhost:80 wsgi:app
