from io import BufferedReader
from ruamel.yaml import YAML  # Chose ruamel over pyyaml due to default yaml 1.2 support


def load_same_config_file(file_reader: BufferedReader):
    yaml = YAML(typ="safe")
    return yaml.load("".join(map(bytes.decode, file_reader.readlines())))
