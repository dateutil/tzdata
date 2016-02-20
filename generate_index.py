
if __name__ == "__main__":
    import yaml
    from six import iteritems

    from os import path
    from collections import OrderedDict

    from config import load_config

    from tzdata_files import get_zoneinfo_files, get_sig_files, get_tzdata_files
    from tzdata_files import load_directory
    from tzdata_files import version_key, data_key, zi_key

    # Load the configuration we need
    (
     data_loc, iana_sig_loc, du_sig_loc, zi_meta_loc,
     index_loc, latest_loc, version_key, zi_latest_fname,
     data_key, zi_key, iana_sig_key, du_sig_key
    ) = load_config((
        'tzdata_loc', 'iana_sig_loc', 'du_sig_loc',  'zoneinfo_metadata_loc',
        'index_loc', 'latest_loc', 'version_key', 'zi_latest_fname',
        'data_key', 'zoneinfo_key', 'iana_sig_key', 'du_sig_key'
    ))

    (data_flist,
     ianas_flist,
     dus_flist,
     zi_flist) = map(load_directory,
                     (data_loc, iana_sig_loc, du_sig_loc, zi_meta_loc))
    
    data_files = get_tzdata_files(data_flist)
    data_files = get_sig_files(ianas_flist, c_key=iana_sig_key, c_dict=data_files)
    data_files = get_sig_files(dus_flist, c_key=du_sig_key, c_dict=data_files)
    data_files = get_zoneinfo_files(zi_flist, c_dict=data_files)

    out_list = []

    keys = (version_key,
            data_key,
            iana_sig_key,
            du_sig_key,
            zi_key)

    for version, subdict in iteritems(data_files):
        try:
            tzdata = subdict[data_key]
            tzdata_fpath = path.join(data_loc, tzdata)
        except KeyError:
            continue

        try:
            iana_sig = subdict[iana_sig_key]
            iana_sig_fpath = path.join(iana_sig_loc, iana_sig)
        except KeyError:
            iana_sig_fpath = ''

        try:
            du_sig = subdict[du_sig_key]
            du_sig_fpath = path.join(du_sig_loc, du_sig)
        except KeyError:
            du_sig_fpath = ''

        try:
            zi_meta = subdict[zi_key]
            zi_meta_fpath = path.join(zi_meta_loc, zi_meta)
        except KeyError:
            zi_meta_fpath = ''

        dict_items = list(zip(keys,
                              (version,
                               tzdata_fpath,
                               iana_sig_fpath,
                               du_sig_fpath,
                               zi_meta_fpath)))

        out_list.append(dict(dict_items))

    out_list = sorted(out_list, key=lambda x: x[version_key], reverse=True)

    # Get the latest subdict
    latest = out_list[0]

    with open(latest_loc, 'w') as yf:
        yaml.dump(latest, yf, default_flow_style=False)

    with open(index_loc, 'w') as yf:
        yaml.dump(out_list, yf, default_flow_style=False)
