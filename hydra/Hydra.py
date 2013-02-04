'''
Created on Feb 3, 2013

@author: bpurgaso
'''

from twisted.words.protocols import irc
from twisted.internet import protocol
from twisted.internet import reactor
import time
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
        '''
        Called whenever an inbound message arrives
        '''
        print user, channel, msg
        user = user.rsplit('!', 1)[0]

    # Check to see if they're sending me a private message
        if channel == self.nickname:
            self.msg(user, "I've read your pm and ignored it.")
            return

        # Otherwise check to see if it is a message directed at me
        if msg.startswith(self.nickname + ":"):
            '''
            embedded commands go here
            '''
            #OPME
            if msg.rsplit()[1] == 'opme':
                if self.auth.isUserAuthorized('opme', user):
                    self.mode(channel, set, 'o', None, user)
                else:
                    self.msg(channel, "You aren't authorized for opme.")

            #HELP
            elif msg.rsplit()[1] == 'help':
                if self.auth.isUserAuthorized('help', user):
                    for i in self.auth.getAvailableCommandsForUser(user):
                        self.msg(channel, '%s:  %s' %\
                                 (i, self.auth.getHelpForCommand(i)))
                        time.sleep(self.config['msg_delay'])
                else:
                    self.msg(channel, "You aren't authorized for help.")

            #RELOAD
            elif msg.rsplit()[1] == 'reload':
                if self.auth.isUserAuthorized('reload', user):
                    self.configManager.reload()
                    self.msg(channel, "Configuration Reloaded")
                    if not self.auth.sanityCheck(False):
                        self.msg(channel, "Configuration Sanity is suspect, "\
                         "rolling back.")
                else:
                    self.msg(channel, "You aren't authorized for reload.")

            #KICK
            elif msg.rsplit()[1] == 'kick':
                if self.auth.isUserAuthorized('kick', user):
                    if self.nickname not in msg.rsplit()[2:]:
                        for i in msg.rsplit()[2:]:
                            self.kick(channel, i, 'Later broseph.')
                    else:
                        self.msg(channel, "Nope, not happening.")
                else:
                    self.kick(channel, user, 'Sorry bro, nothing personal.')
            else:
                '''
                External script execution goes here
                '''
                if self.auth.isUserAuthorized(msg.rsplit()[1], user):
                    #kick off the async call
                    self.executor.invokeCommand(self, msg.rsplit()[1], user,\
                                channel, " ".join(msg.rsplit()[2:]), True)
                else:
                    self.msg(channel, "You aren't authorized for %s." %\
                             (msg.rsplit()[1]))
        else:
            '''
            filter processing go here
            '''
            pass

    def postToIRC(self, channel, lst):
        for i in lst:
            self.msg(channel, i)
            time.sleep(self.config['msg_delay'])
        reactor.run()  # @UndefinedVariable


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
        reactor.run()                # @UndefinedVariable

    def reloadConfig(self):
        self.config = self.configManager.getConfig()

### dummy code below
h = Hydra()
