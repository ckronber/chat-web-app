# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.8
#-slim-buster

EXPOSE 5000

ENV DOCKER_BUILD=1

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
# Install pip requirements
RUN pip install -r requirements.txt

COPY ./chat-app ./chat

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
#CMD ["--bind", "0.0.0.0:5000", "./chat/app:sio"]
#CMD ["gunicorn","-w", "1","./chat/app:app"]
CMD ["python", "./chat/app.py"]