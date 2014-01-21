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


def load_ini(ini_file, encoding):
    """ Parse and collapse a ConfigParser-Style ini file into a nested,
    eval'ing the individual values, as they are assumed to be valid
    python statement formatted """

    tmpconfig = ConfigParser.ConfigParser()
    with codecs.open(ini_file, 'r', encoding) as f:
        tmpconfig.readfp(f)

    config = {}
    for section in tmpconfig.sections():
        config[section] = {}
        for option in tmpconfig.options(section):
            config[section][option] = tmpconfig.get(section, option)

    return config