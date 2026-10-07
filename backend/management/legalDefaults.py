from pathlib import Path

# TODO: impl cleaner pathing such that it will never have to be manually changed or only one global val need change
MEDIA_DIR = (Path(__file__).resolve().parent) / 'media' 
LEGAL_DIR = MEDIA_DIR/'legal'

def TermsService():
    with open(LEGAL_DIR/'TOS.md', "r") as f:
        return f.read()
