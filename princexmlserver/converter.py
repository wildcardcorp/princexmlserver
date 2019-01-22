import os
import shutil
import subprocess
from logging import getLogger
from tempfile import mkdtemp

logger = getLogger('princexmlserver')


class PrinceSubProcess(object):
    default_paths = ['/bin', '/usr/bin', '/usr/local/bin']
    bin_name = 'prince'

    if os.name == 'nt':
        close_fds = False
    else:
        close_fds = True

    def __init__(self):
        binary = self._findbinary()
        self.binary = binary
        if binary is None:
            raise IOError("Unable to find %s binary" % self.bin_name)

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

    def _run_command(self, cmd):
        if isinstance(cmd, str):
            cmd = cmd.split()
        cmdformatted = ' '.join(cmd)
        logger.info("Running command %s" % cmdformatted)
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, close_fds=self.close_fds)
        output, error = process.communicate()
        process.stdout.close()
        process.stderr.close()
        if process.returncode != 0:
            error = """Command
%s
finished with return code
%i
and output:
%s
%s""" % (
                cmdformatted, process.returncode,
                output.decode('utf-8'), error.decode('utf-8'))
            logger.info(error)
            raise Exception(error)
        logger.info("Finished Running Command %s" % cmdformatted)
        return output

    def create_pdf(self, html, css, doctype='html'):
        basepath = mkdtemp()
        xmlpath = os.path.join(basepath, 'index.html')
        with open(xmlpath, 'w') as fi:
            fi.write(html)
        cmd = [self.binary, xmlpath, '-i %s' % doctype]
        for idx, data in enumerate(css):
            csspath = os.path.join(basepath, '%i.css' % idx)
            with open(csspath, 'w') as fi:
                fi.write(data)
            cmd.append("-s %s" % csspath)
        outputpath = os.path.join(basepath, 'output.pdf')
        cmd.append('-o %s' % outputpath)
        self._run_command(cmd)
        with open(outputpath, 'rb') as fi:
            data = fi.read()
        shutil.rmtree(basepath)
        return data


try:
    prince = PrinceSubProcess()
except IOError:
    raise Exception("Error, no prince installation found.")
