FROM python:latest

# add user
RUN apt-get update && apt-get install -y sudo
ARG uid
ARG gid
ARG user
RUN groupadd --gid ${gid} ${user} && useradd -ms /bin/bash --uid ${uid} --gid ${gid} ${user}
RUN usermod -aG sudo ${user}

# ssh
RUN apt-get update && apt-get upgrade -y && apt-get install openssh-server -y
RUN mkdir /var/run/sshd
RUN sed -ri 's/^#?PermitRootLogin\s+.*/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -ri 's/UsePAM yes/#UsePAM yes/g' /etc/ssh/sshd_config

# poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/usr/local python3 -

# talib
COPY ./ta-lib-0.4.0-src.tar.gz /tmp/ta-lib-0.4.0-src.tar.gz
WORKDIR /tmp
RUN apt-get install -y build-essential
RUN tar -xvf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ &&\
    ./configure --prefix=/usr &&\
    make &&\
    make install
RUN pip install TA-Lib
