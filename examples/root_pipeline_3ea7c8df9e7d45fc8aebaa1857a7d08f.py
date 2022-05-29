
from typing import NamedTuple
from base64 import b64encode
import json
import logging
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.image as mpimg
import numpy as np
import random
from pathlib import Path
import pickle
import sys
import time
import kfp

import torch
import torch.nn as nn
import torch.nn.parallel
import torch.backends.cudnn as cudnn
import torch.optim as optim
import torch.utils.data
import torchvision.datasets as dset
import torchvision.transforms as transforms
import torchvision.utils as vutils
from run_info import run_info_fn


from same_step_000_afdeddf09e474ffdbe0543fd0d775bbd import same_step_000_afdeddf09e474ffdbe0543fd0d775bbd_fn



run_info_comp = kfp.components.create_component_from_func(
    func=run_info_fn,
    packages_to_install=[
        "dill==0.3.5.1",
        "kfp==1.8.12",
    ],
)


same_step_000_afdeddf09e474ffdbe0543fd0d775bbd_comp = create_component_from_func(
    func=same_step_000_afdeddf09e474ffdbe0543fd0d775bbd_fn,
    base_image="combinatorml/jupyterlab-tensorflow-opencv:0.9",
    packages_to_install=[
        "dill==0.3.5.1",
        "pympler==1.0.1",
        "requests==2.27.1",
        'matplotlib', 'numpy', 'Pillow', 'torch', 'torchvision' # TODO: make this a loop
    ],
)


# TODO: support kubeflow-specific config like aws secrets, mlflow endpoints.
@dsl.pipeline(name="Compilation of pipelines",)
def root(
    context='', metadata_url='',
):
    # Generate secrets (if not already created)
    secrets_by_env = {}


    run_info = run_info_comp(run_id=kfp.dsl.RUN_ID_PLACEHOLDER)



    same_step_000_afdeddf09e474ffdbe0543fd0d775bbd = same_step_000_afdeddf09e474ffdbe0543fd0d775bbd_comp(

        input_context="",

        run_info=run_info.outputs["run_info"],
        metadata_url=metadata_url
    )


    same_step_000_afdeddf09e474ffdbe0543fd0d775bbd.execution_options.caching_strategy.max_cache_staleness = "P0D"
    for k in env_vars:
        same_step_000_afdeddf09e474ffdbe0543fd0d775bbd.add_env_variable(V1EnvVar(name=k, value=env_vars[k]))


