# SMART Extractor 
Extracts data from GSF PDFs for SMART facilitators. 
Data is extracted using [Tabula](https://github.com/tabulapdf/tabula-java) (with its python bindings), then cleaned up. 
Since PDF data extraction is not perfect, the script collections emails (strings containing '@')
and outputs the set of emails for which no entry was extracted; these will have to be extracted
by hand.

## Dependencies
 - python (tested in 3.6)
 - java (7 or 8)
 - [tabula-py](https://github.com/chezou/tabula-py)

## How to install dependencies
 1. Download and install [python](https://www.python.org/downloads/) and [Java](http://www.oracle.com/technetwork/java/javase/downloads/index.html), if you don't have them
 2. (optional) Install [virtualenv](https://virtualenv.pypa.io/en/stable/installation/) and configure an environment
     1. `pip install virtualenv`
     2. `virtualenv pdf`
     3. `pdf\Scripts\activate` (use `deactivate` to exit the virtualenv) 
 3. Install tabula-py: `pip install tabula-py`
    *NOTE*: tabula-py relies on pandas; it is strongly recommended that you install this within a virtualenv

## How to use this script

### Basic usage

```
python smart_extractor.py input.pdf
```
This will extract data from `input.pdf`, saving the extracted data in `output.csv` and the missed emails in `missed.csv`.
If `output.csv` or `missed.csv` exist, you can supply different output names with `-o` and `-m`, or use `-f` to overwrite
existing files.

### Batch convert
```
python smart_extractor.py input1.pdf path/to/input2.pdf directory/of/pdfs/
```
You can supply multiple PDF files, as well as directories containing PDFs. The results are collected and written to output.csv and missed.csv.

### All options
```
usage: smart_extractor.py [-h] [-o OUTPUT] [-m MISSED] [-f] [-q]
                          input [input ...]

Extract GSF data from PDF. Good entries are saved in output.csv; entries that
couldn't be procssed are saved in output-missed.csv.

positional arguments:
  input                 a PDF file, or directory of PDF files, to process

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        filename for extracted entries
  -m MISSED, --missed MISSED
                        filename for emailed not found in extracted entries
  -f, --force           force overwrite of existing output files
  -q, --quiet           don't print processing info to the command line
``` 
