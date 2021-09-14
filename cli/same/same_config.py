from cerberus import Validator
from box import Box


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

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, version):
        self._version = version

    @property
    def labels(self) -> list:
        return self._labels

    @labels.setter
    def labels(self, labels):
        self._labels = labels

    @property
    def sha(self):
        return self._sha

    @sha.setter
    def sha(self, sha):
        self._sha = sha


class Dataset:
    _environments = Box()

    def __init__(self, name: str):
        self._name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def schema_uri(self):
        return self._schema_uri

    @schema_uri.setter
    def schema_uri(self, schema_uri):
        self._schema_uri = schema_uri

    @property
    def environments(self):
        return self._environments

    @environments.setter
    def environments(self, environments):
        self._environments = environments

    def add_environment(self, name, value):
        self._environments[name] = value

    def drop_environment(self, name):
        self._environments.pop(name)


class Datasets(Box):
    def __init__(self):
        pass

    def add_dataset(self, name, dataset):
        ds = Dataset(name)
        ds.schema_uri = dataset.get("schema_uri", None)
        for k in dataset["environments"]:
            ds.add_environment(k, dataset["environments"][k])

        self[name] = ds

    def drop_dataset(self, name):
        self.pop(name)


class BaseImage:
    _packages = []

    def __init__(self, name: str):
        self._name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def image_tag(self):
        return self._image_tag

    @image_tag.setter
    def image_tag(self, image_tag):
        self._image_tag = image_tag

    @property
    def packages(self):
        return self._packages

    @packages.setter
    def packages(self, packages: list):
        self._packages = packages

    @property
    def private_registry(self):
        return self._private_registry

    @private_registry.setter
    def private_registry(self, private_registry):
        self._private_registry = private_registry


class BaseImages(Box):
    def __init__(self):
        pass

    def add_base_image(self, name, base_image):
        bi = BaseImage(name)
        bi.image_tag = base_image.get("image_tag")
        for v in base_image.get("packages", []):
            bi.packages.append(v)
        bi.private_registry = base_image.get("private_registry", False)

        self[name] = bi

    def drop_base_image(self, name):
        self.pop(name)


class Notebook:
    def __init__(self, name: str, path: str):
        self._name = name
        self._path = path

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        self._path = path


class Run:
    def __init__(self, name: str, sha: str):
        self._name = name
        self._sha = sha

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def sha(self):
        return self._sha

    @sha.setter
    def sha(self, sha):
        self._sha = sha

    @property
    def parameters(self):
        return self._parameters

    @parameters.setter
    def parameters(self, parameters):
        self._parameters = parameters


class SAMEValidator(Validator):
    def _validate_must_have_default(self, constraint, base_images_field_name, all_base_images):
        if constraint and (all_base_images is None or all_base_images.get("default", None) is None):
            self._error(base_images_field_name, "Base images does not contain a 'default' entry.")


schema = {
    "apiVersion": {"type": "string", "required": True},
    "metadata": {
        "type": "dict",
        "schema": {
            "name": {"type": "string", "required": True, "regex": r"^[\d\w]+"},
            "version": {"type": "string", "required": True},
            "labels": {"type": "list"},
            "sha": {"type": "string"},
        },
        "required": True,
    },
    "datasets": {
        "type": "dict",
        "keysrules": {"type": "string", "regex": r"^[\d\w]+"},
        "valuesrules": {
            "type": "dict",
            "schema": {
                "schema_uri": {"type": "string"},
                "environments": {
                    "type": "dict",
                    # TODO: Figure out why we can't check for datasets->environments not having a default field
                    # "must have default": True, -- could not get this to work for some reason
                },
            },
        },
        "allow_unknown": True,
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
        "must have default": True,
    },
    "notebook": {"type": "dict", "schema": {"name": {"type": "string", "required": True}, "path": {"type": "string", "required": True}}},
    "run": {
        "type": "dict",
        "schema": {
            "name": {"type": "string", "required": True},
            "sha": {"type": "string", "required": True},
            "parameters": {
                "type": "dict",
            },
        },
    },
}


class SAME_config:
    _datasets = Datasets()
    _base_images = BaseImages()

    def __init__(
        self,
        same_config_dict,
        config_file_path: str = "same.yaml",
        apiVersion: str = "sameproject.io/v1alpha1",
    ):

        self.metadata = same_config_dict.get("metadata", None)
        self.datasets = same_config_dict.get("datasets", None)
        self.base_images = same_config_dict.get("base_images", None)
        self.notebook = same_config_dict.get("notebook")
        self.run = same_config_dict.get("run")
        self._config_file_path = config_file_path

    @property
    def metadata(self):
        return self._metadata

    @metadata.setter
    def metadata(self, value):
        self._metadata = Metadata(value["name"], value["version"])
        self._metadata.labels = value.get("labels", None)
        self._metadata.sha = value.get("sha", None)

    @property
    def datasets(self):
        return self._datasets

    @datasets.setter
    def datasets(self, value):
        for k in value:
            self._datasets.add_dataset(k, value[k])

    @property
    def base_images(self):
        return self._base_images

    @base_images.setter
    def base_images(self, value):
        for k in value:
            self._base_images.add_base_image(k, value[k])

    @property
    def notebook(self):
        return self._notebook

    @notebook.setter
    def notebook(self, value):
        self._notebook = Notebook(value["name"], value["path"])

    @property
    def run(self):
        return self._run

    @run.setter
    def run(self, value):
        this_run = Run(value["name"], value["sha"])
        this_run.parameters = value.get("parameters", None)
        self._run = this_run


# type RepositoryCredentials struct {
# 	SecretName string `yaml:"secretname,omitempty"`
# 	Server     string `yaml:"server,omitempty"`
# 	Username   string `yaml:"username,omitempty"`
# 	Password   string `yaml:"password,omitempty"`
# 	Email      string `yaml:"email,omitempty"`
# }
