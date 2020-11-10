FROM ubuntu:16.04

# upgrade ubuntu packages
ENV DEBIAN_FRONTEND="noninteractive"
RUN apt-get update
RUN apt-get install apt-utils -y
RUN apt-get upgrade -y

# install princexml dependencies
RUN apt-get install xfonts-utils \
    cabextract wget libcurl3-gnutls \
    libfontconfig1 libxml2 libtiff5 \
    libart-2.0-2 libjpeg62 libgif7 gsfonts -y
RUN apt-get install libcurl3 -y

# install mscorefonts
RUN wget -O ttf.deb http://ftp.us.debian.org/debian/pool/contrib/m/msttcorefonts/ttf-mscorefonts-installer_3.7_all.deb
RUN dpkg -i ttf.deb

# install princexml
RUN wget -O prince.tar.gz http://www.princexml.com/download/prince-9.0r5-ubuntu1604-amd64.tar.gz
RUN tar -zxvf prince.tar.gz
RUN sh prince*/install.sh

# install pyenv
RUN apt-get install git curl -y
RUN apt-get install -y build-essential libssl-dev zlib1g-dev libbz2-dev \
    libreadline-dev libsqlite3-dev llvm libncurses5-dev libncursesw5-dev \
    xz-utils tk-dev libffi-dev liblzma-dev python-openssl
RUN curl -L https://raw.githubusercontent.com/pyenv/pyenv-installer/dd3f7d0914c5b4a416ca71ffabdf2954f2021596/bin/pyenv-installer | bash
ENV PYENV_VIRTUALENV_INIT=1
ENV PYENV_SHELL=sh
ENV PATH=/root/.pyenv/plugins/pyenv-virtualenv/shims:/root/.pyenv/shims:/root/.pyenv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin


WORKDIR /usr/src/app

# install python version for app
COPY .python-version .
RUN pyenv install

# upgrade pip
RUN pip3 install --upgrade setuptools pip wheel

# install app requirements
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# install app
COPY princexmlserver/ ./princexmlserver
COPY setup.py .
COPY production.ini .
COPY README.md .
COPY CHANGES.txt .
COPY MANIFEST.in .
RUN pip3 install -e .


EXPOSE 6543
CMD ["pserve", "/usr/src/app/production.ini"]
