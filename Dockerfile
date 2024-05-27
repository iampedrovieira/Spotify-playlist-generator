FROM alpine:latest

#RUN apk update && apk add bash
RUN  apk update && apk add
RUN apk add --no-cache bash

WORKDIR /home/app

RUN cd /home/app

# git 
#RUN apk add git

#Node instalaion
#RUN apk add --update nodejs npm
#Python instalation

RUN apk add --no-cache python3 py3-pip

EXPOSE 5000
