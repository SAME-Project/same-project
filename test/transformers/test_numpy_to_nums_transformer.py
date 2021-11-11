from .context import ExecutionEnvironment
from .context import NumpyToNumsTransformer
from .context import Step


class TestNumpyToNumsTransformer:
    def test_random(self):
        # Before transformation, the namespaces need to have the imported modules
        pre_transform_code = """import numpy as np"""
        env : ExecutionEnvironment = ExecutionEnvironment()
        exec(pre_transform_code, env.global_namespace, env.local_namespace)
        transform_code = """X1 = np.random.randn(500, 1) + 5.0"""
        env = ExecutionEnvironment()
        step = Step(code=transform_code)
        transformer = NumpyToNumsTransformer(env)
        transformer.transform_step(step)
        expected_code = """import nums.numpy as nps
X1 = nps.random.randn(500, 1) + 5.0
"""
        assert expected_code == step.code
        assert 1 == len(step.packages_to_install)
        assert ['nums.numpy'] == step.packages_to_install

    def test_get(self):
        # Before transformation, the namespaces need to have the imported modules
        pre_transform_code = """import numpy as np"""
        env : ExecutionEnvironment = ExecutionEnvironment()
        exec(pre_transform_code, env.global_namespace, env.local_namespace)
        transform_code = """X1 = np.random.randn(500, 1) + 5.0"""
        env = ExecutionEnvironment()
        step_1 = Step(code=transform_code)
        transformer = NumpyToNumsTransformer(env)
        transformer.transform_step(step_1)
        expected_code = """import nums.numpy as nps
X1 = nps.random.randn(500, 1) + 5.0
"""
        assert expected_code == step_1.code
        assert 1 == len(step_1.packages_to_install)
        assert ['nums.numpy'] == step_1.packages_to_install
        exec(step_1.code, env.global_namespace, env.local_namespace)
        transform_code = """print(X1)
"""
        step_2 = Step(code=transform_code)
        transformer = NumpyToNumsTransformer(env)
        transformer.transform_step(step_2)
        expected_code = """print(X1.get())
"""
        assert expected_code == step_2.code
        assert 0 == len(step_2.packages_to_install)
