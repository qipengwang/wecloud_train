FROM python:3.7

RUN mkdir /app
ADD . /app/
WORKDIR /app

RUN pip install -r requirements.txt
RUN mkdir data
RUN wget https://www.cs.toronto.edu/\~kriz/cifar-100-python.tar.gz -O data/cifar-100-python.tar.gz

RUN mkdir runs

EXPOSE 5000
EXPOSE 6006

ENTRYPOINT ["/bin/bash", "/app/entrypoint.sh"]