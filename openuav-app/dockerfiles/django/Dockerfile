FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
RUN apt-get update
RUN apt-get install -y vim
RUN apt-get install -y dnsutils

# Not verified
RUN django-admin.py startproject openuav .
RUN python3 manage.py startapp sim
# Not verified

ADD . /code/