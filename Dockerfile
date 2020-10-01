FROM python:3.8

RUN pip3 install scrapy

VOLUME [ "/data" ]

WORKDIR /app

COPY ikea.py /app/

ENV KNOWN_FILE=/data/known.pkl

ENTRYPOINT [ "scrapy", "runspider", "--loglevel", "ERROR", "ikea.py" ]