py_zero_steps = """
# ---

foo = "bar"

# +
import tensorflow
"""

py_zero_steps_with_params = """
# ---

# + tags=["parameters"]
foo = "bar"

# +
import tensorflow
"""

py_one_step = """
# ---

# +
foo = "bar"

# +
# + tags=["same_step_1"]
import tensorflow
"""

py_one_step_with_cache = """
# ---

# + tags=["parameters"]
foo = "bar"

# +
# + tags=["same_step_1", "cache=P20D"]
import tensorflow
"""

# 	TWO_STEPS = `
# # ---

# # + tags=["parameters"]
# foo = "bar"

# # +
# # + tags=["same_step_1"]
# import tensorflow

# # +
# # + tags=["same_step_2"]
# import pytorch
# `

# 	TWO_STEPS_COMBINE = `
# # ---

# # + tags=["parameters"]
# foo = "bar"

# # +
# # + tags=["same_step_1"]
# import tensorflow

# # +
# # + tags=["same_step_1"]
# import numpy

# # +
# # + tags=["same_step_2"]
# import pytorch
# `

# 	TWO_STEPS_COMBINE_NO_PARAMS = `
# # +
# # + tags=["same_step_1"]
# import tensorflow

# # +
# # + tags=["same_step_1"]
# import numpy

# # +
# # + tags=["same_step_2"]
# import pytorch
# `

# 	NOTEBOOKS_WITH_IMPORT = `
# # ---
# # jupyter:
# #   jupytext:
# #     text_representation:
# #       extension: .py
# #       format_name: light
# #       format_version: '1.5'
# #       jupytext_version: 1.11.1
# #   kernelspec:
# #     display_name: Python 3
# #     language: python
# #     name: python3
# # ---

# # + tags=["parameters"]
# foo = "bar"
# num = 17

# # +
# import tensorflow

# a = 4

# # +
# from IPython.display import Image

# b = a + 5

# url = 'https://same-project.github.io/SAME-samples/automated_notebook/FaroeIslands.jpeg'

# from IPython import display`
# )
