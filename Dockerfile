FROM alpine:3.6

RUN apk update && apk upgrade && apk add --update python3 python3-dev postgresql-dev ffmpeg build-base gettext
RUN ln -s /usr/bin/python3 /usr/bin/python && ln -s /usr/bin/pip3 /usr/bin/pip
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN mkdir /app

ADD ./src /app
WORKDIR /app

ENV PYTHONBUFFERED 1
ENV C_FORCE_ROOT 1

RUN pip install -r requirements.txt
