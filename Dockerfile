# syntax=docker/dockerfile:1

# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.9-slim-buster
EXPOSE 5000 8000 80

ENV FLASK_ENV = "development"
ENV DOCKER_BUILD=1
# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

WORKDIR /chatApp

COPY requirements.txt .
# Install pip requirements
RUN pip install -r requirements.txt

COPY ./chatApp .

#During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["python","-m","flask","run","--host=0.0.0.0"]
#CMD ["uwsgi","--http :5000","--gevent","1000","--http-websockets","--master","--wsgi-file","app.py","--callable","app"]
#CMD uwsgi --http :5000 --gevent 1000 --http-websockets --master --wsgi-file app.py --callable app
