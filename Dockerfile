FROM python:3.7-alpine

RUN apk add bash curl
RUN pip3 install requests