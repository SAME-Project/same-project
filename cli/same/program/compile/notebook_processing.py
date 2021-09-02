def get_pipeline_path(same_config_file):
    """Returns absolute value of the pipeline path relative to current file execution"""
    return same_config_file['pipeline']['package']
