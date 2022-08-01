from sameproject.ops.runtime_options import register_option

register_option(
    "input_repo",
    "Shortcut for specifying pfs input repo, same as --input='{\"pfs\": {\"repo\": \"images\"}'",
    backend="pachyderm",
)

register_option(
    "input_glob",
    "Shortcut for specifying pfs input glob, same as --input='{\"pfs\": {\"glob\": \"/*\"}'",
    backend="pachyderm",
)

register_option(
    "input",
    "JSON formatted input spec, see 'input' section of "+
        "https://docs.pachyderm.com/latest/reference/pipeline-spec/",
    backend="pachyderm"
)
