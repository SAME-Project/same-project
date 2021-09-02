from ruamel.yaml import YAML  # Chose ruamel over pyyaml due to default yaml 1.2 support
from pathlib import Path


def load_same_config_file(file_path):
    yaml = YAML(typ="safe")
    return yaml.load(Path(file_path).read_text(encoding="ascii"))
