FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN apt-get update
RUN pip install -r requirements.txt
RUN apt-get install -y vim
RUN apt-get install -y dnsutils
RUN apt-get install -y postgresql-client-common 
RUN apt-get install -y postgresql-client

# Not verified
RUN django-admin.py startproject openuav .
RUN python3 manage.py startapp sim
# Not verified

ADD . /code/
