from .context import PandasToDaskTransformer
from .context import Step


class TestPandasToDaskTransformer:
    def test_read_csv(self):
        test_csv_input_path = "testdata/table1.csv"

        code = f"""import pandas as pd
df = pd.read_csv('{test_csv_input_path}')
print(df)
"""

        step = Step(code=code)
        transformer = PandasToDaskTransformer()
        transformer.transform_step(step)

        expected_code = f"""import dask.dataframe as dd
import pandas as pd
df = dd.read_csv('{test_csv_input_path}')
print(df)
"""

        assert expected_code == step.code
        assert ['dask.dataframe'] == step.packages_to_install

    def test_sum(self):
        test_csv_input_path = "testdata/table1.csv"

        code = f"""import pandas as pd
df = pd.read_csv('{test_csv_input_path}')
x = df.sum()
print(x)
"""

        step = Step(code=code)
        transformer = PandasToDaskTransformer()
        transformer.transform_step(step)

        expected_code = f"""import dask.dataframe as dd
import pandas as pd
df = dd.read_csv('{test_csv_input_path}')
x = df.sum().compute()
print(x)
"""

        assert expected_code == step.code
        assert ['dask.dataframe'] == step.packages_to_install

    def test_no_translation_sum(self):
        # x = [1,2,3]
        # y = sum(x)
        pass
