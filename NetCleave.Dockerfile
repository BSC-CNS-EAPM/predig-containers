FROM bsceapm/predig-base:latest
################## METADATA ######################
LABEL maintainer="Christian Domínguez-Dalmases <christian.dominguez@bsc.es>, Albert Cañellas-Sole <albert.canellas@bsc.es>, Roc Farriol-Duran <roc.farriol@bsc.es>" \
    container="PredIG-NetCleave Image" \
    about.summary="NetCleave-PrediG" \
    about.home="https://github.com/BSC-CNS-EAPM/predig" \
    software.version="1.0"

# Copy the environment file
COPY predig_env.yml /tmp/predig_env.yml

# Install the environment
RUN micromamba create -n predig_env -f /tmp/predig_env.yml -y

# Set up environment activation in system-wide profile
RUN echo "source /opt/conda/envs/predig_env/bin/activate" >> /etc/bash.bashrc

# Copy the immuno container
COPY Immuno/NetCleave /Immuno

# Working directory
WORKDIR /predig

# Create a symlink from /uniprot to /Immuno/NetCleave/data/databases/uniprot
RUN mkdir -p /Immuno/NetCleave/data/databases/uniprot
RUN ln -s /Immuno/NetCleave/data/databases/uniprot /uniprot

ENTRYPOINT ["micromamba", "run", "-n", "predig_env", "python", "/Immuno/NetCleave.py"]