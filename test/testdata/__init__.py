from sameproject.ops.notebooks import read_notebook
from sameproject.data.config import SameConfig
from typing import Optional, Callable, List
from base64 import urlsafe_b64encode
from pathlib import Path
from box import Box
import pytest
import json

# Registry of fully-configured notebooks, same configs and requirements.txt
# files. Tests can request notebooks as pytest fixtures by name or group,
# and each notebook comes with a success condition that should validated by
# the test to ensure it has been executed correctly.
_registry = {}


def notebook(*args) -> Callable:
    """
    Returns a pytest decorator for the given name - see _get_decorator().
    """
    entries = []
    for name in args:
        if name not in _registry:
            raise Exception("Attempted to fetch non-existent testdata '{name}'.")

        entries.append(_registry[name])

    return _get_decorator(entries)


def notebooks(*args) -> Callable:
    """
    Returns a pytest decorator for the given group - see _get_decorator().
    """
    entries = []
    for entry in _registry.values():
        if entry.group in args:
            entries.append(entry)

    if len(entries) == 0:
        raise Exception("Attempted to fetch non-existent testdata groups '{args}'.")

    return _get_decorator(entries)


def _get_decorator(entries: List[dict]) -> Callable:
    """
    Returns a pytest parametrize decorator for the given list of registry
    entries. Entries are parametrized with the fields 'config', 'notebook',
    'requirements' and 'validation_fn' for the config file, notebook
    dictionary, requirements.txt file and validation function respectively.
    """
    ids = [entry.name for entry in entries]
    params = "config, notebook, requirements, validation_fn"
    data = [(
        entry.config,
        entry.notebook,
        entry.requirements,
        entry.validation_fn,
    ) for entry in entries]

    return pytest.mark.parametrize(params, data, ids=ids)


def _register_notebook(
    name: str,
    desc: str,
    group: str,
    config_path: Path,
    validation_fn: Optional[Callable[dict, bool]] = None,
):
    """Registers a notebook with the given name, path and callback function."""
    if not config_path.exists():
        raise Exception(f"Attempted to register testdata '{name}' with a non-existent config: {config_path}")

    with config_path.open("r") as file:
        config = SameConfig.from_yaml(file.read())
        config = config.resolve(config_path.parent)
        config = config.inject_runtime_options()

    nb_path = Path(config.notebook.path)
    if not nb_path.exists():
        raise Exception(f"Attempted to register testdata '{name}' with a non-existent notebook: {nb_path}")
    nb = read_notebook(nb_path)

    req = None
    if "requirements" in config.notebook:
        req_path = Path(config.notebook.requirements)
        if not req_path.exists():
            raise Exception(f"Attempted to register testdata '{name}' with a non-existent requirements.txt: {req_path}")

        with req_path.open("r") as file:
            req = file.read()

    _registry[name] = Box({
        "name": name,
        "desc": desc,
        "group": group,
        "config": config,
        "notebook": nb,
        "requirements": req,
        "validation_fn": validation_fn,
    })


# Tagged notebooks for testing different combinations of tags and code in the
# notebook parsing code in 'sameproject/ops/notebooks.py'. The validation
# function checks that the correct number of steps and cells are parsed.
_tagged = [
    ("code", 1, 3),
    ("code_tag", 2, 2),
    ("code_tag_code", 2, 2),
    ("tag", 2, 2),
    ("tag_code", 1, 1),
    ("tag_code_tag", 2, 2),
    ("tag_code_tag_code", 2, 2),
    ("tag_tag", 2, 2),
    ("tag_tag_code", 2, 2),
    ("code_tag_code_tag_code", 3, 3),
    ("code_code_tag_code_code_tag_code_code", 3, 6),
]
for name, steps, cells in _tagged:
    def validation_fn(steps, cells):  # for capturing steps/cells in closure
        return lambda res: res["steps"] == steps and res["cells"] == cells

    _register_notebook(
        f"tagged_{name}",
        f"Tests tag/code combination '{name}'.",
        "tagged",
        Path(__file__).parent / f"tagged/{name}.yaml",
        validation_fn(steps, cells),
    )


# Notebooks that stress-test various weak points in SAME and pin down features
# that every backend should support. This is stuff like making sure variables
# defined in one step are accessible from another step, making sure exploding
# variables are supported, making sure requirements are installed etc. The
# validation functions should be run against the output context of the last
# step in the notebook execution.
def _validate_features_serialised_modules(res):
    e = urlsafe_b64encode("test".encode())
    return res["x"] == e and res["y"] == e and res["z"] == e


def _validate_features_exploding_variables(res):
    with pytest.raises(Exception):
        next(res["x"])
    with pytest.raises(Exception):
        next(res["y"])
    return True


def _validate_features_datasets(res):
    path = Path(__file__).parent / "features/datasets/default.json"
    with path.open("r") as file:
        data = json.loads(file.read())

    return json.dumps(data) == json.dumps(json.load(res["x"]))


_register_notebook(
    "features_function_references",
    "Checks that functions can reference each other in notebooks.",
    "features",
    Path(__file__).parent / "features/function_references/same.yaml",
    lambda res: res["x"] == 1,
)
_register_notebook(
    "features_imported_functions",
    "Checks that imports work both globally and in function scope.",
    "features",
    Path(__file__).parent / "features/imported_functions/same.yaml",
    lambda res: json.loads(res["x"])["x"] == 0,
)
_register_notebook(
    "features_multistep",
    "Checks that multistep notebooks are supported.",
    "features",
    Path(__file__).parent / "features/multistep/same.yaml",
    lambda res: res["y"] == "1",
)
_register_notebook(
    "features_requirements_file",
    "Checks that requirements.txt files are supported.",
    "features",
    Path(__file__).parent / "features/requirements_file/same.yaml",
)
_register_notebook(
    "features_serialised_modules",
    "Checks that imported modules can be accessed across steps.",
    "features",
    Path(__file__).parent / "features/serialised_modules/same.yaml",
    _validate_features_serialised_modules,
)
_register_notebook(
    "features_exploding_variables",
    "Checks that exploding variables are supported for unserialisable variables.",
    "features",
    Path(__file__).parent / "features/exploding_variables/same.yaml",
    _validate_features_exploding_variables,
)
_register_notebook(
    "features_datasets",
    "Checks that 'sdk.dataset(...)' integration is working correctly.",
    "features",
    Path(__file__).parent / "features/datasets/same.yaml",
    _validate_features_datasets,
)


# A selection of pytorch notebooks found in the wild.
_register_notebook(
    "pytorch_first_neural_network",
    "Trains a simple MNIST classifier using a linear perceptron.",
    "pytorch",
    Path(__file__).parent / "pytorch/first_neural_network/same.yaml",
)
_register_notebook(
    "pytorch_neural_network_from_scratch",
    "Trains a basic one-layer neural network as an introduction to pytorch.",
    "pytorch",
    Path(__file__).parent / "pytorch/neural_network_from_scratch/same.yaml",
)
_register_notebook(
    "pytorch_a_gentle_introduction_to_pytorch",
    "A basic introduction to deep learning with pytorch.",
    "pytorch",
    Path(__file__).parent / "pytorch/a_gentle_introduction_to_pytorch/same.yaml",
)
_register_notebook(
    "pytorch_bag_of_words",
    "Implements a bag-of-words text classifier.",
    "pytorch",
    Path(__file__).parent / "pytorch/bag_of_words/same.yaml",
)
_register_notebook(
    "pytorch_concise_logistic_regression",
    "Trains an image classifier using concise logistic regression.",
    "pytorch",
    Path(__file__).parent / "pytorch/concise_logistic_regression/same.yaml",
)
_register_notebook(
    "pytorch_continuous_bag_of_words",
    "Implements a continuous bag-of-words text classifier.",
    "pytorch",
    Path(__file__).parent / "pytorch/continuous_bag_of_words/same.yaml",
)
_register_notebook(
    "pytorch_deep_continuous_bag_of_words",
    "Implements a continuous bag-of-words text classifier using deep neural networks.",
    "pytorch",
    Path(__file__).parent / "pytorch/deep_continuous_bag_of_words/same.yaml",
)
_register_notebook(
    "pytorch_introduction_to_gnns_with_pytorch_geometric",
    "A guide to using graph neural networks in pytorch.",
    "pytorch",
    Path(__file__).parent / "pytorch/introduction_to_gnns_with_pytorch_geometric/same.yaml",
)
_register_notebook(
    "pytorch_pytorch_hello_world",
    "A baby-steps introduction to deep learning in pytorch.",
    "pytorch",
    Path(__file__).parent / "pytorch/pytorch_hello_world/same.yaml",
)
_register_notebook(
    "pytorch_pytorch_logistic_regression",
    "Implements a logistic regression model from scratch for image classification.",
    "pytorch",
    Path(__file__).parent / "pytorch/pytorch_logistic_regression/same.yaml",
)
_register_notebook(
    "pytorch_roberta_fine_tuning_emotion_classification",
    "Fine-tunes a language model to classify the emotional content of text.",
    "pytorch",
    Path(__file__).parent / "pytorch/roberta_fine_tuning_emotion_classification/same.yaml",
)


# A selection of tensorflow notebooks found in the wild.
_register_notebook(
    "tensorflow_siamese_network",
    "Trains a Siamese network for classifying images.",
    "tensorflow",
    Path(__file__).parent / "tensorflow/siamese_network/same.yaml",
)
_register_notebook(
    "tensorflow_named_entity_recognition_transformers",
    "Trains a transformer network for identifying named entities in text.",
    "tensorflow",
    Path(__file__).parent / "tensorflow/named_entity_recognition_transformers/same.yaml",
)
_register_notebook(
    "tensorflow_attention_is_all_you_need",
    "Implements a small transformer model for manipulating human-readable dates.",
    "tensorflow",
    Path(__file__).parent / "tensorflow/attention_is_all_you_need/same.yaml",
)
_register_notebook(
    "tensorflow_feature_tokenizer_transformer",
    "Trains a Feature Tokenizer Transformer network from scratch.",
    "tensorflow",
    Path(__file__).parent / "tensorflow/feature_tokenizer_transformer/same.yaml",
)
_register_notebook(
    "tensorflow_object_detection_selective_search",
    "Trains an object detector from a base image classification model.",
    "tensorflow",
    Path(__file__).parent / "tensorflow/object_detection_selective_search/same.yaml",
)
_register_notebook(
    "tensorflow_object_detection_sliding_window",
    "Another approach to detecting objects based on an image classification model.",
    "tensorflow",
    Path(__file__).parent / "tensorflow/object_detection_sliding_window/same.yaml",
)
_register_notebook(
    "tensorflow_text_classification_attentional_positional_embeddings",
    "Trains a text classification model using a transformer network.",
    "tensorflow",
    Path(__file__).parent / "tensorflow/text_classification_attentional_positional_embeddings/same.yaml",
)
_register_notebook(
    "tensorflow_variational_auto_encoder",
    "An introduction to variational autoencoders for generative modelling of MNIST.",
    "tensorflow",
    Path(__file__).parent / "tensorflow/variational_auto_encoder/same.yaml",
)
