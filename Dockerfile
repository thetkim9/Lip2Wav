FROM tensorflow/tensorflow:1.13.1-gpu
ENV LANG C.UTF-8
RUN apt-get update
RUN add-apt-repository ppa:fkrull/deadsnakes
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update
RUN apt-get -y install python3.7-dev
RUN apt-get -y install build-essential
RUN apt-get -y install ffmpeg
RUN apt-get -y install wget
RUN apt -y install python3-pip
RUN python3.7 -m pip install --upgrade setuptools
RUN python3.7 -m pip install pip
RUN python3.7 -m pip install numpy==1.16.4
RUN python3.7 -m pip install Cython
RUN python3.7 -m pip install pkgconfig
RUN apt-get -y install curl
COPY requirements.txt .
RUN python3.7 -m pip install -r requirements.txt
RUN apt update && apt install -y libsm6 libxext6
RUN apt-get install -y libxrender-dev
RUN wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm
=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate
 'https://docs.google.com/uc?export=download&id=1CeF7CbamFZc--kOoIZd-9ZMB6JQDyxDf'
 -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1CeF7CbamFZc--kOoIZd-9ZMB6JQDyxDf"
 -O tacotron_model.ckpt-313000.data-00000-of-00001 && rm -rf /tmp/cookies.txt
RUN wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm
=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate
 'https://docs.google.com/uc?export=download&id=1DD9JpiqyafaoBgIWoQFOx5uWSn6ZgvB2'
 -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1DD9JpiqyafaoBgIWoQFOx5uWSn6ZgvB2"
  -O tacotron_model.ckpt-313000.index && rm -rf /tmp/cookies.txt
RUN wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm
=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate
 'https://docs.google.com/uc?export=download&id=1sN2nm8gXfNbO4NgNmmRZl3JDtdYGPUEP'
  -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1sN2nm8gXfNbO4NgNmmRZl3JDtdYGPUEP"
   -O tacotron_model.ckpt-313000.meta && rm -rf /tmp/cookies.txt
RUN python3.7 -m pip install torch==1.5.0 torchvision==0.6.0 -f https://download.pytorch.org/whl/torch_stable.html
RUN rm /var/lib/apt/lists/lock && rm /var/cache/apt/archives/lock && rm /var/lib/dpkg/lock*
RUN python3.7 -m pip install Unidecode
RUN apt-get -y install vim
RUN apt -y install git-all
COPY . .
EXPOSE 80
#CMD python3 server.py
