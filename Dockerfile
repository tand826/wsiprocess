FROM python:3.7-slim

RUN apt update -y
RUN apt install -y libvips

ADD ./ $HOME
RUN pip3 install -r requirements.txt
RUN pip3 install wsiprocess