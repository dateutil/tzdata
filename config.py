import yaml

def load_config(keys=None):
    with open('config.yml', 'r') as yf:
        conf = yaml.load(yf)

    if keys is not None:
        return [conf[k] for k in keys]

    return conf