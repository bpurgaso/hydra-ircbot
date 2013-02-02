'''
Created on Feb 1, 2013

@author: bpurgaso
'''


import yaml
import threading
import signal
from subprocess import Popen, STDOUT, PIPE


'''
Timeout Infrastructure
'''


class TimeoutException(Exception):
    '''
    A custom exception we can throw, it doesn't need to do any work.
    It just has to be throwable to break a try-except block.
    '''
    pass


class externalWorker(threading.Thread):
    '''
    External script executing threads
    '''

    def __init__(self, command, timeout):
        threading.Thread.__init__(self)
        self.prefix = 'exec '
        self.suffix = ' 2> /dev/null'
        self.command = command
        self.timeout = timeout
        self.default = 'Command %s, timed out at %s seconds.' % \
        (command, timeout)

    def startWithTimeout(self):
        self.start()
        self.join(self.timeout)
        if self.is_alive():
            self.p.kill()
            self.results = ['TIMEOUT']
        else:
            self.results = self.tmp

    def run(self):
        self.tmp = self.__shellCall(self.prefix + self.command + self.suffix)

    def __shellCall(self, command):
        self.p = Popen(
            command,
            stderr=STDOUT,
            stdout=PIPE,
            close_fds=True,
            shell=True)
        out, err = self.p.communicate()  # @UnusedVariable
        return out.splitlines()


class Executor(object):
    '''
    classdocs
    '''

    def __init__(self, auth):
        '''
        Constructor
        '''
        self.auth = auth  # Source of Authority
        self.conf = self.loadConfigFromDisk()

    def loadConfigFromDisk(self):
        f = open('config.yaml')
        tmp = yaml.load(f)
        f.close()
        return tmp

    def invokeCommand(self, command):
        pass
        '''
         - Make Executor the only entry-point when executing command
         - be sure to set demon status
         - Executor always checks with Authenticator before running a command
         - Executor reacts differently based on Authenticator's response
        '''

'''
Dummy code below
'''
if __name__ == '__main__':
    ew1 = externalWorker('echo hello world', 10)
    ew2 = externalWorker('sleep 18', 2)
    ew1.startWithTimeout()
    print ew1.results

    ew2.startWithTimeout()
    print ew2.results
