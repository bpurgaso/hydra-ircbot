'''
Created on Feb 1, 2013

@author: bpurgaso
'''


import yaml
import threading
import signal
from ConfigManager import ConfigManager
from subprocess import Popen, STDOUT, PIPE
from Authenticator import Authenticator


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

    def __init__(self, bot, command, timeout, user, channel, postToIRC):
        threading.Thread.__init__(self)
        self.command = command
        self.timeout = timeout
        self.postToIRC = postToIRC
        self.channel = channel
        self.bot = bot

    def run(self):
        ew = externalWorker(self.command, self.timeout)
        ew.daemon = True
        self.results = ew.startWithTimeout()

        if self.postToIRC:
            self.bot.postToIRC(self.channel, self.results)
        else:
            return self.results


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

    def __init__(self, configManager, auth):
        '''
        Constructor
        '''
        self.configManager = configManager         # Source of truth
        self.configManager.registerListener(self)  # reg for config updates
        self.auth = auth                           # Source of Authority
        self.reloadConfig()            # Load Config

    def reloadConfig(self):
        print "Executor:  Reloading Config"
        self.config = self.configManager.getConfig()

    def invokeCommand(self, bot, command, user, channel, params,\
                                                     postToIRC=True):
        '''
         - Make Executor the only entry-point when executing command
         - be sure to set demon status
         - Executor always checks with Authenticator before running a command
         - Executor reacts differently based on Authenticator's response
         - Executor needs a method call to allow it to send back to the invoker
        '''
        if self.auth.isUserAuthorized(command, user):
            watchDogTmp = watchDogWorker(bot, 'python ./bin/%s.py %s' % (\
                command, params), self.config['commands'][command]['timeout'],\
                                user, channel, postToIRC)
            watchDogTmp.daemon = True
            watchDogTmp.start()
        elif not postToIRC:  # If unauthorized and not posting to IRC channel
            return ['UNAUTHORIZED']
        else:                # If authorized and we are posting to IRC channel
            bot.postToIRC(channel, ['UNAUTHORIZED'])
