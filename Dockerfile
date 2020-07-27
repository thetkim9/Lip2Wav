FROM ubuntu:latest
ENV LANG C.UTF-8
RUN apt-get update
RUN apt-get install python3.7.4
RUN apt-get install ffmpeg
RUN apt -y install python-pip
RUN pip install -r requirements.txt
#RUN pip install Flask-Limiter
#RUN pip install Pillow
#RUN pip install requests
COPY . .
EXPOSE 80
#CMD python server.py

