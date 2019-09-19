import hashlib
import json

from config import load_config

# Load the configuration
def load_base_metadata():
    base_metadata_file, = load_config(('base_metadata_file',))

    with open(base_metadata_file, 'r') as jf:
        base_metadata = json.load(jf)

    return base_metadata

base_metadata = load_base_metadata()


def get_sha512(fpath):
    with open(fpath, 'rb') as f:
        sha_hasher = hashlib.sha512()
        sha_hasher.update(f.read())

        return sha_hasher.hexdigest()


def generate_metadata(version, fname, fpath, md_base=None):
    md_base = md_base or base_metadata
    md_base = md_base.copy()

    md_base['tzdata_file'] = fname
    md_base['tzversion'] = version
    md_base['tzdata_file_sha512'] = get_sha512(fpath)

    return md_base


def valid_metadata(md_fpath, fpath, md_base=None):
    md_base = md_base or base_metadata

    with open(md_fpath, 'r') as jf:
        md = json.load(jf)

    if md['metadata_version'] < md_base['metadata_version']:
        return False

    sha512 = md.get('tzdata_file_sha512', None)
    return (sha512 is not None and sha512 == get_sha512(fpath))


def save_json(fpath, obj):
    pretty_print = dict(indent=4, sort_keys=True, separators=(',', ': '))
    with open(fpath, 'w') as jf:
        json.dump(obj, jf, **pretty_print)

if __name__ == "__main__":
    from os import listdir, path

    from tzdata_files import get_tzdata_files, data_key, load_directory

    # Get all the valid tzdata files we have in the tzdata location
    (data_loc,
     zi_format,
     zi_meta_loc) = load_config(('tzdata_loc',
                                 'zoneinfo_format_str',
                                 'zoneinfo_metadata_loc'))

    flist = load_directory(data_loc)

    data_files = get_tzdata_files(flist)
    for version, subdict in data_files.items():
        fname = subdict[data_key]
        fpath = path.join(data_loc, fname)

        zi_fname = zi_format.format(version=version)
        zi_fpath = path.join(zi_meta_loc, zi_fname)

        if not (path.exists(zi_fpath) and valid_metadata(zi_fpath, fpath)):
            md = generate_metadata(version, fname, fpath)
            save_json(zi_fpath, md)




