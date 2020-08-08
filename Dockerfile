FROM python:3.7-slim

ENV VIPSVERSION 8.9.2

# build libvips from source
RUN apt update -y && apt install -y wget build-essential pkg-config libglib2.0-dev libexpat1-dev libtiff5-dev libjpeg62-turbo-dev libgsf-1-dev openslide-tools libpng-dev
RUN wget https://github.com/libvips/libvips/releases/download/v${VIPSVERSION}/vips-${VIPSVERSION}.tar.gz && tar xvfz vips-${VIPSVERSION}.tar.gz 
RUN cd vips-${VIPSVERSION} && ./configure && make && make install && ldconfig

# library for opencv
RUN apt install -y libsm6

# pip packages for wsiprocess
ADD ./ $HOME
RUN pip install -r requirements.txt
RUN pip install -e .
