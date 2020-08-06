FROM python:3.7-slim

ENV VIPSVERSION 8.9.2

# build libvips from source

RUN apt update -y && apt install -y build-essential pkg-config libglib2.0-dev libexpat1-dev libtiff5-dev libjpeg-turbo8-dev libgsf-1-dev openslide-tools libpng-dev
RUN wget https://github.com/libvips/libvips/releases/download/v${VIPSVERSION}/vips-vips-${VIPSVERSION}.tar.gz && tar xvfz vips-${VIPSVERSION}.tar.gz 
RUN cd vips-${VIPSVERSION}
RUN ./configure && make && make install && ldconfig

ADD ./ $HOME
RUN pip3 install -r requirements.txt
RUN pip3 install -e .
