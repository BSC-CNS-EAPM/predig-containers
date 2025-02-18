# PredIG Container Documentation

## Overview

PredIG (https://github.com/BSC-CNS-EAPM/PredIG) is a predictor of T-cell epitope immunogenicity that supports pan-HLA-I predictions and various input formats for epitope assessment: Peptides+UniProtID(CSV), Peptides+ProteinSeq(CSV) and Full Protein Sequence (FASTA).

## Abstract

Cytotoxic T cells are key effectors in the immune response against pathogens and cancer. Hence, their activation, driven by the recognition of immunogenic epitopes, is a fundamental goal for immunotherapies such as checkpoint inhibitors, TILs or vaccines. The epitope landscape in cancer and infection, however, is too large to test due to the immense number of candidates versus the high cost and low throughput of experimental techniques. Immunoinformatic models can prioritize the candidates with greater potential with orders of magnitude higher throughput than experimental approaches, but their success rate has remained incremental and their explainability limited. Here we present PredIG, a predictor of T-cell epitope immunogenicity that integrates antigenic and physicochemical properties of 17448 peptide-HLA complexes using XGBoost, a decision-tree-based algorithm. PredIG outperforms state-of-the-art methods in two pathogen and non-canonical cancer antigen held-out sets. In cancer neoantigens, PredIG increases the success rate of binding affinity predictions and identifies alternative immunogenic epitopes. Furthermore, since PredIG uses an explainable architecture, its interpretability scheme pinpoints the importance of antigenic and physicochemical epitope properties and their differences in each antigen type. Overall, PredIG increases the immunogenicity success rates in vaccine design for cancer and infection and displays an unprecedented interpretability to build community trust. In addition, PredIG is accessible through containerized environments and a user-friendly webserver at https://horus.bsc.es/predig

## Prerequisites

1. Docker/Singularity installed on your system
2. UniProt database file (uniprot_sprot.fasta)
3. The PredIG Docker image:

```bash
docker pull bsceapm/predig:latest
```

For macOS running on Apple Silicon the image has to be requested using the `linux/amd64` platform tag:
```bash
docker pull bsceapm/predig:latest --platform linux/amd64
```

## UniProt Database Setup

1. [Download](https://ftp.ebi.ac.uk/pub/databases/uniprot/knowledgebase/uniprot_sprot.fasta.gz) the UniProt database file (uniprot_sprot.fasta)
2. Place it in a directory that will be mounted to the container
3. This directory must be bound to `/uniprot` when running the container

## Basic Usage with Docker

The container requires two volume bindings to make your files available to the program inside the docker environment.
This can be accomplished with the `-v` flag:

- Your working directory to `/predig` (for input/output files): `-v /path/to/work/dir:/predig`
- UniProt database directory to `/uniprot`: `-v /path/to/uniprot/dir:/uniprot`

> **_NOTE:_** The binding to the working directory might change with every experiment. Binding to uniprot has to remain the same unless a new version of the uniprot.fasta file has been provided.

Basic command structure:

```bash
docker run -v /path/to/work/dir:/predig -v /path/to/uniprot/dir:/uniprot bsceapm/predig <input_file> --output <output_file> [options]
```

## PREDIG Models

PredIG provides three different models optimized for target epitope types.
neoant > opt for cancer neoantigens.
noncan > opt for non-canonical cancer antigens.
path > opt for epitopes derived from infectious pathogens.

Specify setting the flag --model:

```bash
docker run -v /path/to/work/dir:/predig -v /path/to/uniprot/dir:/uniprot bsceapm/predig <input_file> --output <output_file> --model neoant [options]
```

## Input Modes

### 1. UniProt Mode (Default)

Predict using a list of epitopes (peptide sequences), HLA-I alleles in 4 digits resolution (ie HLA-A\*01:01) and associated UniProt ID for their parental protein. The CSV file must contain the following columns: epitope, HLA_allele, uniprot_id

Example:

```bash
docker run -v ./my_data:/predig -v ./uniprot:/uniprot bsceapm/predig input_uniprot.csv --output results.csv
```

### 2. Recombinant Mode

Predict using a list of epitopes (peptide sequences), HLA-I alleles in 4 digits resolution (ie HLA-A\*01:01) and the amino acid sequence for their parental protein. Useful in case the target protein is mutant, recombinant or not indexed at UniProt. The CSV file must contain the columns: epitope, HLA_allele, protein_seq, protein_name

Example:

```bash
docker run -v ./my_data:/predig -v ./uniprot:/uniprot bsceapm/predig input_sequences.csv --output results.csv --type recombinant
```

### 3. FASTA Mode

Predict all the epitopes of a target protein using FASTA input file. Specify the target HLA-I alleles using an additional CSV file listing alleles in 4-digits resolution. Epitopes of X to X sequence length will be generated. Set using the flag --precursor-length and XXX.

Example:

```bash
docker run -v ./my_data:/predig -v ./uniprot:/uniprot bsceapm/predig sequences.fasta --output results.csv --type fasta --alleles alleles.csv
```

## Command Arguments

Required:

- Input file: Path to the input file (relative to mounted directory)
- `--output`: Name of the output file

Optional:

- `--type`: Input file type (uniprot, fasta, or recombinant)
- `--model`: Prediction model (noncan, neoant, or path)
- `--alleles`: Path to HLA alleles file (required for FASTA mode)
- `--alpha`: Alpha parameter value for TapMap
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
singularity run --bind /path/to/work/dir:/predig,/path/to/uniprot/dir:/uniprot /path/to/predig.sif <input_file> --output <output_file> [options]
```

### Singularity Examples

1. UniProt Mode:

```bash
singularity run --bind ./:/predig,./my_uniprot_folder:/uniprot /path/to/predig.sif input_uniprot.csv --output results.csv
```

2. Recombinant Mode:

```bash
singularity run --bind ./:/predig,./my_uniprot_folder:/uniprot /path/to/predig.sif input_sequences.csv --output results.csv --type recombinant
```

3. FASTA Mode:

```bash
singularity run --bind ./:/predig,./my_uniprot_folder:/uniprot /path/to/predig.sif sequences.fasta --output results.csv --type fasta --alleles alleles.csv
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
