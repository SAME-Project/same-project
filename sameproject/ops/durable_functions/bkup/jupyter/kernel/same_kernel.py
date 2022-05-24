from __future__ import print_function
from context import Step
from clients.durable_functions_client import DurableFunctionsClient
from metakernel import MetaKernel
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
    _same_client = None

    @property
    def same_client(self):
        if self._same_client:
            return self._same_client
        backend_host = "http://localhost:7071"
        user = "gochaudh"
        start_state_id = 0
        self._same_client = DurableFunctionsClient(backend_host, user, start_state_id)
        return self._same_client

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
        code_stripped = code.strip()
        step : Step = Step(code=code_stripped)
        steps = [step]
        outputs = self.same_client.execute_steps(steps)
        assert len(outputs) == 1
        output = outputs[0]
        result = output["result"]
        stdout = result["stdout"]
        stderr = result["stderr"]
        exec_result = result["exec_result"]
        if stdout and stdout != "":
            print(stdout)
        if exec_result and exec_result != "":
            print(exec_result)
        if stderr and stderr != "":
            print(stderr, file=sys.stderr)
        # TODO: Do this in DEBUG mode only.
        print(result)
        return exec_result

    def get_completions(self, info):
        python_magic = self.line_magics['python']
        return python_magic.get_completions(info)

    def get_kernel_help_on(self, info, level=0, none_on_fail=False):
        python_magic = self.line_magics['python']
        return python_magic.get_help_on(info, level, none_on_fail)


if __name__ == '__main__':
    SAMEKernel.run_as_main()
