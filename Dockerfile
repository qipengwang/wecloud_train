FROM python:3.8

RUN mkdir /app
ADD . /app/
WORKDIR /app
# RUN pip install -r requirements.txt

EXPOSE 5000
