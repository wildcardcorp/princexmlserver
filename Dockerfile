FROM python:3.9-bullseye

WORKDIR /usr/src/app/

COPY . .

RUN pip3 install -U setuptools pip wheel \
    && python setup.py bdist_wheel


FROM python:3.9-bullseye

# upgrade ubuntu packages
ENV DEBIAN_FRONTEND="noninteractive"
RUN apt-get update \
    && apt-get install apt-utils -y \
    && apt-get upgrade -y \
    && apt-get install -y xfonts-utils \
        cabextract curl wget \
        libfontconfig1 libxml2 libtiff5 \
        libart-2.0-2 libjpeg62 libgif7 \
        liblcms2-2 libwebpdemux2 \
        gsfonts libcurl4 \
        git build-essential libssl-dev zlib1g-dev libbz2-dev \
        libreadline-dev libsqlite3-dev llvm libncurses5-dev libncursesw5-dev \
        xz-utils tk-dev libffi-dev liblzma-dev

## install mscorefonts
RUN curl -o ttf.deb http://ftp.us.debian.org/debian/pool/contrib/m/msttcorefonts/ttf-mscorefonts-installer_3.8.1_all.deb
RUN dpkg -i ttf.deb

# install princexml
RUN curl -o prince.deb https://www.princexml.com/download/prince_15-1_debian11_amd64.deb
RUN dpkg -i prince.deb

WORKDIR /usr/src/app

# upgrade pip
RUN pip3 install --upgrade setuptools pip wheel

# install app
COPY --from=0 /usr/src/app/dist/*.whl /usr/src/
COPY docker.ini .
COPY requirements.txt .
RUN pip3 install -r requirements.txt
RUN pip3 install /usr/src/*.whl


EXPOSE 6543
CMD ["pserve", "/usr/src/app/docker.ini", "use_redis=false", "redis_host=localhost", "log_level=INFO"]
