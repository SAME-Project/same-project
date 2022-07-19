import json
import os

from base64 import b64encode
from pathlib import Path
from typing import Dict, List, Optional, Union

from .constants import DEFAULT_TAG, IMAGE
from .utils import get_entrypoint, get_dependencies, pip_list, script_to_module


def convert_to_transform(script: os.PathLike, tag: Optional[str] = None) -> Dict:
    # import pdb; pdb.set_trace()
    module = script_to_module(script)
    entrypoint = get_entrypoint(module)
    dependencies = sanitize_dependencies(get_dependencies(entrypoint))
    image = select_image(dependencies, tag)
    encoded_source = b64encode(Path(script).read_bytes())
    return dict(
        cmd=["python3", "entrypoint.py", encoded_source.decode(), *dependencies],
        image=image
    )


def sanitize_dependencies(dependencies: Union[List[str], None]) -> List[str]:
    if not dependencies:
        return []
    packages = pip_list()

    sanitized_dependencies = []
    for dependency in dependencies:
        if "==" not in dependency:
            message = f"Specified dependency {dependency} is not pinned to a version. "
            version = packages.get(dependency)
            if version:
                message += f"Using the version of the dependency installed: {version}"
                dependency = f"{dependency}=={version}"
            else:
                message += "No installed version of the dependency found. "
                message += "Against our better judgement we are leaving this unpinned. "
            print(message)
        sanitized_dependencies.append(dependency)
    return sanitized_dependencies


def select_image(dependencies: List[str], tag: Optional[str]) -> str:
    tag = tag or DEFAULT_TAG
    image = f"{IMAGE}:{tag}"
    if "opencv-python" in [dep.split("==")[0] for dep in dependencies]:
        return f"{image}-opencv"
    return image


def write_pipeline(pipeline: os.PathLike, transform: Dict) -> None:
    pipeline = Path(pipeline)
    if not pipeline.exists():
        payload = dict(
            pipeline=dict(name=pipeline.stem),
            description="",
            input=dict(),
        )
    else:
        try:
            payload = json.loads(pipeline.read_bytes())
        except json.decoder.JSONDecodeError:
            raise RuntimeError(f"Could not read file: {pipeline}")

    payload["transform"] = transform
    try:
        with pipeline.open("w") as file:
            json.dump(payload, file, indent=2)
    except IOError as err:
        raise RuntimeError(
            f"Could not create file: {pipeline}"
        ) from err
    return
