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


class watchDogWorker(threading.Thread):
    '''
    watchDog thread, launches secondary timeout enabling thread
    '''

    def __init__(self, command, timeout):
        threading.Thread.__init__(self)
        self.command = command
        self.timeout = timeout

    def run(self):
        ew = externalWorker(self.command, self.timeout)
        ew.daemon = True
        self.results = ew.startWithTimeout()

        #call back to the Executor and invoke some method to send results back


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

        return self.results

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
         - Executor needs a method call to allow it to send back to the invoker
        '''

'''
Dummy code below
'''
if __name__ == '__main__':
    ew1 = watchDogWorker('echo hello world', 2)
    ew2 = watchDogWorker('sleep 18', 2)
    ew3 = watchDogWorker('echo hello world3', 2)
    ew1.start()
    ew2.start()
    ew3.start()

    ew1.join()
    print ew1.results
    ew3.join()
    print ew3.results
    ew2.join()
    print ew2.results
