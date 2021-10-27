from .context import PandasToDaskTransformer
from .context import Step


class TestPandasToDaskTransformer:
    def test_read_csv(self):
        test_csv_input_path = "testdata/table1.csv"

        code = f"""
import pandas as pd
df = pd.read_csv('{test_csv_input_path}')
print(df)
        """

        input_step = Step(code=code)
        transformer = PandasToDaskTransformer()
        updated_step = transformer.transform_step(input_step)

        expected_code = f"""
import dask.dataframe as dd
import pandas as pd
df = dd.read_csv('{test_csv_input_path}')
print(df)
        """

        assert expected_code == updated_step.code
        # TODO assert for imports
