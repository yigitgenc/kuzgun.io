# kuzgun.io

Dockerized online streaming software.

[![Build Status](https://travis-ci.org/yigitgenc/kuzgun.io.svg?branch=travis)](https://travis-ci.org/yigitgenc/kuzgun.io)

# Installation

__kuzgun.io__ is designed to be run on your server effortlessly.
Only thing you have to do install [Docker](https://www.docker.com/what-docker) on 
your server to build and run kuzgun.io.

## Contents:

* [Running on __Ubuntu 16.04__](#running-on-ubuntu-1604)
    * [Pre-requisites](#pre-requisites)
    * [Setup](#setup)
* [Running on __your computer__](#running-on-your-computer)
    * [Installing](#installing)
    * [Running](#running)
    * [Debugging](#debugging)
    * [Tests](#tests)

### Running on Ubuntu 16.04

#### Pre-requisites

* Ubuntu 16.04
* Docker
* At least 1GB memory. (swap can be used)
* At least 5GB disk space. (make sure you have enough space to download things)

#### Setup

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

Go build and run the following commands respectively:
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

### Running on your computer

#### Installing

Get Docker first:
* <a href="https://download.docker.com/mac/stable/Docker.dmg" target="_blank">Docker CE for Mac</a>
* <a href="https://download.docker.com/win/stable/Docker%20for%20Windows%20Installer.exe" target="_blank">Docker CE for Windows</a>
* <a href="https://docs.docker.com/engine/installation/linux/docker-ce/centos/" target="_blank">Docker CE for CentOS</a>
* <a href="https://docs.docker.com/engine/installation/linux/docker-ce/debian/" target="_blank">Docker CE for Debian</a>
* <a href="https://docs.docker.com/engine/installation/linux/docker-ce/fedora/" target="_blank">Docker CE for Fedora</a>
* <a href="https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/" target="_blank">Docker CE for Ubuntu</a>

And clone the repo by using `git`:
```
$ git clone git@github.com:yigitgenc/kuzgun.io.git
$ cd kuzgun.io/
$ git lfs pull  # This is required to run tests.
```

#### Running

To build and run `kuzgun.io`, go to project's root directory and run the following commands respectively:
```
$ sudo docker-compose build
$ sudo docker-compose up -d
$ sudo docker-compose run --rm app python manage.py migrate
$ sudo docker-compose run --rm app python manage.py collectstatic --noinput
```

#### Debugging

```
$ docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

#### Tests
```
$ docker-compose -f docker-compose.yml -f docker-compose.dev.yml run --rm --user='app' app coverage run manage.py test --verbosity=2
```
> If you are running tests as a root user in your host; specify `--user='root'` argument to the `docker-compose run` command.

> Coverage report will be generated in `htmlcov` directory.
