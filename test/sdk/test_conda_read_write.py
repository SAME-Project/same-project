# from sameproject.sdk.same import CondaEnv, CondaEnvValidator
# from cerberus import SchemaError
# import pytest
# from ruamel.yaml.compat import StringIO
# from pathlib import Path
# from ruamel.yaml import YAML
# from mock import MagicMock

# import os
# import builtins

# conda_env_file_path = "test/testdata/sample_conda_files/complicated_conda.yaml"

# # Test name, Conda File Path, Valid, Error Phrase
# sample_conda_file_paths = [
#     ("Good - Simple Conda File", "test/testdata/sample_conda_files/simple_conda.yaml", True, ""),
#     ("Good - Complicated Conda File", "test/testdata/sample_conda_files/complicated_conda.yaml", True, ""),
#     ("Bad - Unknown field", "test/testdata/sample_conda_files/bad_unknown_conda.yaml", False, "unknown field"),
#     (
#         "Bad - Empty File",
#         "test/testdata/sample_conda_files/bad_empty_conda.yaml",
#         False,
#         "...",
#     ),
# ]


# @pytest.fixture
# def same_config():
#     with open(conda_env_file_path, "rb") as f:
#         return CondaEnv(buffered_reader=f)


# def test_load_same_config_both_set():
#     with pytest.raises(ValueError) as e:
#         # Setting both values should raise error (values don't matter)
#         CondaEnv(buffered_reader=StringIO(), content="NON_EMPTY_STRING")

#     assert "CondaEnv accepts either" in str(e.value)


# def test_bad_config_from_file_buffer(caplog):
#     _, empty_conda_env_file, _, _ = sample_conda_file_paths[3]
#     with pytest.raises(ValueError) as e:
#         with open(empty_conda_env_file, "rb") as f:
#             CondaEnv(buffered_reader=f)

#     assert "is empty" in str(e.value)

#     _, unknown_field_conda_env_file, _, _ = sample_conda_file_paths[2]
#     with pytest.raises(SyntaxError) as e:
#         with open(unknown_field_conda_env_file, "rb") as f:
#             CondaEnv(buffered_reader=f)

#     assert "unknown field" in str(e.value)


# def test_load_same_from_string():
#     with pytest.raises(ValueError) as e:
#         CondaEnv(content="")

#     assert "Content is empty." in str(e.value)

#     _, unknown_field_conda_env_file, _, _ = sample_conda_file_paths[2]

#     with pytest.raises(SyntaxError) as e:
#         with open(unknown_field_conda_env_file, "rb") as f:
#             unknown_field_conda_content = "".join(map(bytes.decode, f.readlines()))

#         CondaEnv(content=unknown_field_conda_content)

#     assert "unknown field" in str(e.value)


# @pytest.mark.skip("Writing environment file from same.import not implemented")
# def test_write_same_file():
#     assert False, "NYI"
#     # Bad path
#     # Bad file


# def test_load_conda_env():
#     same_file_path = Path(conda_env_file_path)
#     assert same_file_path.exists()

#     with open(conda_env_file_path, "rb") as f:
#         same_config_file_contents = CondaEnv(buffered_reader=f)

#     assert same_config_file_contents is not None


# def test_must_have_dependencies():

#     with open(conda_env_file_path, "rb") as f:
#         good_conda_env = CondaEnv(buffered_reader=f)

#     yaml = YAML(typ="safe")

#     try:
#         s = StringIO()
#         yaml.dump(good_conda_env.to_dict(), stream=s)
#         CondaEnv(content=s.getvalue())
#     except SyntaxError as e:
#         assert False, e

#     bad_conda_env = good_conda_env.copy()
#     bad_conda_env.pop("dependencies")

#     with pytest.raises(SyntaxError) as e:
#         s = StringIO()
#         yaml.dump(bad_conda_env.to_dict(), stream=s)
#         CondaEnv(content=s.getvalue())

#     assert "required field" in str(e.value)
#     assert "dependencies" in str(e.value)


# def test_conda_env_schema_compiles():
#     try:
#         v = CondaEnvValidator.get_validator()
#     except SchemaError as e:
#         pytest.fail(f"Schema failed to validate: {e}")

#     assert v is not None


# @pytest.mark.parametrize("test_name, same_config_file_path, valid, error_phrase", sample_conda_file_paths, ids=[p[0] for p in sample_conda_file_paths])
# def test_load_sample_conda_env_configs(caplog, test_name, same_config_file_path, valid, error_phrase):
#     v = CondaEnvValidator.get_validator()
#     try:
#         with open(same_config_file_path, "rb") as f:
#             conda_env_contents = CondaEnv(f)  # noqa
#         assert valid, print(f"Unable to validate conda env config: {v.errors}")
#     except SyntaxError as e:
#         assert not valid, print(f"CondaEnv is invalid, but not detected: {str(e.msg)}")
#         assert error_phrase in str(e.msg)
#     except ValueError:
#         assert not valid, print("CondaEnv is empty but was not detected.")


# def test_e2e_load_conda_env_object(caplog):
#     with open(conda_env_file_path, "rb") as f:
#         conda_env_object = CondaEnv(buffered_reader=f)  # noqa

#     assert conda_env_object.name == "complicated_conda_env"
#     assert len(conda_env_object.channels) == 2
#     assert len(conda_env_object.dependencies) == 6
#     assert "python=3.6" in conda_env_object.dependencies[0]
#     assert conda_env_object.extras.GPU == "A100"


# def test_full_conda_write(caplog, mocker, tmp_path):
#     mocker.patch.object(Path, "write_text")

#     with open(conda_env_file_path, "rb") as f:
#         conda_env_object = CondaEnv(buffered_reader=f)  # noqa

#     conda_env_object.write(tmp_path / "conda.yaml")  # path value is unused because it is mocked

#     written_text = Path.write_text.call_args[0][0]
#     assert isinstance(written_text, str)

#     written_conda_env = CondaEnv(content=written_text)
#     assert written_conda_env is not None
