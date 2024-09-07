# L5X Diag Generator

## Description
L5X Diag Generator is a Python-based project designed to automate the generation of L5X files for Rockwell Automation's RSLogix5000 environment. It automates the process of creating custom rungs with associated comments and instructions for various devices. The project reads a CSV file containing device information, applies the logic to pre-defined L5X templates, and generates both the main output L5X and HMI label files.

## Features
- Parses device properties from a CSV file.
- Automatically generates new rungs based on device data.
- Supports module-specific file generation.
- Clears existing rungs from the template files before generating new ones.
- Creates and formats rung content with `CDATA` sections to ensure proper L5X syntax.
- Generates both a primary L5X output file and an HMI labels L5X file.

## Requirements
- Python 3.x
- lxml library

To install `lxml`, you can use the following command:

```bash
pip install lxml
