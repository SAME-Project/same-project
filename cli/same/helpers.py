from ruamel.yaml import YAML
from ruamel.yaml.compat import StringIO


def dict_to_yaml(input_dict: dict) -> dict:
    yaml = YAML(typ="safe")
    s = StringIO()
    try:
        yaml.dump(input_dict, stream=s)
        return s.getvalue()
    except SyntaxError as e:
        raise SyntaxError(f"Failure converting dict to yaml: {e}")
