from io import BufferedReader
from ruamel.yaml import YAML

# from ruamel.yaml import YAML  # Chose ruamel over pyyaml due to default yaml 1.2 support
from cli.same.same_config import SAME_config


def load_same_config_file(file_reader: BufferedReader):
    yaml = YAML(typ="safe")
    yaml_dict = yaml.load("".join(map(bytes.decode, file_reader.readlines())))
    return SAME_config(yaml_dict)
