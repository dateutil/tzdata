import ftplib

from six import iteritems

from os import path
from os import remove

import sys

from tzdata_files import get_tzdata_files, get_sig_files
from tzdata_files import data_key as dkey
from tzdata_files import sig_key as skey

import yaml


class InvalidSizeError(OSError):
    pass


def get_file_size(ftp_conn, fname, old_type='A'):
    ftp_conn.sendcmd('TYPE I')
    s = ftp_conn.size(fname)
    ftp_conn.sendcmd('TYPE ' + old_type)

    return s


def download_file(ftp_conn, fpath, fname, exp_size=None):
        with open(fpath, 'wb') as cf:
            f.retrbinary('RETR ' + fname, cf.write)

        if exp_size is not None and path.getsize(fpath) != exp_size:
            remove(fpath)

            raise InvalidSizeError('Downloaded file size does not match expectation.')


class InvalidStatusError(OSError):
    pass

def fail_on_invalid_status(f, retr, status_code):
    if not retr.startswith(str(status_code)):
        f.quit()
        raise InvalidStatusError(retr)

if __name__ == '__main__':
    # Load the configuration
    from config import load_config

    keys = ('rate_limit', 'fetch_errors_out', 'ftp_server',
        'dir_loc', 'tzdata_loc', 'iana_sig_loc')
    
    (rate_limit, errors_out, ftp_server,
     dir_loc, data_loc, sig_loc) = load_config(keys)

    dir_loc = dir_loc.split('/')

    # Initialize the connection
    f = ftplib.FTP(ftp_server)
    retr = f.login()

    fail_on_invalid_status(f, retr, '230')

    # Browse to the correct directory
    for cdir in dir_loc:
        retr = f.cwd(cdir)

        fail_on_invalid_status(f, retr, '250')

    # Get a list of all data files and signatures
    flist = f.nlst()
    data_files = get_tzdata_files(flist)
    data_files = get_sig_files(flist, c_dict=data_files)

    # Download any missing files and generate preliminary metadata files
    errors = []
    tzdata_to_download = []
    signatures_to_download = []

    # Figure out what's missing
    for version, subdict in iteritems(data_files):
        dfname = subdict.get(dkey, None)
        if dfname is None:
            continue

        sfname = subdict.get(skey, None)

        data_fpath = path.join(data_loc, dfname)
        sig_fpath = path.join(sig_loc, sfname) if sfname is not None else None

        for fname, fpath, lapp in ((dfname, data_fpath, tzdata_to_download),
                                   (sfname, sig_fpath, signatures_to_download)):
            if fname is None:
                continue

            if not path.exists(fpath):
                exp_size = get_file_size(f, fname)

                lapp.append((fpath, fname, exp_size))

    # Go through and download everything
    print("Downloading tzdata files.")
    for ii, (fpath, fname, exp_size) in enumerate(tzdata_to_download):
        label = dict(fname=fname, ii=ii, total=len(tzdata_to_download))
        sys.stdout.write("Downloading file {ii} of {total}: {fname}\r".format(**label))
        download_file(f, fpath, fname, exp_size)

    sys.stdout.write("\r")
    print("Downloading signature files.")
    for ii, (fpath, fname, exp_size) in enumerate(signatures_to_download):
        label = dict(fname=fname, ii=ii, total=len(tzdata_to_download))
        sys.stdout.write("Downloading file {ii} of {total}: {fname}\r".format(**label))
        download_file(f, fpath, fname, exp_size)

    sys.stdout.write("\r\n")

    for version, subdict in iteritems(data_files):
        dfname = subdict.get(dkey, None)
        if dfname is None:
            continue

        sfname = subdict.get(skey, None)

        data_fpath = path.join(data_loc, dfname)
        sig_fpath = path.join(sig_loc, sfname) if sfname is not None else None

        valid = False
        # If it doesn't exist, download it
        for fname, fpath in ((dfname, data_fpath), (sfname, sig_fpath)):
            if fname is None:
                continue

            if not path.exists(fpath):
                exp_size = get_file_size(f, fname)

                try:
                    download_file(f, fpath, fname, exp_size)
                except InvalidSizeError as e:
                    errors.append((fname, fpath, e))
                    break

    f.quit()

    if len(errors):
        with open(errors_out, 'w') as yf:
            yaml.dump(errors_out)

        print("Errors occurred during the download - " +
              " see {err_out} for details".format(err_out=errors_out))

