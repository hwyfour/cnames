# cnames

A script for building two trees from the reverse domain name notation of both CNAMEs and URLs.

The python script `cnames.py` outputs a number of trees into individual JSON files per tree. You may wish to combine these all into one large tree after generating the smaller trees for each URL.

## Usage

### Setup and initialize your Python virtual environment

    $ virtualenv venv
    $ source venv/bin/activate
    $ pip install -r requirements.txt

### Install the Grunt dependencies

    $ npm install

### Run the tree generator

    $ python cnames.py -i <input csv>

### Concatenate the individual trees into two final trees

    $ grunt
