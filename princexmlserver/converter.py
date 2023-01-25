import os
import shutil
import subprocess
from logging import getLogger
from tempfile import mkdtemp

logger = getLogger('princexmlserver')


class PrinceSubProcess(object):
    default_paths = ['/bin', '/usr/bin', '/usr/local/bin']
    bin_name = 'prince'
    close_fds = os.name != 'nt'

    def __init__(self):
        self.binary = self._findbinary()
        if self.binary is None:
            raise IOError(f'Unable to find {self.bin_name} binary')

    def _findbinary(self):
        if 'PRINCE' in os.environ:
            return os.environ['PRINCE']
        if 'PATH' in os.environ:
            path = (os.environ['PATH']).split(os.pathsep)
        else:
            path = self.default_paths
        for dir in path:
            fullname = os.path.join(dir, self.bin_name)
            if os.path.exists(fullname):
                return fullname
        return None

    def _run_command(self, command, html):
        if isinstance(command, str):
            command = command.split()
        formatted_command = ' '.join(command)
        logger.info(f'Running command {formatted_command}')
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            close_fds=self.close_fds,
        )
        output, error = process.communicate(html.encode('utf-8'))
        if process.returncode != 0:
            error = f'''Command
{formatted_command}
finished with return code
{process.returncode}
and output:
{output.decode('utf-8')}
{error.decode('utf-8')}'''
            logger.error(error)
            raise Exception(error)
        logger.info(f'Finished Running Command {formatted_command}')
        return output

    def create_pdf(self, html, css, additional_args={}):
        doctype = additional_args.get('doctype', 'html')
        pdf_profile = additional_args.get('pdf_profile', 'PDF/UA-1')
        temp_directory = mkdtemp()
        command = [self.binary, '-', f'--input={doctype}', f'--pdf-profile={pdf_profile}']
        for index, data in enumerate(css):
            css_path = os.path.join(temp_directory, f'{index}.css')
            with open(css_path, 'w') as css_file:
                css_file.write(data)
            command.append(f'--style={css_path}')
        pdf_output = self._run_command(command, html)
        shutil.rmtree(temp_directory)
        return pdf_output


try:
    prince = PrinceSubProcess()
except IOError:
    raise Exception("Error, no prince installation found.")
