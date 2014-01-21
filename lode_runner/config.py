try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser

import codecs


def load_json(json_file, encoding):
    """ This will use the json module to to read in the config json file.
    """
    import json
    with codecs.open(json_file, 'r', encoding=encoding) as handle:
        config = json.load(handle)

    return config