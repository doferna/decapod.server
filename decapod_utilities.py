import os
import shutil
import subprocess

def mkdirIfNecessary(path):
    if os.path.exists(path) is False:
        os.mkdir(path)

def remakeDir(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.mkdir(path)
    
def invokeCommandSync(cmdArgs, error, message):
    proc = subprocess.Popen(cmdArgs, stdout=subprocess.PIPE)
    output = proc.communicate()[0]
    if proc.returncode != 0:
        print(output)
        raise error, message
    
    return output