import re
import os
from os import path

from functools import partial

from config import load_config

# Get a list of files and parse out the versions that work

def update_with_matching(flist, c_re, c_key, c_dict=None, key_group='version'):
    """
    Updates an existing dictionary with items from a file list whose names
    match the regular expression.

    :param flist:
        A list of files.

    :param c_re:
        Any function returning a match object with a group named by
        :param:`key_group`. Passing a compiled regular expression uses
        the `match` method.

    :param c_key:
        The key under which to add this entry to the sub-dictionary.

    :param c_dict:
        An existing dictionary of dictionaries to updated with the matching
        file name. If no dictionary provided, a new dictionary will be
        generated.

    :param key_group:
        The name of the group from which to pull the dictionary keys.

    :returns:
        Returns a dictionary of dictionaries.
    """
    c_dict = c_dict or {}
    if not hasattr(c_re, '__call__'):
        # Assume it's a compiled regular expression and call 'match'
        c_re = c_re.match

    for fname in flist:
        m = c_re(fname)

        if m is not None:
            key = m.group(key_group)
            subdict = c_dict.setdefault(key, {})
            subdict[c_key] = fname

    return c_dict

# Load from config
(data_regex, sig_regex, zi_regex,
 data_key, sig_key, zi_key, version_key) = load_config(
 ('data_regex', 'sig_regex', 'zi_regex',
  'data_key', 'iana_sig_key', 'zoneinfo_key', 'version_key'))

# TZData
data_re = re.compile(data_regex)

def get_tzdata_files(flist, c_dict=None, **kwargs):
    kw = dict(c_dict=c_dict,
              c_re=data_re.match,
              c_key=data_key,
              key_group=version_key)

    kw.update(kwargs)

    return update_with_matching(flist, **kw)


# IANA Signatures
sig_re = re.compile(sig_regex)

def get_sig_files(flist, c_dict=None, **kwargs):
    kw = dict(c_dict=c_dict,
              c_re=sig_re.match,
              c_key=sig_key,
              key_group=version_key)

    kw.update(kwargs)

    return update_with_matching(flist, **kw)

# Zoneinfo files
zi_re = re.compile(zi_regex)

def get_zoneinfo_files(flist, c_dict=None, **kwargs):
    kw = dict(c_dict=c_dict,
              c_re=zi_re.match,
              c_key=zi_key,
              key_group=version_key)

    kw.update(kwargs)

    return update_with_matching(flist, **kw)

def load_directory(dir_loc):
    def is_file(x):
        loc = path.join(dir_loc, x)
        return path.isfile(loc)

    return list(filter(is_file, os.listdir(dir_loc)))
