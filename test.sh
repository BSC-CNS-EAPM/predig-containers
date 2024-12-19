#!/bin/bash

# Exit on any error
set -e

# Function to compare files and exit if they differ
compare_files() {
    local expected=$1
    local actual=$2
    local test_name=$3
    
    echo "Verifying output for $test_name test..."
    if ! diff "$expected" "$actual"; then
        echo "❌ ERROR: $test_name test failed - files are different"
        exit 1
    fi
    echo "✅ $test_name test passed"
}

echo "Testing the docker image"

# Copy the test folder
echo "Copying the test folder"
cp -r tests tests_run

# Test the UNIPROT mode
echo "Testing the UNIPROT mode"
docker run -v ./tests_run/:/predig -v ./uniprot:/uniprot \
    predig-base predig_input1_uniprot_example.csv --output uniprot_output.csv
compare_files "tests_outcome/uniprot_output.csv" "tests_run/uniprot_output.csv" "UNIPROT"

# Test the recombinant mode
echo "Testing the recombinant mode"
docker run -v ./tests_run/:/predig -v ./uniprot:/uniprot \
    predig-base predig_input2_recombinant_example.csv --output recombinant_output.csv --type recombinant
compare_files "tests_outcome/recombinant_output.csv" "tests_run/recombinant_output.csv" "Recombinant"

# Test the FASTA mode
echo "Testing the FASTA mode"
docker run -v ./tests_run/:/predig -v ./uniprot:/uniprot \
    predig-base predig_input3_b2m_fasta_example.fasta --output fasta_output.csv --type fasta --alleles predig_input3_alleles_example.csv
compare_files "tests_outcome/fasta_output.csv" "tests_run/fasta_output.csv" "FASTA"

# Clean up
echo "Cleaning up generated outputs"
rm -rf tests_run

echo "✅ All tests passed successfully!"