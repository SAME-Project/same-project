from traitlets.config import Config
import nbformat as nbf
from nbconvert.exporters import PythonExporter
from nbconvert.preprocessors import TagRemovePreprocessor
from nbconvert.exporters.templateexporter import TemplateExporter
from pathlib import Path
from uuid import uuid4
from typing import Tuple
import time


template = "root.jinja"
config = {
        'Exporter': {'template_file': template,
                     'template_path': ['./']},
        'ExtractOutputPreprocessor': {'enabled': True},
    }

exporter = PythonExporter(config)

def render(compile_path: str, steps: list, same_config: dict) -> Tuple[Path, str]:
    body, resources = exporter.from_notebook_node(
        compile_path, resources={'output_files_dir': compile_path})
    same_config["compile_path"] = compile_path
    root_pipeline_name = f"root_pipeline_{uuid4().hex.lower()}"
    root_path = Path(compile_path) / f"{root_pipeline_name}.py"
    with open(root_path, 'w') as f:
        f.write(body)