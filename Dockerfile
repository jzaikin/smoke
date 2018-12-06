# This Dockerfile is for a container that runs the tests for: front-end, back-end, smokr
FROM lsmith202/smoke-base
RUN pip install tox wheel codecov
RUN apt-get update && apt-get install -y yarn

## COPIED from: https://gist.github.com/remarkablemark/aacf14c29b3f01d6900d13137b21db3a
# replace shell with bash so we can source files
RUN rm /bin/sh && ln -s /bin/bash /bin/sh

# update the repository sources list
# and install dependencies
RUN apt-get update \
    && apt-get install -y curl \
    && apt-get -y autoclean

# nvm environment variables
ENV NVM_DIR /usr/local/nvm
ENV NODE_VERSION 4.4.7

# install nvm
# https://github.com/creationix/nvm#install-script
RUN curl --silent -o- https://raw.githubusercontent.com/creationix/nvm/v0.31.2/install.sh | bash

# install node and npm
RUN source $NVM_DIR/nvm.sh \
    && nvm install $NODE_VERSION \
    && nvm alias default $NODE_VERSION \
    && nvm use default

# add node and npm to path so the commands are available
ENV NODE_PATH $NVM_DIR/v$NODE_VERSION/lib/node_modules
ENV PATH $NVM_DIR/versions/node/v$NODE_VERSION/bin:$PATH
## END COPIED
=======
#download base Jenkins image
FROM jenkinsci/blueocean

#set user
USER root

#run update and install prerequisites
RUN apk update && apk add build-base alpine-sdk python2-dev python3-dev ruby python python3 py-pip yarn openjdk8 libffi-dev libffi 

#python install stuff
RUN pip install -U pip tox codecov setuptools ez_setup

#plugins install 
COPY plugins.txt /usr/share/jenkins/plugins.txt
RUN /usr/local/bin/install-plugins.sh < /usr/share/jenkins/plugins.txt

#tell docker which port to connect on
EXPOSE 8080

USER jenkins
