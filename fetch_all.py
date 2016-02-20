from six.moves.urllib import request
from six.moves.urllib.parse import urljoin
from string import ascii_lowercase
from time import sleep

delay = 0.5
base_url = "ftp://ftp.iana.org/tz/releases/"
data_path = "tzdata/"
tzdata_format = "tzdata{year}{v}.tar.gz"
sig_format = "{filename}.asc"

missing_versions = []
missing_sigs = []

for ii in range(1998, 2016):
    jj = 0
    for v in ascii_lowercase:
        b_fname = tzdata_format.format(year=ii, v=v)
        sig_bfname = sig_format.format(filename=b_fname)

        url = urljoin(base_url, b_fname)
        sig_url = urljoin(base_url, sig_bfname)

        fname = urljoin(data_path, b_fname)
        sig_fname = urljoin(data_path, sig_bfname)

        try:
            print(url)
            request.urlretrieve(url, fname)     # Download the tzdata file
            print(b_fname)
            jj = 0
        except IOError:
            missing_versions.append(b_fname)
            jj += 1
            if jj > 1:
                break
            else:
                continue

        try:
            request.urlretrieve(sig_url, sig_fname)
        except IOError:
            missing_sigs.append(sig_bfname)

        sleep(delay)

print("Missing versions: ")
print(missing_versions)

print("Missing signatures: ")
print(missing_sigs)
