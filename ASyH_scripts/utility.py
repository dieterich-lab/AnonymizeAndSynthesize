from os.path import dirname, join
import json


METADATA_PATH = join(dirname(__file__), 'metadata.json')


def get_metadata():
    with open(METADATA_PATH, 'r') as json_file:
        metadata = json.load(json_file)
    return metadata
