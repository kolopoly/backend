FROM python:3.10-slim

RUN apt-get update
RUN apt-get -y install gcc openssh-client openssh-server pkg-config
RUN apt-get -y install default-libmysqlclient-dev

WORKDIR /code
COPY requirements.txt /code/requirements.txt
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN rm -rf /var/lib/apt/lists/*
COPY . /code
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DockerHOME=/home/app/webapp
CMD ./run.sh
EXPOSE 8000
