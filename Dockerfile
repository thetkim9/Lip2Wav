FROM tensorflow/tensorflow:1.13.1-gpu
ENV LANG C.UTF-8
RUN apt-get update
#RUN apt-get -y install software-properties-common
#RUn apt-add-repository universe
RUN add-apt-repository ppa:fkrull/deadsnakes
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update
RUN apt-get -y install python3.7-dev
#RUN python --version
RUN apt-get -y install build-essential
RUN apt-get -y install ffmpeg
#RUN pip3 install -r requirements.txt
RUN apt-get -y install wget
RUN apt -y install python3-pip
RUN python3.7 -m pip install --upgrade setuptools
RUN python3.7 -m pip install pip
RUN python3.7 -m pip install numpy==1.16.4
RUN python3.7 -m pip install Cython
RUN python3.7 -m pip install pkgconfig
RUN apt-get -y install curl
#RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
#RUN yes yes | bash Miniconda3-latest-Linux-x86_64.sh
#RUN mv yes/condabin/conda /usr/bin/
#RUN conda install -c anaconda numpy
#RUN conda install -c anaconda Cython
#RUN conda install -c anaconda pkgconfig
#RUN conda install -c anaconda flask
#RUN conda install -c anaconda "Pillow<7"
#RUN conda install -c anaconda requests
#RUN conda install -c anaconda pip
#RUN apt-get -y install build-essential
#RUN conda config --add channels conda-forge
#RUN conda install -c conda-forge gcc
#RUN /yes/bin/pip install lws 
#RUN /yes/bin/pip install pesq 
#RUN /yes/bin/pip install webrtcvad
COPY requirements.txt .
RUN python3.7 -m pip install -r requirements.txt
RUN apt update && apt install -y libsm6 libxext6
RUN apt-get install -y libxrender-dev
RUN wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1M_F3vLk1rWnRNPDE3dVYnz9RWlXL1ty4' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1M_F3vLk1rWnRNPDE3dVYnz9RWlXL1ty4" -O tacotron_model.ckpt-313000 && rm -rf /tmp/cookies.txt
RUN python3.7 -m pip install torch==1.5.0 torchvision==0.6.0 -f https://download.pytorch.org/whl/torch_stable.html
RUN rm /var/lib/apt/lists/lock && rm /var/cache/apt/archives/lock && rm /var/lib/dpkg/lock*
RUN python3.7 -m pip install Unidecode
RUN apt-get -y install vim
RUN apt -y install git-all
COPY . .
EXPOSE 80
#CMD python3 server.py
