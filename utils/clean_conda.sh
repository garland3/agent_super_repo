#!/bin/bash

# Get a list of all conda environments except 'base'
conda_envs=$(conda env list | grep -v "base" | awk '{print $1}' | grep -v "^$")

# Loop through each environment and remove it
for env in $conda_envs; do
    echo "Removing conda environment: $env"
    conda remove -n "$env" --all -y
done

echo "Finished removing conda environments."
