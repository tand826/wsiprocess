FROM ubuntu:16.04

RUN apt update
RUN apt install libvips
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3 get-pip.py
RUN pip install -r requirements.txt
RUN pip install wsiprocess