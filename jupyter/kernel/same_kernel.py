from __future__ import print_function
from context import Step
from context import deserialize_obj
from context import DurableFunctionsClient
from kernel_logger import KernelLogger
from metakernel import MetaKernel
from IPython.core.interactiveshell import InteractiveShell
from six import reraise
import logging
import sys


class SAMEKernel(MetaKernel):
    """
    Kernel implementation to use with Jupyter/IPython for executing code remotely using SAME.
    """
    implementation = 'SAME Python Kernel'
    implementation_version = '1.0'
    language = 'python'
    language_version = '0.1'
    banner = "SAME - Run Python on the SAME backend"
    language_info = {
        'mimetype': 'text/x-python',
        'name': 'python',
        'file_extension': '.py',
        'help_links': MetaKernel.help_links,
    }
    kernel_json = {
        "argv": [
            sys.executable, "-m", "same_kernel", "-f", "{connection_file}"],
        "display_name": "SAME Kernel",
        "language": "python",
        "name": "same_kernel"
    }
    _interactive_shell = None
    _same_client = None
    _logger = None
    _debug_mode = True

    @property
    def debug_mode(self):
        return self._debug_mode

    @debug_mode.setter
    def debug_mode(self, value):
        self._debug_mode = value

    @property
    def interactive_shell(self):
        if self._interactive_shell:
            return self._interactive_shell
        self._interactive_shell = InteractiveShell()
        return self._interactive_shell

    @property
    def same_client(self):
        if self._same_client:
            return self._same_client
        backend_host = "http://localhost:7071"
        user = "default"
        start_state_id = 0
        self._same_client = DurableFunctionsClient(backend_host, user, start_state_id)
        return self._same_client

    @property
    def logger(self):
        if self._logger:
            return self._logger
        self._logger = KernelLogger(prefix='SAME')
        return self._logger

    def get_usage(self):
        return ("This is the SAME Python Kernel")

    def set_variable(self, name, value):
        """
        Set a variable in the kernel language.
        """
        python_magic = self.line_magics['python']
        python_magic.env[name] = value

    def get_variable(self, name):
        """
        Get a variable from the kernel language.
        """
        python_magic = self.line_magics['python']
        return python_magic.env.get(name, None)

    def do_execute_direct(self, code):
        try:
            self._do_execute_direct_core(code)
        except:
            self.interactive_shell.showtraceback()

    def _do_execute_direct_core(self, code):
        code_stripped = code.strip()
        step : Step = Step(code=code_stripped)
        steps = [step]

        outputs = self.same_client.execute_steps(steps)
        self.logger.log(outputs, logging.DEBUG)

        assert len(outputs) == 1
        output = outputs[0]
        result = output["result"]

        status = result["status"]
        if status == "success":
            stdout = result["stdout"]
            stderr = result["stderr"]
            exec_result = result["exec_result"]
            if stdout and stdout != "":
                self.Print(stdout)
            if exec_result and exec_result != "":
                self.Print(exec_result)
            if stderr and stderr != "":
                self.Error(stderr, file=sys.stderr)
        elif status == "fail":
            reason = result["reason"]
            info = result["info"]
            if reason == "exception":
                exception_base64 = info["exception"]
                exception = deserialize_obj(exception_base64)
                if type(exception) is tuple:
                    # This comes from sys.exc_info()
                    exception_tuple = exception
                    exception_class = exception_tuple[0]
                    exception_value = exception_tuple[1]
                    exception_traceback = exception_tuple[2]
                    # TODO clean the stack trace
                    reraise(exception_class, exception_value, exception_traceback)
                else:
                    raise exception
        return exec_result

    def get_completions(self, info):
        python_magic = self.line_magics['python']
        return python_magic.get_completions(info)

    def get_kernel_help_on(self, info, level=0, none_on_fail=False):
        python_magic = self.line_magics['python']
        return python_magic.get_help_on(info, level, none_on_fail)

    def set_user(self, user: str):
        self.same_client.user = user
        self.logger.log(f"Set user to: {user}")

    def set_next_state_id(self, id: int):
        self.same_client.next_state_id = id
        self.logger.log(f"Set next state ID to: {id}")

    def set_backend_host(self, backend_host: str):
        self.same_client.set_workflow_url(backend_host)
        self.logger.log(f"Set backend host to: {backend_host}")

    def get_user(self):
        return self.same_client.user

    def get_next_state_id(self):
        return self.same_client.next_state_id

    def get_backend_host(self):
        return self.same_client.workflow_url


if __name__ == '__main__':
    SAMEKernel.run_as_main()
