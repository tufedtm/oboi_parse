FROM python:3.6

ENV PYTHONUNBUFFERED 1

#RUN mkdir /code

WORKDIR /code

RUN pip install -U setuptools Scrapy

#COPY req.txt /code/
#
#RUN pip install -r req.txt

#COPY . /code/

#ENTRYPOINT ['/bin/bash']
#ENTRYPOINT ["tail", "-f", "/dev/null"]
