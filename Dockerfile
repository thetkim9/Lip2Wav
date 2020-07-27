FROM ubuntu:latest
ENV LANG C.UTF-8
RUN apt-get update
RUN apt-get install python3.7.4
RUN apt-get install ffmpeg
RUN apt -y install python-pip
RUN pip install -r requirements.txt
#RUN pip3 install Flask-Limiter
#RUN pip3 install Pillow
#RUN pip3 install requests
COPY . .
EXPOSE 80
#CMD python3 server.py
