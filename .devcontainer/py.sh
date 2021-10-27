#! /usr/bin/env sh

# Taken from: https://github.com/yagnik/python-template/blob/master/.devcontainer/devcontainer.json
poetry run python "$@" && cd - > /dev/null