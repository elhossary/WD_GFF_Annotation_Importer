# GFF to Wikidata importing Tool

## Description
This tool can be used to import genomic annotations in GFF files to Wikidata. It automates the importing process. It is a part of [InteractOA](https://interactoa.toolforge.org/) project.
## Prerequisites
1. Install dependencies:
   - ```pip install wikidataintegrator pywikibot bcbio-gff pandas```
3. Clone this repo
2. Modify user-config.py
    - Go to line 43
    - Add your Wikidata's username

## Usage
- The usage is simple, only run 'run.py', then it will ask for the GFF path and the qualifier ID of the strain you want to link the annotations to.
- Afterwards, it will ask for your Wikidata username and password 

