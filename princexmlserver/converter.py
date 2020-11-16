import os
import shutil
import subprocess
from logging import getLogger
from tempfile import mkdtemp

logger = getLogger('princexmlserver')


class PrinceSubProcess(object):
    default_paths = ['/bin', '/usr/bin', '/usr/local/bin']
    bin_name = 'prince'
    basepath = None

    if os.name == 'nt':
        close_fds = False
    else:
        close_fds = True

    def __init__(self):
        binary = self._findbinary()
        self.binary = binary
        if binary is None:
            raise IOError(f'Unable to find {self.bin_name} binary')

    def _parse_static_resources(self, static_list, static_type):
        cmd_addition = []
        flag = '--script' if static_type == 'js' else '--style'
        for index, data in enumerate(static_list):
            path = self._get_path(f'{index}.{static_type}')
            with open(path, 'w') as file:
                file.write(data)
            cmd_addition += [f'{flag}={path}']
        return (locals().get('path', None), cmd_addition)

    def _get_path(self, filename):
        if self.basepath is None:
            return
        return os.path.join(self.basepath, filename)

    def _notify_error(self, cmdformatted, process, output, error):
        error = f"""Command
{cmdformatted}
finished with return code
{process.returncode}
and output:
{output.decode('utf-8')}
{error.decode('utf-8')}"""
        logger.error(error)
        raise Exception(error)

    def _findbinary(self):
        if 'PRINCE' in os.environ:
            return os.environ['PRINCE']
        if 'PATH' in os.environ:
            path = os.environ['PATH']
            path = path.split(os.pathsep)
        else:
            path = self.default_paths
        for dir in path:
            fullname = os.path.join(dir, self.bin_name)
            if os.path.exists(fullname):
                return fullname
        return None

    def _run_command(
        self,
        cmd,
        outputpath=None,
        script_file=None,
        final_pass=True,
    ):
        # if isinstance(cmd, str):
        #     cmd = cmd.split()
        if final_pass:
            cmd += [f'--output={outputpath}']
        cmdformatted = ' '.join(cmd)
        logger.info(f'Running command {cmdformatted}')
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, close_fds=self.close_fds)
        output, error = process.communicate()
        process.stdout.close()
        process.stderr.close()
        if process.returncode != 0:
            self._notify_error(cmdformatted, process, output, error)
        logger.info(f'Finished Running Command {cmdformatted}')
        if os.path.exists(outputpath):
            return output
        if error:
            if error.startswith(b'prince: error: page count greater than 1'):
                with open(script_file, 'a+') as file:
                    file.write('quarterInchPageHeight++;\n')
        else:
            final_pass = True
        return self._run_command(
            cmd,
            outputpath=outputpath,
            script_file=script_file,
            final_pass=final_pass,
        )

    def create_pdf(
        self, 
        html,
        css=[],
        js=[],
        doctype='html',
        enable_javascript=False
    ):
        self.basepath = mkdtemp()
        xmlpath = self._get_path('index.html')
        outputpath = self._get_path('output.pdf')
        
        with open(xmlpath, 'w') as xml_file:
            xml_file.write(html)
        
        cmd = [
            self.binary,
            xmlpath,
            f'--input={doctype}',
            '--media=print',
        ]

        js_path, js_commands = self._parse_static_resources(js, 'js')
        _, css_commands = self._parse_static_resources(css, 'css')
        cmd += js_commands + css_commands
        
        if enable_javascript:
            cmd += ['--javascript']

        self._run_command(
            cmd,
            outputpath=outputpath,
            script_file=js_path,
            final_pass=(not js and not enable_javascript),
        )
        with open(outputpath, 'rb') as outfile:
            data = outfile.read()
        shutil.rmtree(self.basepath)
        self.basepath = None
        return data


try:
    prince = PrinceSubProcess()
except IOError:
    raise Exception('Error, no prince installation found.')
