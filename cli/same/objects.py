class Step:
    name = "same_step_unset"
    cache_value = "P0D"
    environment_name = "default"
    tags = []
    index = -1  # order of this step
    code = ""
    parameters = []  # additional parameters as part of the function definition
    packages_to_install = {}

    def __init__(self):
        pass
