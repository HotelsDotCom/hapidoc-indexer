############################################################
# Dockerfile to build HApiDocIndexer Container
# Based on Ubuntu 18.04
############################################################

# Set the base image to Ubuntu
FROM ubuntu:18.04

##### Install libraries/dependencies
# Install rsyslog to enable cron logs
RUN apt-get update && \
    apt-get -y install rsyslog
RUN apt-get update && \
    apt-get install -y \
        git \
        openssh-server

# Install openssl and configure git to avoid https issues
RUN apt-get install openssl
RUN git config --global http.sslVerify false

# Install Java 8
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y  software-properties-common && \
    add-apt-repository ppa:webupd8team/java -y && \
    apt-get update && \
    echo oracle-java7-installer shared/accepted-oracle-license-v1-1 select true | /usr/bin/debconf-set-selections && \
    apt-get install -y oracle-java8-installer && \
    apt-get clean

# Install anaconda2
RUN wget https://repo.continuum.io/archive/Anaconda2-4.4.0-Linux-x86_64.sh
RUN bash Anaconda2-4.4.0-Linux-x86_64.sh -b -p ~/anaconda
RUN rm Anaconda2-4.4.0-Linux-x86_64.sh

# Configure anaconda
RUN echo 'alias python=/root/anaconda/bin/python' >> ~/.bashrc
RUN ["/bin/bash", "-c", "source ~/.bashrc"]
RUN echo 'export PATH=~/anaconda/bin:$PATH' >> ~/.bashrc
RUN ["/bin/bash", "-c", "source ~/.bashrc"]
env PATH ~/anaconda/bin:$PATH
RUN echo $PATH
RUN ["/bin/bash", "-c", "conda update --yes conda"]
RUN ["/bin/bash", "-c", "conda config --add channels conda-forge"]

# Install project dependencies using conda
ADD ./requirements.txt ./requirements.txt
RUN ["/bin/bash", "-c", "conda install --yes --file requirements.txt"]

# Install stashy dependency using pip
RUN ["/bin/bash", "-c", "pip install stashy"]

##### Install CLAMS required libraries
# Install astyle
RUN apt-get install astyle

### Install srcML (depends on libarchive and libcurl4)
# Install libarchive and libcurl4
RUN apt-get update && \
    apt-get install -y \
        libarchive-dev \
        libcurl4-openssl-dev

# Install/configure srcml
RUN wget http://131.123.42.38/lmcrs/beta/srcML-Ubuntu18.04.deb
RUN dpkg -i srcML-Ubuntu18.04.deb

# Create dir for project
RUN rm -rf hapidocindexer
RUN mkdir hapidocindexer

# Set project directory
ENV DIRPATH /hapidocindexer

# Create logs directory
RUN mkdir $DIRPATH/logs
RUN chmod +x $DIRPATH/logs

# Set the default directory where CMD, RUN, and ENTRYPOINT commands will execute
WORKDIR $DIRPATH

# Copy dirs from local
ADD hapidocdownloader ./hapidocdownloader
ADD hapidoccore ./hapidoccore
ADD hapidocdb ./hapidocdb

# Clone CLAMS
RUN git clone -b make-clams-extendable https://github.com/mast-group/clams.git --depth 1
RUN mv clams/src hapidoccore/src
RUN mv clams/libs hapidoccore/libs

# Configure CLAMS dependencies
RUN mkdir hapidoccore/libs/astyle
RUN ln -s /usr/bin/astyle ./hapidoccore/libs/astyle/astyle
RUN mkdir hapidoccore/libs/srcml
RUN ln -s /usr/bin/srcml ./hapidoccore/libs/srcml/srcml

# Add projects mappings
ADD mappings.py ./mappings.py

# Add cron scripts
ADD run.sh ./run.sh
RUN chmod +x ./run.sh
ADD crontab ./crontab
RUN chmod +x ./crontab

CMD printenv | grep -v "no_proxy" >> /etc/environment && touch /hapidocindexer/logs/hapidocindexer.log && cron && less +F /hapidocindexer/logs/hapidocindexer.log

CMD /bin/bash ./run.sh
# Uncomment if you want to set up a cron job for the indexer
#RUN crontab ./crontab
