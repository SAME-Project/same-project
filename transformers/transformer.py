from .context import Step
import ast


class Transformer:
    """
    TODO: Make this an abstract class and decorate methods accordingly.
    """
    def __init__(self):
        self._required_imports = {}

    def transform_step(self, step: Step) -> Step:
        pass

    def perform_imports(self, ast_root_node):
        # TODO annotate
        for import_name, import_asname in self._required_imports.items():
            import_node = ast.Import(names=[ast.alias(name=import_name, asname=import_asname)])
            ast_root_node.body.insert(0, import_node)
        ast.fix_missing_locations(ast_root_node)
