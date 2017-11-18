FROM alpine:3.6

RUN apk update && apk upgrade && apk add --update sudo python3 python3-dev postgresql-dev ffmpeg build-base gettext
RUN ln -s /usr/bin/python3 /usr/bin/python && ln -s /usr/bin/pip3 /usr/bin/pip
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN mkdir /app && mkdir /data && mkdir /static && mkdir /uploads
RUN addgroup -g 1337 -S app && adduser -u 1337 -h /app -D -S app -G app
RUN echo "app ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers

ADD ./src /app
ADD ./data /data

RUN chown -R app:app /app && chown -R app:app /data && chown -R app:app /static && chown -R app:app /uploads

WORKDIR /app

ENV PYTHONBUFFERED 1

USER app

RUN sudo -H pip install -r requirements.txt
