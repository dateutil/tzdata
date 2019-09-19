from os import path

from config import load_config
import subprocess


def valid_signature(fpath, sig_fpath):
    command = ['gpg', '--verify', sig_fpath, fpath]
    rc = subprocess.call(command)
    return not rc

def sign_file(fpath, sig_fpath):
    command = ['gpg', '--output', sig_fpath, '--detach-sig', fpath]

    rc = subprocess.call(command)

    if rc:
        raise SignatureFailedError('Failed with return code: {rc}'.format(rc))

class SignatureFailedError(OSError):
    pass

if __name__ == "__main__":
    (tzdata_loc, iana_sig_loc, du_sig_loc) = load_config(
        ('tzdata_loc', 'iana_sig_loc', 'du_sig_loc')
    )

    from tzdata_files import get_tzdata_files, get_sig_files
    from tzdata_files import load_directory, data_key, sig_key

    d_flist = load_directory(tzdata_loc)
    s_flist = load_directory(iana_sig_loc)

    data_files = get_tzdata_files(d_flist)
    data_files = get_sig_files(s_flist, c_dict=data_files)

    invalid_sigs = []

    for version, subdict in data_files.items():
        try:
            dfname = subdict[data_key]
        except KeyError:
            continue

        try:
            sfname = subdict[sig_key]
        except KeyError:
            continue

        data_path = path.join(tzdata_loc, dfname)
        sig_path = path.join(iana_sig_loc, sfname)
        du_sig_path = path.join(du_sig_loc, sfname)

        if path.exists(du_sig_path) and valid_signature(data_path, du_sig_path):
            continue

        if valid_signature(data_path, sig_path):
            sign_file(data_path, du_sig_path)
        else:
            invalid_sigs.append(sig_path)

    if len(invalid_sigs):
        err_out = 'validation_errors.log'
        with open(err_out, 'w') as f:
            for inv_sig in invalid_sigs:
                print(inv_sig, file=f)

        print("Some invalid signatures were found. See {err_out} for details".format(err_out=err_out))



