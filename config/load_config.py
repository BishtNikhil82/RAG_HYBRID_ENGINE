import yaml

def load_yaml_config(config_path):
    with open(config_path) as f:
        config_dct = yaml.safe_load(f)

    return config_dct
