class ExecutionEnvironment:
    """
    Environment for executing code in.
    This includes the namespaces, imports etc.
    TODO: Add imports.
    TODO: Add ability to update namespaces and serialize only diffs.
    """
    def __init__(self, global_namespace : dict = {}, local_namespace : dict = {}):
        self.global_namespace = global_namespace
        self.local_namespace = local_namespace

    @property
    def global_namespace(self) -> dict:
        return self._global_namespace

    @global_namespace.setter
    def global_namespace(self, global_namespace: dict):
        self._global_namespace = global_namespace

    @property
    def local_namespace(self) -> dict:
        return self._local_namespace

    @local_namespace.setter
    def local_namespace(self, local_namespace: dict):
        self._local_namespace = local_namespace
