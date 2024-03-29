# Copyright 2023 Wildcard Corp.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os
import shutil
import subprocess
from tempfile import mkdtemp

logger = logging.getLogger('princexmlserver')


class PrinceSubProcess(object):
    default_paths = ['/bin', '/usr/bin', '/usr/local/bin']
    bin_name = 'prince'
    close_fds = os.name != 'nt'

    def __init__(self):
        self.binary = self._findbinary()
        if self.binary is None:
            raise IOError(f'Unable to find {self.bin_name} binary')
        logging.info(f"selected `{self.binary}`")
        proc = subprocess.run([self.binary, "--version"], capture_output=True)
        logging.info(proc.stdout.decode('utf-8').replace("\\n", "\n"))

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
        logger.debug(f'Running command `{formatted_command}`')
        logger.debug(html)
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
        logger.info(f'Finished Running Command `{formatted_command}`')
        return output

    def create_pdf(self, html, css, additional_args={}):
        doctype = additional_args.get('doctype', 'html')
        pdf_profile = additional_args.get('pdf_profile', 'PDF/UA-1')
        pdf_lang = additional_args.get('pdf_lang', 'en')
        pdf_title = additional_args.get('pdf_title', None)
        pdf_subject = additional_args.get('pdf_subject', None)
        pdf_author = additional_args.get('pdf_author', None)
        pdf_keywords = additional_args.get('pdf_keywords', None)
        pdf_creator = additional_args.get('pdf_creator', None)
        temp_directory = mkdtemp()
        logger.info(f"using tmp dir `{temp_directory}`")
        command = [
            self.binary,
            '-',
            f'--input={doctype}',
            f'--pdf-profile={pdf_profile}',
            f'--pdf-lang={pdf_lang}',
        ]
        if pdf_title is not None:
            command.append(f'--pdf-title={pdf_title}')
        if pdf_subject is not None:
            command.append(f'--pdf-subject={pdf_subject}')
        if pdf_author is not None:
            command.append(f'--pdf-author={pdf_author}')
        if pdf_keywords is not None:
            command.append(f'--pdf-keywords={pdf_keywords}')
        if pdf_creator is not None:
            command.append(f'--pdf-creator={pdf_creator}')

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
