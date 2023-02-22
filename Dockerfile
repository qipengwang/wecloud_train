FROM python:3.7

RUN mkdir /app
ADD . /app/
WORKDIR /app
RUN pwd && ls
RUN pip install -r requirements.txt
RUN wget https://www.cs.toronto.edu/\~kriz/cifar-100-python.tar.gz -O wecloud_train/data/cifar-100-python.tar.gz

EXPOSE 5000
