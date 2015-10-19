"""
Contains useful functions and utilities that are not neccessarily only useful
for this module. But are also used in differing modules insidide the same
project, and so do not belong to anything specific.
"""


import sys
import os
import logging
import string
import unicodedata
import re
import json
import imp

from cloghandler import ConcurrentRotatingFileHandler


def load_config():
    """
    Loads configuration from config.py and also from local_config.py
    
    :return dictionary
    """
    conf = load_module('config.py')
    conf.update(load_module('local_config.py'))
    conf['PROJ_HOME'] = os.path.dirname('..')
    return conf

def load_module(filename):
    """
    Loads module, first from config.py then from local_config.py
    
    :return dictionary
    """
    
    filename = os.path.join(filename)
    d = imp.new_module('config')
    d.__file__ = filename
    try:
        with open(filename) as config_file:
            exec(compile(config_file.read(), filename, 'exec'), d.__dict__)
    except IOError as e:
        pass
    res = {}
    from_object(d, res)
    return res

def setup_logging(file_, name_, level=config['LOGGING_LEVEL']):
    """
    Sets up generic logging to file with rotating files on disk

    :param file_: the __file__ doc of python module that called the logging
    :param name_: the name of the file that called the logging
    :param level: the level of the logging DEBUG, INFO, WARN
    :return: logging instance
    """

    level = getattr(logging, level)

    logfmt = '%(levelname)s\t%(process)d [%(asctime)s]:\t%(message)s'
    datefmt = '%m/%d/%Y %H:%M:%S'
    formatter = logging.Formatter(fmt=logfmt, datefmt=datefmt)
    logging_instance = logging.getLogger(name_)
    fn_path = os.path.join(os.path.dirname(file_), PROJ_HOME, 'logs')
    if not os.path.exists(fn_path):
        os.makedirs(fn_path)
    fn = os.path.join(fn_path, '{0}.log'.format(name_))
    rfh = ConcurrentRotatingFileHandler(filename=fn,
                                        maxBytes=2097152,
                                        backupCount=5,
                                        mode='a',
                                        encoding='UTF-8')  # 2MB file
    rfh.setFormatter(formatter)
    logging_instance.handlers = []
    logging_instance.addHandler(rfh)
    logging_instance.setLevel(level)

    return logging_instance


def from_object(from_obj, to_obj):
    """Updates the values from the given object.  An object can be of one
    of the following two types:

    Objects are usually either modules or classes.
    Just the uppercase variables in that object are stored in the config.

    :param obj: an import name or object
    """
    for key in dir(from_obj):
        if key.isupper():
            to_obj[key] = getattr(from_obj, key)


def overrides(interface_class):
    """
    To be used as a decorator, it allows the explicit declaration you are
    overriding the method of class from the one it has inherited. It checks that
     the name you have used matches that in the parent class and returns an
     assertion error if not
    """
    def overrider(method):
        """
        Makes a check that the overrided method now exists in the given class
        :param method: method to override
        :return: the class with the overriden method
        """
        assert(method.__name__ in dir(interface_class))
        return method

    return overrider

