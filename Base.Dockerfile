FROM ubuntu:22.04

################## METADATA ######################
LABEL maintainer="Christian Domínguez-Dalmases <christian.dominguez@bsc.es>, Albert Cañellas-Sole <albert.canellas@bsc.es>, Roc Farriol-Duran <roc.farriol@bsc.es>" \
    container="PredIG-Base Dependencies Image" \
    about.summary="Base Image with R and micromamba dependencies" \
    about.home="https://github.com/BSC-CNS-EAPM/predig" \
    software.version="1.0"

################## INSTALLATION ######################
ENV TZ=Europe/Madrid
ARG DEBIAN_FRONTEND=noninteractive

# Update to latest packages and install python=3.7
RUN apt update && apt upgrade -y && \
    apt install software-properties-common -y && \
    add-apt-repository ppa:deadsnakes/ppa -y && \
    apt update && \
    apt install -y \
    python3.7 \
    python3-pip \
    git \
    python-is-python3 \
    vim \
    wget \
    libblas-dev \
    liblapack-dev \
    gfortran \
    curl \
    libcurl4-openssl-dev \
    libxml2-dev \
    zip \
    bzip2

# Install micromamba
RUN curl -Ls http://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xvj bin/micromamba

# Install R 4.2.1
RUN apt install --no-install-recommends r-base -y

# Install R libraries
RUN R -e "install.packages('dplyr', dependencies=TRUE)" && \
    R -e "install.packages('Peptides', dependencies=TRUE)" && \
    R -e "install.packages('seqinr')" && \
    R -e "install.packages('stringr', dependencies=TRUE)" && \
    R -e "install.packages('argparser')" && \
    R -e "install.packages('xgboost', dependencies=TRUE)"

# Initialize micromamba shell
RUN micromamba shell init --shell bash --root-prefix=~/.local/share/mamba
ENV MAMBA_ROOT_PREFIX=~/.local/share/mamba
RUN echo "export MAMBA_ROOT_PREFIX=~/.local/share/mamba" >> ~/.bashrc