from ruamel.yaml import YAML

def convert_to_yaml(text):
    yaml = YAML(typ='safe')
    return yaml.load(text)