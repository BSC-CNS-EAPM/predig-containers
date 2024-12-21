FROM bsceapm/predig-base:latest

################## METADATA ######################
LABEL maintainer="Christian Domínguez-Dalmases <christian.dominguez@bsc.es>, Albert Cañellas-Sole <albert.canellas@bsc.es>, Roc Farriol-Duran <roc.farriol@bsc.es>" \
    container="PredIG-Final Image" \
    about.summary="Final Image with PredIG setup" \
    about.home="https://github.com/BSC-CNS-EAPM/predig" \
    software.version="1.0"

# Copy the environment file
COPY predig_env.yml /tmp/predig_env.yml

# Install the environment
RUN micromamba create -n predig_env -f /tmp/predig_env.yml -y

# Set up environment activation
RUN echo "source ~/.local/share/mamba/envs/predig_env/bin/activate" >> ~/.bashrc

# Download mhcflurry models
RUN micromamba run -n predig_env mhcflurry-downloads fetch models_class1_presentation

# Copy the immuno container
COPY Immuno /Immuno

# Give full permission to /Immuno/netctlpan/tapmat_pred_fsa
RUN chmod 777 /Immuno/netctlpan/tapmat_pred_fsa

# Working directory
WORKDIR /predig

# Create a symlink from /uniprot to /Immuno/NetCleave/data/databases/uniprot
RUN mkdir -p /Immuno/NetCleave/data/databases/uniprot
RUN ln -s /Immuno/NetCleave/data/databases/uniprot /uniprot

ENTRYPOINT ["micromamba", "run", "-n", "predig_env", "python", "/Immuno/run_predig/run.py"]