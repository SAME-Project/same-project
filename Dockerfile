FROM python:3.8

# Basic toolchain                                                                                                                                                                                                     
RUN apt-get update && apt-get install -y \                                                                                                                                                                            
        apt-utils \                                                                                                                                                                                                   
        build-essential \                                                                                                                                                                                             
        git \                                                                                                                                                                                                         
        wget \                                                                                                                                                                                                        
        unzip \                                                                                                                                                                                                       
        yasm \                                                                                                                                                                                                        
        pkg-config \                                                                                                                                                                                                  
        libcurl4-openssl-dev \                                                                                                                                                                                        
        zlib1g-dev \                                                                                                                                                                                                  
        htop \                                                                                                                                                                                                        
        cmake \                                                                                                                                                                                                       
        vim \                                                                                                                                                                                                         
        nano \                                                                                                                                                                                                        
        python3-pip \
        python3-dev \
        python3-tk \
        libx264-dev \
        gcc \
        # python-pytest \
    && cd /usr/local/bin \
    && pip3 install --upgrade pip \
    && apt-get autoremove -y

RUN git clone -b develop https://github.com/AlgoveraAI/same-project.git

WORKDIR /same-project

ARG DEBIAN_FRONTEND=noninteractive

RUN pip3 install .

RUN python3.8 -m pip install jupyter
RUN python3.8 -m pip install nbconvert
ENV KF_PIPELINES_ENDPOINT_ENV='ml_pipeline.kubeflow.svc.cluster.local:8888'

RUN chmod +x ./ocean.sh
