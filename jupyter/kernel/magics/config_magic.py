from metakernel import Magic


class ConfigMagic(Magic):
    def line_config(self, line):
        self._handle_magic(line)

    def cell_config(self, line):
        self._handle_magic(line)

    def _print_error(self, line, exception):
        self.kernel.Error(f"Config failed: {line} - {exception}")

    def _handle_magic(self, line):
        try:
            self._handle_magic_core(line)
        except Exception as exception:
            self._print_error(line, exception)

    def _handle_magic_core(self, line):
        tokens = line.split(' ')
        command = tokens[0]
        if command == "debug":
            arg = tokens[1]
            if arg == "enable":
                self.kernel.debug_mode = True
            elif arg == "disable":
                self.kernel.debug_mode = False
            else:
                raise Exception(f"Unknown arg: {arg}")
        elif command == "user":
            arg = tokens[1]
            if arg == "set":
                user = tokens[2]
                self.kernel.set_user(user)
            elif arg == "get":
                self.kernel.logger.log(f"Current user is: {self.kernel.get_user()}")
            else:
                raise Exception(f"Unknown arg: {arg}")
        elif command == "state":
            arg = tokens[1]
            if arg == "set":
                state_str = tokens[2]
                state = int(state_str)
                self.kernel.set_next_state_id(state)
            elif arg == "get":
                self.kernel.logger.log(f"Next state ID is: {self.kernel.get_next_state_id()}")
            else:
                raise Exception(f"Unknown arg: {arg}")
        elif command == "host":
            arg = tokens[1]
            if arg == "set":
                host = tokens[2]
                self.kernel.set_backend_host(host)
            elif arg == "get":
                self.kernel.logger.log(f"Backend URL: {self.kernel.get_backend_host()}")
            else:
                raise Exception(f"Unknown arg: {arg}")
        else:
            raise Exception(f"Invalid command: {command}")


def register_magics(kernel):
    kernel.register_magics(ConfigMagic)


def register_ipython_magics():
    from metakernel import IPythonKernel
    from metakernel.utils import add_docs
    from IPython.core.magic import register_line_magic, register_cell_magic
    kernel = IPythonKernel()
    magic = ConfigMagic(kernel)
    # Make magics callable:
    kernel.line_magics["config"] = magic
    kernel.cell_magics["config"] = magic

    @register_line_magic
    @add_docs(magic.line_config.__doc__)
    def config(line):
        kernel.call_magic("%config " + line)

    @register_cell_magic
    @add_docs(magic.cell_config.__doc__)
    def config(line, cell):
        magic.code = cell
        magic.cell_config(line)
