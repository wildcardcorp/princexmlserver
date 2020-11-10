FROM ubuntu:16.04

# upgrade ubuntu packages
ENV DEBIAN_FRONTEND="noninteractive"
RUN apt-get update
RUN apt-get install apt-utils -y
RUN apt-get upgrade -y

RUN apt-get install xfonts-utils \
    cabextract python3 python3-pip apt-utils wget libcurl3-gnutls \
    libfontconfig1 libxml2 libtiff5 \
    libart-2.0-2 libjpeg62 libgif7 gsfonts -y
RUN apt-get install libcurl3 -y

RUN wget -O ttf.deb http://ftp.us.debian.org/debian/pool/contrib/m/msttcorefonts/ttf-mscorefonts-installer_3.7_all.deb
RUN dpkg -i ttf.deb

RUN wget -O prince.tar.gz http://www.princexml.com/download/prince-9.0r5-ubuntu1604-amd64.tar.gz
RUN tar -zxvf prince.tar.gz
RUN sh prince*/install.sh

WORKDIR /usr/src/app

COPY . .

RUN pip3 install -e .

EXPOSE 6543
CMD ["pserve", "/usr/src/app/production.ini"]
