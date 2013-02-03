'''
Created on Feb 3, 2013

@author: bpurgaso
'''

from twisted.words.protocols import irc
from twisted.internet import protocol
from twisted.internet import reactor
import time
from datetime import datetime
from ConfigManager import ConfigManager
from Authenticator import Authenticator
from Executor import Executor


class Hydra(object):
    '''
    The big bad scary bot
    '''

    def __init__(self):
        self.configManager = ConfigManager()
        self.config = self.configManager.getConfig()
        self.configManager.registerListener(self)
        self.auth = Authenticator(self.configManager)
        self.executor = Executor(self.configManager, self.auth)

    def reloadConfig(self):
        self.config = self.configManager.getConfig()

### dummy code below
h = Hydra()
