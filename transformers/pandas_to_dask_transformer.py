from .context import Step
from .transformer import Transformer
import ast
import astor


class PandasToDaskTransformer(ast.NodeTransformer, Transformer):
    def __init__(self):
        super().__init__()
        # Import statement for Dask
        self._dask_dataframe_import_name = 'dask.dataframe'
        self._dask_dataframe_import_asname = 'dd'
        # Import statement for Pandas
        self._pandas_import_name = 'pandas'
        self._pandas_import_asname = 'pd'
        # Supported Pandas functions that can be 1:1 mapped to Dask
        self._pandas_to_dask_functions = ['read_csv']

    def _import_dask_dataframe(self):
        """
        Import Dask DataFrame into the environment.
        """
        if self._dask_dataframe_import_name not in self._required_imports:
            self._required_imports[self._dask_dataframe_import_name] = self._dask_dataframe_import_asname

    def _is_translation_valid(self, attr, attr_id):
        """
        Checks if it is valid to convert the given function call from Pandas to Dask.
        """
        if attr not in self._pandas_to_dask_functions:
            return False
        if attr_id != self._pandas_import_name and attr_id != self._pandas_import_asname:
            return False
        return True

    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Attribute):
            attr = node.func.attr
            attr_id = node.func.value.id
            if self._is_translation_valid(attr, attr_id):
                self._import_dask_dataframe()
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
                return updated_node
        return node

    def transform_step(self, step: Step) -> None:
        """
        Transform a given Step's source code into a semantically equivalent source code such that all supported Pandas
        operations are replaced by equivalent Dask operations.
        Note: The transformation is applied to the input Step.
        Example:
            pd.read_csv -> dd.read_csv
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
