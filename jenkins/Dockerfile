FROM jenkins/jenkins:lts

USER root

# prerequisites for docker
RUN apt-get update \
    && apt-get install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        software-properties-common \
        vim \
        iputils-ping \
        unzip \
        wget \
        gnupg \
        netcat \
        zip \
        python3 \
        python3-pip\
        jq

# docker repos
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add - \
    && echo "deb [arch=amd64] https://download.docker.com/linux/ubuntu xenial stable" >> /etc/apt/sources.list.d/additional-repositories.list \
    && echo "deb http://ftp-stud.hs-esslingen.de/ubuntu xenial main restricted universe multiverse" >> /etc/apt/sources.list.d/official-package-repositories.list \
    && apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 437D05B5 \
    && apt-get update

# docker
RUN apt-get install -y docker-ce

# docker-compose
RUN curl -L https://github.com/docker/compose/releases/download/1.25.0/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose \
    && chmod +x /usr/local/bin/docker-compose

#replace docker group
RUN delgroup docker && addgroup -gid 1001 docker

# give jenkins docker rights
RUN usermod -aG docker jenkins

RUN chown -R 1000:1000 /var/jenkins_home

USER jenkins