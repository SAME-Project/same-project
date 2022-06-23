import pytest


# For defining flags that can enable or disable tests based on a pytest mark.
additional_flags = [
    ["kubeflow", {
        "action": "store_true",
        "default": False,
        "help": "run kubeflow backend tests, requires kubeflow installation",
    }],
    ["functions", {
        "action": "store_true",
        "default": False,
        "help": "run functions backend tests, requires azure authentication",
    }],
    ["aml", {
        "action": "store_true",
        "default": False,
        "help": "run aml backend tests, requires azure authentication",
    }],
    ["external", {
        "action": "store_true",
        "default": False,
        "help": "include pytorch, tensorflow and sklearn notebooks in backend tests",
    }],
]


def pytest_addoption(parser):
    for [name, opts] in additional_flags:
        parser.addoption(f"--{name}", **opts)


def pytest_configure(config):
    for [name, _] in additional_flags:
        config.addinivalue_line(
            "markers", f"{name}: mark test to run only when --{name} flag is set"
        )


def pytest_collection_modifyitems(config, items):
    for [name, _] in additional_flags:
        if config.getoption(f"--{name}"):
            continue  # don't skip if flag is set

        skip = pytest.mark.skip(f"--{name} flag isn't set")
        for item in items:
            if name in item.keywords:
                item.add_marker(skip)
