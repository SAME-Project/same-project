from typing import Optional
from .context import ExecutionEnvironment
from .transformer import Transformer
import ast
import dask.dataframe
import inspect


class PandasToDaskTransformer(ast.NodeTransformer, Transformer):
    def __init__(
        self,
        env: Optional[ExecutionEnvironment] = None
    ):
        super().__init__(env)
        # Import statement for Dask
        self._dask_dataframe_import_name = 'dask.dataframe'
        self._dask_dataframe_import_asname = 'dd'
        # Import statement for Pandas
        self._pandas_import_name = 'pandas'
        self._pandas_import_asname = 'pd'
        # Supported Pandas functions that can be 1:1 mapped to Dask
        self._pandas_to_dask_functions = ['read_csv']
        # Pandas functions for which we need to call .compute when translated to Dask
        self._pandas_to_dask_with_compute_functions = ['sum']
        # Function call for .compute
        self._dask_compute = 'compute'

    def _import_dask_dataframe(self) -> None:
        """
        Import Dask DataFrame into the environment.
        """
        if self._dask_dataframe_import_name not in self._required_imports:
            self._required_imports[self._dask_dataframe_import_name] = self._dask_dataframe_import_asname

    def _is_one_to_one_mapping_valid(self, node: ast.AST) -> bool:
        """
        Checks if it is valid to convert the given function call from Pandas to Dask.
        """
        if isinstance(node, ast.Call):
            func = node.func
            return self._is_one_to_one_mapping_valid(func)
        elif isinstance(node, ast.Name):
            id = node.id
            if id != self._pandas_import_name and id != self._pandas_import_asname:
                return False
            val_from_namespace = self._get_val_from_namespaces(id)
            if val_from_namespace is None:
                return False
            if not inspect.ismodule(val_from_namespace):
                return False
            if val_from_namespace.__name__ != self._pandas_import_name:
                return False
            return True
        elif isinstance(node, ast.Attribute):
            attr = node.attr
            if attr not in self._pandas_to_dask_functions:
                return False
            return self._is_one_to_one_mapping_valid(node.value)
        return False

    def _is_compute_required(self, node: ast.AST) -> bool:
        """
        Checks if the Pandas operation being performed requires .compute() when translated to Dask.
        """
        if isinstance(node, ast.Call):
            func = node.func
            return self._is_compute_required(func)
        elif isinstance(node, ast.Name):
            id = node.id
            val_from_namespace = self._get_val_from_namespaces(id)
            if val_from_namespace is None:
                return False
            if not isinstance(val_from_namespace, dask.dataframe.core.DataFrame):
                return False
            return True
        elif isinstance(node, ast.Attribute):
            attr = node.attr
            if attr not in self._pandas_to_dask_with_compute_functions:
                return False
            return self._is_compute_required(node.value)
        return False

    def _try_translate(self, node: ast.AST) -> Optional[ast.AST]:
        """
        If the code in the given node requires any translation, it will create an updated node and return that.
        If no translation was performed, it will return None.
        """
        updated_node = None
        if isinstance(node.func, ast.Attribute):
            if self._is_one_to_one_mapping_valid(node):
                updated_node = ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(
                            id=self._dask_dataframe_import_asname,
                            ctx=node.func.value.ctx
                        ),
                        attr=node.func.attr,
                        ctx=node.func.ctx
                    ),
                    args=node.args,
                    keywords=node.keywords
                )
                # Requires importing the dask.dataframe class as we are converting Pandas to Dask dataframe
                self._import_dask_dataframe()
            elif self._is_compute_required(node):
                updated_node = ast.Call(
                    func=ast.Attribute(
                        value=ast.Call(
                            func=ast.Attribute(
                                value=ast.Name(
                                    id=node.func.value.id,
                                    ctx=node.func.ctx
                                ),
                                attr=node.func.attr,
                                ctx=node.func.ctx
                            ),
                            args=node.args,
                            keywords=node.keywords
                        ),
                        attr=self._dask_compute,
                        ctx=node.func.ctx
                    ),
                    args=[],
                    keywords=[]
                )
        return updated_node
