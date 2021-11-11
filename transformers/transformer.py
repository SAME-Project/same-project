from typing import Any, Optional
from .context import Step
from .context import ExecutionEnvironment
from abc import ABC, abstractclassmethod
import ast
import astor
import logging


class Transformer(ABC):
    """
    TODO: Make this an abstract class and decorate methods accordingly.
    TODO: Have a pre and post method call decorator after the transformation.
    """
    def __init__(self, env: Optional[ExecutionEnvironment] = None):
        self._required_imports = {}
        self.env : ExecutionEnvironment = env if env is not None else ExecutionEnvironment()

    def perform_imports(self, ast_root_node: ast.AST):
        for import_name, import_asname in self._required_imports.items():
            import_node = ast.Import(names=[ast.alias(name=import_name, asname=import_asname)])
            ast_root_node.body.insert(0, import_node)
        ast.fix_missing_locations(ast_root_node)

    def _get_val_from_namespaces(self, id: str) -> Any:
        """
        Get the object associated to a particular key from user/global namespaces.
        Preference is given to local namespace.
        Returns None if an object is not found in either namespace.
        """
        # Look up the value for the variable from the user namespace
        val_from_namespace = self.env.local_namespace.get(id, None)
        if val_from_namespace is None:
            # If not found, look up the value for the variable from the global namespace
            val_from_namespace = self.env.global_namespace.get(id, None)
        return val_from_namespace

    @abstractclassmethod
    def _try_translate(self, node: ast.AST) -> Optional[ast.AST]:
        pass

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
        Transform a given Step's source code into a semantically equivalent source code such that all supported numpy
        operations are replaced by equivalent NumS operations.
        Note: The transformation is applied to the input Step.
        Example:
            1) np.array      -->  nps.array
        """
        logging.debug(f'Original step: {step}')
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
        logging.debug(f'Transformed step: {step}')
