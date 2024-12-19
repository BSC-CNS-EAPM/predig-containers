################## BASE IMAGE ######################

FROM ubuntu:22.04

################## METADATA ######################

LABEL maintainer="Christian Domínguez-Dalmases <christian.dominguez@bsc.es>, Albert Cañellas-Sole <albert.canellas@bsc.es>, Roc Farriol-Duran <roc.farriol@bsc.es>" \
    container="PredIG-Base Image" \
    about.summary="Base Image with default dependencies" \
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

# Copy the environment file
COPY predig_env.yml /tmp/predig_env.yml

# Install the environment
RUN micromamba create -n predig_env -f /tmp/predig_env.yml  -y

# Install R 4.2.1
RUN apt install --no-install-recommends r-base -y

# R libraries
RUN R -e "install.packages('dplyr', dependencies=TRUE)" # NICE
# RUN R -e "install.packages('tidyr', dependencies=TRUE)"
RUN R -e "install.packages('Peptides', dependencies=TRUE)" # NICE
# repos='http://R-Forge.R-project.org'
RUN R -e "install.packages('seqinr')" # NICE
RUN R -e "install.packages('stringr', dependencies=TRUE)" # NICE
# RUN R -e "install.packages('caret', dependencies=TRUE)"
RUN R -e "install.packages('argparser')" # NICE
RUN R -e "install.packages('xgboost', dependencies=TRUE)" # NICE
# RUN R -e "install.packages('glmnet', dependencies=TRUE)"

# Load libraries
RUN R -e "library(dplyr)"
# RUN R -e "library(tidyr)"
RUN R -e "library(Peptides)"
RUN R -e "library(seqinr)"
RUN R -e "library(stringr)"
# RUN R -e "library(caret)"
RUN R -e "library(argparser)"
RUN R -e "library(xgboost)"
# RUN R -e "library(glmnet)"

# Initialize micromamba shell and set up environment activation
RUN micromamba shell init --shell bash --root-prefix=~/.local/share/mamba
ENV MAMBA_ROOT_PREFIX=~/.local/share/mamba
RUN echo "export MAMBA_ROOT_PREFIX=~/.local/share/mamba" >> ~/.bashrc
RUN echo "source ~/.local/share/mamba/envs/predig_env/bin/activate" >> ~/.bashrc

# Download mhcflurry models
RUN micromamba run -n predig_env mhcflurry-downloads fetch models_class1_presentation

# Copy the immuno container
COPY Immuno /Immuno

# Give full permission to /Immuno/netctlpan/tapmat_pred_fsa
RUN chmod 777 /Immuno/netctlpan/tapmat_pred_fsa

# Working directory
WORKDIR /predig

ENTRYPOINT ["micromamba", "run", "-n", "predig_env", "python", "/Immuno/run_predig/run.py"]