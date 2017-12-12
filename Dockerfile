FROM python:3-alpine
MAINTAINER Charlie Gildawie <charles.gildawie@gmail.com>

LABEL org.label-schema.name="dembones" \
      org.label-schema.description="HTTP(s) web server that does bad things" \
      org.label-schema.vcs-url="https://github.com/TransactCharlie/badserver" \
      org.label-schema.usage="README.md" \
      org.label-schema.vcs-ref="${VCS_REF}" \
      org.label-schema.vendor="TransactCharlie" \
      org.label-schema.schema-version="1.0" \
      org.label-schema.version="${BUILD_NUMBER}"

COPY badserver.py badserver.py
COPY certs certs
COPY requirements.txt requirements.txt

RUN apk add --update py-pip alpine-sdk \
 && pip3 install -r requirements.txt \
 && apk del py-pip alpine-sdk

ENTRYPOINT ["python", "badserver.py"]
