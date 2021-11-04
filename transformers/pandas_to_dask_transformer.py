from typing import Any, Optional
from .context import Step
from .transformer import Transformer
import ast
import astor
import dask.dataframe
import inspect


class PandasToDaskTransformer(ast.NodeTransformer, Transformer):
    def __init__(
        self,
        user_namespace: Optional[dict] = None,
        global_namespace: Optional[dict] = None
    ):
        super().__init__()
        self.user_namespace = user_namespace if user_namespace is not None else {}
        self.global_namespace = global_namespace if global_namespace is not None else {}
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

    def _get_val_from_namespaces(self, id: str) -> Any:
        """
        Get the object associated to a particular key from user/global namespaces.
        Preference is given to user namespace.
        Returns None if an object is not found in either namespace.
        """
        # Look up the value for the variable from the user namespace
        val_from_namespace = self.user_namespace.get(id, None)
        if val_from_namespace is None:
            # If not found, look up the value for the variable from the global namespace
            val_from_namespace = self.global_namespace.get(id, None)
        return val_from_namespace

    def _is_one_to_one_mapping_valid(self, node: ast.AST) -> bool:
        """
        Checks if it is valid to convert the given function call from Pandas to Dask.
        """
        attr = node.func.attr
        id = node.func.value.id
        if attr not in self._pandas_to_dask_functions:
            return False
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

    def _is_compute_required(self, node: ast.AST) -> bool:
        """
        Checks if the Pandas operation being performed requires .compute() when translated to Dask.
        """
        attr = node.func.attr
        id = node.func.value.id
        if attr not in self._pandas_to_dask_with_compute_functions:
            return False
        val_from_namespace = self._get_val_from_namespaces(id)
        if val_from_namespace is None:
            return False
        if not isinstance(val_from_namespace, dask.dataframe.core.DataFrame):
            return False
        return True

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

    def visit_Call(self, node: ast.Call) -> ast.Call:
        """
        Visit (and translate, if applicable) the Call nodes in the AST.
        """
        translated_node = self._try_translate(node)
        if translated_node is not None:
            # Translation resulted in updating the node, so replace it
            return translated_node
        # No translation happened, keep the original node
        return node

    def transform_step(self, step: Step) -> None:
        """
        Transform a given Step's source code into a semantically equivalent source code such that all supported Pandas
        operations are replaced by equivalent Dask operations.
        Note: The transformation is applied to the input Step.
        Example:
            1) pd.read_csv   -->  dd.read_csv
            2) x = df.sum()  -->  x = df.sum().compute()
        """
        super().transform_step(step)
        # Parse the code into its AST
        tree = ast.parse(step.code)
        # Run the transformation
        updated_tree = self.visit(tree)
        # Update node locations in the tree after potential changes due to transformation
        ast.fix_missing_locations(updated_tree)
        # Add any import statements that are required after transformation
        self.perform_imports(updated_tree)
        # Convert back the AST into source code
        updated_code = astor.to_source(updated_tree)
        # Update the source code in the Step
        step.code = updated_code
        # Update the packages required for the Step
        for package in self._required_imports.keys():
            if package not in step.packages_to_install:
                step.packages_to_install.append(package)
