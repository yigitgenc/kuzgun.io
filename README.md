# kuzgun.io
![Coverage Status](https://cdn.rawgit.com/yigitgenc/kuzgun.io/master/data/coverage.svg)

Yours free dockerized online streaming software.

## Installation

__kuzgun.io__ is designed to run on your server effortlessly.
Only thing you have to do install [Docker](https://www.docker.com/what-docker) on 
your server to build and run kuzgun.io and you are ready to go!

### Contents:

* [Running on __Ubuntu 16.04__](#running-on-ubuntu-1604)

#### Running on Ubuntu 16.04
First, let's update and upgrade our packages. Also you have to install `software-properties-common`
```
$ sudo apt-get update
$ sudo apt-get upgrade
$ sudo apt-get install -y software-properties-common
```
Add the GPG key for the official Docker repository to the system:
```
$ curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
```
Add the Docker repository to APT sources:
```
$ sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
$ sudo apt-get update
```
Make sure you are about to install from the Docker repo instead of the default Ubuntu 16.04 repo:
```
$ apt-cache policy docker-ce
```
Now you're ready to install Docker.
```
$ sudo apt-get install -y docker-ce
```
Hang on, this is the final step for Docker installation. Download `docker-compose`. Phew!
You should specify the latest version of docker-compose.
```
$ export DOCKER_COMPOSE_VERSION=1.15.0
$ sudo curl -L https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
```
Apply executable permissions to the binary:
```
$ sudo chmod +x /usr/local/bin/docker-compose
```
Finally, now we are ready to download `kuzgun.io` on our server.
```
$ curl -L https://github.com/yigitgenc/kuzgun.io/archive/master.zip -o kuzgun.io.zip
$ unzip kuzgun.io.zip
```
> If you don't have `unzip`; install it by doing `$ sudo apt-get install -y unzip`.

Go to project's root by doing `cd kuzgun.io` and create your `.env` file:
```
$ echo "
# Make it hard to guess by someone else and keep it secret. You can generate 
# your secret key by using this link: https://www.miniwebtool.com/django-secret-key-generator/
SECRET_KEY=VerySecretKey
# Set your timezone. More information: 
# https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
TZ=Europe/Istanbul
" > .env
```
Go build and run `kuzgun.io`:
```
$ sudo docker-compose build
$ sudo docker-compose up -d
$ sudo docker-compose run --rm app python manage.py migrate
$ sudo docker-compose run --rm app python manage.py collectstatic --noinput
```
Create your superuser and get your credentials.
```
$ sudo docker-compose run --rm app python manage.py createsuperuser
$ Username: yourusername
$ Email address: yourname@email.com
$ Password: yourpassword
$ Password (again): yourpassword
```
You're all set! Go and login to the web app on the browser to start using `kuzgun.io` immediately: 
`http://your_server_ip` or `http://yourdomainname.com`
