from objects.execution_environment import ExecutionEnvironment
from .context import PandasToDaskTransformer
from .context import Step


class TestPandasToDaskTransformer:
    def test_read_csv(self):
        """
        Transform pandas.read_csv into dask.dataframe.read_csv.
        This is a 1:1 mapping where the calls to pandas module are replaced with dask.dataframe module.
        """
        test_csv_input_path = "test/transformers/testdata/table1.csv"
        # Before transformation, the namespaces need to have the imported modules
        pre_transform_code = """import pandas as pd"""
        env : ExecutionEnvironment = ExecutionEnvironment()
        exec(pre_transform_code, env.global_namespace, env.local_namespace)
        # Transform the use of Pandas to Dask
        transform_code = f"""df = pd.read_csv('{test_csv_input_path}')
print(df)
"""
        step = Step(code=transform_code)
        transformer = PandasToDaskTransformer(env)
        transformer.transform_step(step)
        # Verify that the transformed code includes the Dask DataFrame and replaced the use of Pandas with Dask
        expected_code = f"""import dask.dataframe as dd
df = dd.read_csv('{test_csv_input_path}')
print(df)
"""
        assert expected_code == step.code
        assert 1 == len(step.packages_to_install)
        assert ['dask.dataframe'] == step.packages_to_install

    def test_sum(self):
        """
        Transform df.sum() on a Pandas DataFrame into a df.sum().compute() on a Dask DataFrame.
        """
        test_csv_input_path = "test/transformers/testdata/table1.csv"
        # Before transformation, the namespaces need to have the imported modules
        pre_transform_code = """import pandas as pd"""
        env : ExecutionEnvironment = ExecutionEnvironment()
        exec(pre_transform_code, env.global_namespace, env.local_namespace)
        # Transform the use of Pandas to Dask
        transform_code = f"""
df = pd.read_csv('{test_csv_input_path}')
"""
        step_1 = Step(code=transform_code)
        transformer = PandasToDaskTransformer(env)
        transformer.transform_step(step_1)
        # Verify that the transformed code includes the Dask DataFrame and replaced the use of Pandas with Dask
        expected_code = f"""import dask.dataframe as dd
df = dd.read_csv('{test_csv_input_path}')
"""
        assert expected_code == step_1.code
        assert 1 == len(step_1.packages_to_install)
        assert ['dask.dataframe'] == step_1.packages_to_install
        # Execute the translated code so that the df variable is in the namespaces
        exec(step_1.code, env.global_namespace, env.local_namespace)
        # Transform again so the Pandas sum() is replaced with Dask sum().compute()
        transform_code = """x = df.sum()
print(x)
"""
        step_2 = Step(code=transform_code)
        transformer = PandasToDaskTransformer(env)
        transformer.transform_step(step_2)
        # Verify that sum() is now replaced with sum().compute()
        expected_code = """x = df.sum().compute()
print(x)
"""
        assert expected_code == step_2.code
        assert 0 == len(step_2.packages_to_install)

    def test_no_translation_sum_call(self):
        """
        Since we transform Pandas sum(), make sure that non-Pandas sum() is not transformed.
        """
        pre_transform_code = """x = [1, 2]"""
        env : ExecutionEnvironment = ExecutionEnvironment()
        exec(pre_transform_code, env.global_namespace, env.local_namespace)
        transform_code = """y = sum(x)
print(y)
"""
        step = Step(code=transform_code)
        transformer = PandasToDaskTransformer(env)
        transformer.transform_step(step)
        # There should be no difference (no transformation should happen)
        expected_code = transform_code
        assert expected_code == step.code
        assert 0 == len(step.packages_to_install)

    def test_no_translation_sum_attribute(self):
        """
        Since we transform Pandas sum(), make sure that non-Pandas sum() is not transformed.
        """
        pre_transform_code = """class MyList:

    def __init__(self, lst):
        self.lst = lst

    def sum(self):
        return sum(self.lst)


x = MyList([1, 2])
        """
        env : ExecutionEnvironment = ExecutionEnvironment()
        exec(pre_transform_code, env.global_namespace, env.local_namespace)
        transform_code = """y = x.sum()
print(y)
"""
        step = Step(code=transform_code)
        transformer = PandasToDaskTransformer(env)
        transformer.transform_step(step)
        # There should be no difference (no transformation should happen)
        expected_code = transform_code
        assert expected_code == step.code
        assert 0 == len(step.packages_to_install)
