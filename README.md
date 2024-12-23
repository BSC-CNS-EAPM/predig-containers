# PredIG Docker and Singularity Documentation

## Overview

PredIG is a tool for protein immunogenicity prediction that can predict from various input formats including UniProt IDs and FASTA sequences.

## Prerequisites

1. Docker/Singularity installed on your system
2. UniProt database file (uniprot_sprot.fasta)
3. The PredIG Docker image:

```bash
docker pull bsceapm/predig:latest
```

## UniProt Database Setup

1. Download the UniProt database file (uniprot_sprot.fasta) [Download here](https://ftp.ebi.ac.uk/pub/databases/uniprot/knowledgebase/uniprot_sprot.fasta.gz -O uniprot_sprot.fasta.gz)
2. Place it in a directory that will be mounted to the container
3. This directory must be bound to `/uniprot` when running the container

## Basic Usage with Docker

The container requires two volume bindings:

- Your working directory to `/predig` (for input/output files)
- UniProt database directory to `/uniprot`

Basic command structure:

```bash
docker run -v /path/to/work/dir:/predig -v /path/to/uniprot/dir:/uniprot bsceapm/predig <input_file> --output <output_file> [options]
```

## Input Modes

### 1. UniProt Mode (Default)

Predict using UniProt.
Example:

```bash
docker run -v ./my_data:/predig -v ./uniprot:/uniprot \
 bsceapm/predig input_proteins.csv --output results.csv
```

### 2. Recombinant Mode

Precit using recombinant sequences.
Example:

```bash
docker run -v ./my_data:/predig -v ./uniprot:/uniprot \
 bsceapm/predig input_sequences.csv --output results.csv --type recombinant
```

### 3. FASTA Mode

Predict from FASTA input files. Requires an additional HLA alleles file.
Example:

```bash
docker run -v ./my_data:/predig -v ./uniprot:/uniprot \
 bsceapm/predig sequences.fasta --output results.csv --type fasta --alleles alleles.csv
```

## Command Arguments

Required:

- Input file: Path to the input file (relative to mounted directory)
- `--output`: Name of the output file

Optional:

- `--type`: Input file type (uniprot, fasta, or recombinant)
- `--model`: Prediction model (noncan, neoant, or path)
- `--alleles`: Path to HLA alleles file (required for FASTA mode)
- `--alpha`: Alpha parameter value
- `--precursor-length`: Length of precursor sequence

## Running with Singularity

Singularity can run Docker containers directly, making it easy to use PredIG in HPC environments where Docker might not be available.

### Converting Docker Image to Singularity

1. Pull the Docker image and convert it to Singularity format:

```bash
singularity pull predig.sif docker://bsceapm/predig:latest
```

### Basic Usage with Singularity

The command structure is similar to Docker, but uses Singularity bind syntax:

```bash
singularity run --bind /path/to/work/dir:/predig,/path/to/uniprot/dir:/uniprot \
    predig.sif <input_file> --output <output_file> [options]
```

### Singularity Examples

1. UniProt Mode:

```bash
singularity run --bind ./my_data:/predig,./uniprot:/uniprot \
    predig.sif input_proteins.csv --output results.csv
```

2. Recombinant Mode:

```bash
singularity run --bind ./my_data:/predig,./uniprot:/uniprot \
    predig.sif input_sequences.csv --output results.csv --type recombinant
```

3. FASTA Mode:

```bash
singularity run --bind ./my_data:/predig,./uniprot:/uniprot \
    predig.sif sequences.fasta --output results.csv --type fasta --alleles alleles.csv
```

### Singularity Notes

- Multiple bind paths are separated by commas in Singularity
- The `.sif` file can be placed anywhere and called from any directory
- All other functionality remains identical to the Docker version
- File permissions are inherited from your user account, unlike Docker

## Example File Formats

### UniProt Mode Input Example

CSV file with UniProt IDs:

```
UniProtID
P01889
P61769
```

### Recombinant Mode Input Example

CSV file with protein sequences:

```
Sequence
MALTLSFFVVLLLVG
MLPGLALLLLAAWTARA
```

### FASTA Mode Input Example

FASTA file (sequences.fasta):

```
>Protein1
MALTLSFFVVLLLVG
>Protein2
MLPGLALLLLAAWTARA
```

Alleles file (alleles.csv):

```
Allele
HLA-A*02:01
HLA-B*07:02
```

## Notes

- All input/output files must be in the directory mounted to `/predig`
- The UniProt database file must be in the directory mounted to `/uniprot`
- File paths in commands should be relative to the mounted directories
- Output files will be created in your mounted working directory
