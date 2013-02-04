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


class bot(irc.IRCClient):
    """
    irc bots, yay
    """
    def _get_nickname(self):
        return self.factory.nickname
    nickname = property(_get_nickname)

    def reloadConfig(self):
        self.config = self.configManager.getConfig()

    def signedOn(self):
        #Initial Setup
        self.configManager = self.factory.configManager
        self.configManager.registerListener(self)
        self.config = self.configManager.getConfig()
        self.auth = self.factory.auth
        self.executor = self.factory.executor
        print "Signed on as %s." % (self.nickname)
        for i in self.config['channels'].keys():
            if self.config['channels'][i]['autojoin']:
                irc.IRCClient.join(self, i, self.config['channels'][i]['key'])

    def joined(self, channel):
        print "Joined %s." % (channel)

    def privmsg(self, user, channel, msg):
        pass


class botFactory(protocol.ClientFactory):
    """
    Factory for producing "bot"
    """
    protocol = bot

    def __init__(self, channel, configManager, auth, executor):
        self.startChannel = channel
        self.configManager = configManager
        self.config = self.configManager.getConfig()
        self.auth = auth
        self.executor = executor

        #required
        self.nickname = self.config['nick']

    def clientConnectionLost(self, connector, reason):
        print "Lost connection (%s), reconnecting." % (reason)
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "Could not connect:  %s" % (reason)


class Hydra(object):
    '''
    The big bad scary bot
    '''

    def __init__(self):
        self.startChannel = '#hydra'
        self.configManager = ConfigManager()
        self.config = self.configManager.getConfig()
        self.configManager.registerListener(self)
        self.auth = Authenticator(self.configManager)
        self.executor = Executor(self.configManager, self.auth)

        n = self.config['network']
        p = self.config['port']
        b = botFactory(self.startChannel, self.configManager, self.auth,\
                       self.executor)
        reactor.connectTCP(n, p, b)  # @UndefinedVariable
        reactor.run()  # @UndefinedVariable

    def reloadConfig(self):
        self.config = self.configManager.getConfig()

### dummy code below
h = Hydra()
