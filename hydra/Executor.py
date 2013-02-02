'''
Created on Feb 1, 2013

@author: bpurgaso
'''


import yaml
import threading
from subprocess import Popen, STDOUT, PIPE


class externalWorker(threading.thread):
    '''
    External script executing threads
    '''

    def __init__(self, command):
        threading.Thread.__init__(self)
        self.suffix = ' 2> /dev/null'
        self.command = command

    def run(self):
        self.__shellCall(self.command + self.suffix)

    def __shellCall(self, command):
        p = Popen(
            command,
            stderr=STDOUT,
            stdout=PIPE,
            close_fds=True,
            shell=True)
        out, err = p.communicate()  # @UnusedVariable
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
        #needs timeout functionality... perhaps in workerThread
