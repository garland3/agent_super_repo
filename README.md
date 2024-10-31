# Agent Super Repo

This repository contains various AI agent implementations and testing projects:

## Project Structure

- **langchain_simple_agent/**: Implementation of a simple agent using LangChain framework
  - Contains basic test implementations and examples
  - See folder's README.md for specific details

- **selenium_agent/**: Agent implementation using Selenium for web automation
  - Contains test scripts and configurations
  - Includes settings.yaml for configuration

- **omni-parse-test/**: Testing environment for Microsoft's OmniParser
  - Implementation of GUI parsing and interaction
  - Contains OmniParser integration tests
  - Note: Recommended to run on Linux environment

- **utils/**: Utility scripts and helper functions
  - Contains conda environment management scripts
  - Helper utilities for the project

## Requirements

See `requirements.txt` for all dependencies.

## Setup

Each subfolder contains its own README with specific setup instructions for that component.

I have a conda env named 'agents'

```bash
conda create -n agents python=3.12
conda activate agents
pip install -r requirements.txt
```

## Note

Some components may have specific environment requirements. Please refer to individual folder READMEs for detailed setup instructions.



