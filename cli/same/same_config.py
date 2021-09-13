from cerberus import Validator, DocumentError


class Metadata:
    def __init__(self, name: str, version: str):
        self._name = name
        self._version = version

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name


class SAMEValidator(Validator):
    def _check_with_must_have_default(self, environments_field_name, all_environments, error):
        if all_environments.get(environments_field_name).get("default", None) is None:
            return DocumentError(environments_field_name, "Environments does not contain a 'default' entry.")


schema = {
    "apiVersion": {"type": "string"},
    "metadata": {
        "type": "dict",
        "schema": {
            "name": {"type": "string", "required": True, "regex": r"^[\d\w]+"},
            "version": {"type": "string", "required": True},
            "labels": {"type": "list"},
            "sha": {"type": "string"},
        },
    },
    "datasets": {
        "type": "dict",
        "schema": {
            "name": {"type": "string", "required": True, "regex": r"^[\d\w]+"},
            "schema_uri": {"type": "string"},
            "environments": {
                "type": "dict",
                "keysrules": {"type": "string", "regex": r"^[\d\w]+"},
                "allow_unknown": True,
            },
        },
    },
    "base_images": {
        "type": "dict",
        "keysrules": {"type": "string", "regex": r"^[\d\w]+"},
        "valuesrules": {
            "type": "dict",
            "schema": {
                "image_tag": {"type": "string", "required": True, "regex": ".*/.*"},
                "packages": {"type": "list"},
                "private_registry": {"type": "boolean"},
            },
        },
        "allow_unknown": True,
        "check_with": "must_have_default",
    },
    "pipeline": {"type": "dict", "schema": {"name": {"type": "string", "required": True}, "package": {"type": "string", "required": True}}},
}


class SAME_config:
    def __init__(
        self,
        metadata: Metadata,
        config_file_path: str = "same.yaml",
        apiVersion: str = "sameproject.io/v1alpha1",
    ):
        # environments: dict,
        # pipeline: dict,
        # datasets: dict,
        # run: dict,
        self._metadata = metadata
        # self.environments = environments
        # self.pipeline = pipeline
        # self.datasets = datasets
        # self.run = run
        self._config_file_path = config_file_path

    @property
    def metadata(self):
        return self._metadata

    @metadata.setter
    def metadata(self, value):
        self._metadata.name = value["name"]
        self._metadata.version = value["version"]


# // DataSet is the data to be downloaded/mounted into the cluster.
# type DataSet struct {
# 	Type          string `yaml:"type,omitempty"`
# 	URL           string `yaml:"url,omitempty"`
# 	MakeLocalCopy bool   `yaml:"makeLocalCopy,omitempty"`
# }

# // Run is the name and specific parameters to run against one of the previously created pipelines.
# // RunWrapper comes from here: https://medium.com/@nate510/dynamic-json-umarshalling-in-go-88095561d6a0
# type Run struct {
# 	Name       string                 `yaml:"name,omitempty"`
# 	Parameters map[string]interface{} `yaml:"parameters,omitempty"`
# }

# type Environment struct {
# 	ImageTag                 string                `yaml:"image_tag,omitempty"`
# 	AppendCurrentEnvironment bool                  `yaml:"append_current_environment,omitempty"`
# 	Packages                 []string              `yaml:"packages,omitempty,omitempty"`
# 	PrivateRegistry          bool                  `yaml:"private_registry,omitempty"`
# 	Credentials              RepositoryCredentials `yaml:"repository_credentials,omitempty"`
# }

# type RepositoryCredentials struct {
# 	SecretName string `yaml:"secretname,omitempty"`
# 	Server     string `yaml:"server,omitempty"`
# 	Username   string `yaml:"username,omitempty"`
# 	Password   string `yaml:"password,omitempty"`
# 	Email      string `yaml:"email,omitempty"`
# }
