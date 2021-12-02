from logging import exception
from typing import Optional

from nums.core import application_manager
from .context import ExecutionEnvironment
from .transformer import Transformer
from nums.core.array.blockarray import BlockArray
from nums.core import settings
from nums.core.application_manager import instance
import ast
import inspect


class NumpyToNumsTransformer(ast.NodeTransformer, Transformer):
    def __init__(
        self,
        env: Optional[ExecutionEnvironment] = None
    ):
        super().__init__(env)
        # Import statement for NumS
        self._nums_import_name = 'nums.numpy'
        self._nums_import_asname = 'nps'
        # Import statement for numpy
        self._numpy_import_name = 'numpy'
        self._numpy_import_asname = 'np'
        # Supported numpy functions that can be 1:1 mapped to NumS
        self._numpy_to_nums_functions = ['array', 'randn', 'random']
        # numpy functions for which we need to call .compute when translated to NumS
        self._numpy_to_nums_with_compute_functions = ['sum']
        # Function call for .get
        self._nums_get = 'get'
        # NumS app manager that gets configured with user settings and connects to the backend
        self._nums_app_manager = None

    def _setup_nums(self):
        """
        Configure NumS and set the appropriate variables here.
        If not already configured and this resulted in successful configuration, returns True.
        Otherwise returns False.
        """
        if self._nums_app_manager is not None:
            return False

        settings.system_name = "azure_functions"

        # TODO: Hardcoded. Fix.
        c1, c2 = 1, 1
        settings.cluster_shape = (c1, c2)

        # TODO: Hardcoded. Fix.
        exp_config = {}
        exp_config["hosts"] = ["http://localhost:8081"]
        exp_config["exec_config"] = "default"
        exp_config["lb_policy"] = "random"
        exp_config["print_calls"] = False
        exp_config["cache_size_gb"] = 1
        exp_config["num_procs_per_worker"] = 1
        for k, v in exp_config.items():
            settings.azure_functions_system_config[k] = v
        self._nums_app_manager = instance()
        return True

    def _configure_and_import_nums(self) -> None:
        """
        Configure NumS.
        Add the configured NumS into the environment.
        This is only done once.
        """
        if self._setup_nums():
            self._required_imports[self._nums_import_name] = self._nums_import_asname
            self.env.add_to_temporary_global_namespace("nums_app_manager", self._nums_app_manager)

    def __is_one_to_one_mapping_valid_on_name_node(self, node: ast.Name) -> bool:
        id = node.id
        if id != self._numpy_import_name and id != self._numpy_import_asname:
            return False
        val_from_namespace = self._get_val_from_namespaces(id)
        if val_from_namespace is None:
            return False
        if not inspect.ismodule(val_from_namespace):
            return False
        if val_from_namespace.__name__ != self._numpy_import_name:
            return False
        return True

    def _is_one_to_one_mapping_valid(self, node: ast.AST) -> bool:
        """
        Checks if it is valid to convert the given function call from numpy to NumS.
        """
        if isinstance(node, ast.Call):
            func_valid = self._is_one_to_one_mapping_valid(node.func)
            args_valid = any([self._is_one_to_one_mapping_valid(arg) for arg in node.args])
            keywords_valid = any([self._is_one_to_one_mapping_valid(keyword) for keyword in node.keywords])
            return any([func_valid, args_valid, keywords_valid])
        elif isinstance(node, ast.Name):
            return self.__is_one_to_one_mapping_valid_on_name_node(node)
        elif isinstance(node, ast.Attribute):
            attr = node.attr
            if attr not in self._numpy_to_nums_functions:
                return False
            return self._is_one_to_one_mapping_valid(node.value)
        return False

    def __is_get_required_on_name_node(self, node: ast.Name) -> bool:
        id = node.id
        val_from_namespace = self._get_val_from_namespaces(id)
        if val_from_namespace is None:
            return False
        if not isinstance(val_from_namespace, BlockArray):
            return False
        return True

    def _is_get_required(self, node: ast.AST) -> bool:
        """
        Checks if the numpy operation being performed requires .get() when translated to NumS.
        """
        if isinstance(node, ast.Call):
            func = node.func
            func_get_required = self._is_get_required(func)
            args_get_required = any([self._is_get_required(arg) for arg in node.args])
            keywords_get_required = any([self._is_get_required(keyword) for keyword in node.keywords])
            return any([func_get_required, args_get_required, keywords_get_required])
        elif isinstance(node, ast.Name):
            return self.__is_get_required_on_name_node(node)
        elif isinstance(node, ast.Attribute):
            attr = node.attr
            if attr not in self._numpy_to_nums_with_compute_functions:
                return False
            return self._is_get_required(node.value)
        return False

    def _create_updated_compute_required_node(self, node: ast.AST) -> ast.AST:
        """
        TODO: Update docstring.
        TODO: Comments in function.
        Creates an updated node from the given node if any source-to-source translation is applicable.
        Returns the same node if no translation is applicable.
        Recursively does this for relevant child nodes of the given node.
        TODO: When using this, can we remove the usage of _is_get_required and _is_one_to_one_mapping_valid by
        merging all the logic into this?
        """
        if isinstance(node, ast.Call):
            # TODO: Unit test for updating keywords.
            updated_args = []
            updated_keywords = []
            for arg in node.args:
                updated_arg = self._create_updated_compute_required_node(arg)
                updated_args.append(updated_arg)
            for keyword in node.keywords:
                updated_keyword = self._create_updated_compute_required_node(keyword)
                updated_keywords.append(updated_keyword)
            updated_func = self._create_updated_compute_required_node(node.func)
            updated_call_node = ast.Call(
                func=updated_func,
                args=updated_args,
                keywords=updated_keywords
            )
            return updated_call_node
        elif isinstance(node, ast.Name):
            if self.__is_get_required_on_name_node(node):
                updated_node = ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(
                            id=node.id,
                            ctx=ast.Load()
                        ),
                        attr=self._nums_get,
                        ctx=ast.Load()
                    ),
                    args=[],
                    keywords=[]
                )
                return updated_node
        elif isinstance(node, ast.Attribute):
            attr = node.attr
            if attr not in self._numpy_to_nums_with_compute_functions:
                return node
            value = node.value
            # TODO: Can the name be recursively done or node.ctx is required?
            if isinstance(value, ast.Name) and self.__is_get_required_on_name_node(value):
                updated_node = ast.Attribute(
                    value=ast.Call(
                        func=node,
                        args=[],
                        keywords=[]
                    ),
                    attr=self._nums_get,
                    ctx=node.ctx
                )
                return updated_node
        return node

    def _create_updated_one_to_one_mapping_node(self, node: ast.AST) -> ast.AST:
        """
        TODO: Update docstring.
        TODO: Comments in function.
        Creates an updated node from the given node if any source-to-source translation is applicable.
        Returns the same node if no translation is applicable.
        Recursively does this for relevant child nodes of the given node.
        TODO: When using this, can we remove the usage of _is_get_required and _is_one_to_one_mapping_valid by
        merging all the logic into this?
        """
        if isinstance(node, ast.Call):
            # TODO: Unit test for updating keywords.
            updated_func = self._create_updated_one_to_one_mapping_node(node.func)
            updated_args = []
            updated_keywords = []
            for arg in node.args:
                updated_arg = self._create_updated_one_to_one_mapping_node(arg)
                updated_args.append(updated_arg)
            for keyword in node.keywords:
                updated_keyword = self._create_updated_one_to_one_mapping_node(keyword)
                updated_keywords.append(updated_keyword)
            updated_call_node = ast.Call(
                func=updated_func,
                args=updated_args,
                keywords=updated_keywords,
            )
            return updated_call_node
        elif isinstance(node, ast.Name):
            if self.__is_one_to_one_mapping_valid_on_name_node(node):
                updated_name_node = ast.Name(
                    id=self._nums_import_asname,
                    ctx=node.ctx
                )
                return updated_name_node
        elif isinstance(node, ast.Attribute):
            attr = node.attr
            if attr not in self._numpy_to_nums_functions:
                return node
            value = node.value
            updated_value = self._create_updated_one_to_one_mapping_node(value)
            if updated_value != value:
                updated_attribute_node = ast.Attribute(
                    value=updated_value,
                    attr=attr,
                    ctx=node.ctx
                )
                return updated_attribute_node
        return node

    def _try_translate(self, node: ast.AST) -> Optional[ast.AST]:
        """
        If the code in the given node requires any translation, it will create an updated node and return that.
        If no translation was performed, it will return None.
        """
        updated_node = None
        # TODO make this recursive like the above methods - right now the test_random test fails.
        if self._is_one_to_one_mapping_valid(node):
            updated_node = self._create_updated_one_to_one_mapping_node(node)
            # Requires inserting NumS variables into the namespaces before execution.
            self._configure_and_import_nums()
        elif self._is_get_required(node):
            updated_node = self._create_updated_compute_required_node(node)
        return updated_node

    def _resolve_blockarray(self, obj, visited=None):
        if visited is None:
            visited = set()

        addr = id(obj)
        if addr in visited:
            return
        visited.add(addr)

        properties = []
        for a in dir(obj):
            try:
                if not a.startswith('_') and not callable(getattr(obj, a)):
                    properties.append(a)
            except:
                continue

        for property in properties:
            value = getattr(obj, property)
            if isinstance(value, BlockArray):
                resolved_value = value.get()
                setattr(obj, property, resolved_value)
            else:
                self._resolve_blockarray(value, visited)

    def post_process(self):
        """
        """
        for key, value in self.env.global_namespace.items():
            if key in self.env.temporary_entries:
                continue
            # self._resolve_blockarray(value)
        for key, value in self.env.local_namespace.items():
            if key in self.env.temporary_entries:
                continue
            # self._resolve_blockarray(value)
