'''
Created on Feb 3, 2013

@author: bpurgaso
'''

from twisted.words.protocols import irc
from twisted.internet import protocol
from twisted.internet import reactor
from twisted.internet import threads
from ConfigManager import ConfigManager
from Authenticator import Authenticator
from subprocess import PIPE, STDOUT, Popen


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
        print "Signed on as %s." % (self.nickname)
        for i in self.config['channels'].keys():
            if self.config['channels'][i]['autojoin']:
                irc.IRCClient.join(self, i, self.config['channels'][i]['key'])

    def joined(self, channel):
        print "Joined %s." % (channel)

    def irc_INVITE(self, prefix, params):
        """ called by twisted,
        if the bot was invited
        """

        channel = params[-1].lower().replace('#', '')
        if channel not in self.config['channels'].keys():
            self.auth.createChannelEntry(channel)

        self.join(channel, self.config['channels'][channel]['key'])

    def privmsg(self, user, channel, msg):
        '''
        Called whenever an inbound message arrives
        '''
        print user, channel, msg
        user = user.rsplit('!', 1)[0]

        # Check to see if they're sending me a private message
        if channel == self.nickname:
            channel = user
            index = 0
        else:
            index = 1

        # See if the message directed at me
        if msg.startswith(self.nickname + ":") or index == 0:
            '''
            embedded commands go here
            '''
            command = msg.rsplit()[index].lower()

            #REGISTER
            if command == 'register':
                if self.auth.isUserAuthorized('register', user):
                    self.msg(channel, self.auth.registerUser(user, 'default'))
                else:
                    self.msg(channel, "You aren't authorized for register.")
            #PROMOTE
            elif command == 'promote':
                if self.auth.isUserAuthorized('promote', user):
                    try:
                        target_uname = msg.rsplit()[index + 1].lower()
                        target_group = msg.rsplit()[index + 2].lower()

                        if self.auth.getPowerOfUser(user) <=\
                            self.auth.getPowerOfGroup(target_group):

                            self.postToIRC((channel, [self.auth.registerUser(\
                                                target_uname, target_group)]))
                        else:
                            self.postToIRC((channel, ['%s, your power level'\
                                                      ' is'\
                                                     ' insufficient.' % user]))
                    except:
                        self.postToIRC((channel, ['Check your formatting and'\
                                                 ' try again.']))
                else:
                    self.msg(channel, "You aren't authorized for register.")
            #WHOAMI
            elif command == 'whoami':
                if self.auth.isUserAuthorized('whoami', user):
                    self.postToIRC((channel, [self.auth.whoami(user)]))
                else:
                    self.msg(channel, "You aren't authorized for register.")
            #OPME
            elif command == 'opme':
                if self.auth.isUserAuthorized('opme', user):
                    self.mode(channel, set, 'o', None, user)
                else:
                    self.msg(channel, "You aren't authorized for opme.")
            #AUTOOP
            elif command == 'autoop':
                if self.auth.isUserAuthorized('autoop', user):
                    if msg.rsplit()[2].lower() == 'on':
                        self.postToIRC((channel, self.auth.toggleAutoOp(\
                                                       user, channel, True)))
                    else:
                        self.postToIRC((channel, self.auth.toggleAutoOp(\
                                                        user, channel, False)))
                else:
                    self.msg(channel, "You aren't authorized for autoop.")
            #HELP
            elif command == 'help':
                if self.auth.isUserAuthorized('help', user):
                    for i in self.auth.getAvailableCommandsForUser(user):
                        self.msg(user, '%s:  %s' %\
                                 (i, self.auth.getHelpForCommand(i)))
                    self.msg(channel, 'I\'ve sent you a pm.')
                else:
                    self.msg(channel, "You aren't authorized for help.")
            #RELOAD
            elif command == 'reload':
                if self.auth.isUserAuthorized('reload', user):
                    self.configManager.reload()
                    self.msg(channel, "Configuration Reloaded")
                    if not self.auth.sanityCheck(False):
                        self.msg(channel, "Configuration Sanity is suspect, "\
                         "rolling back.")
                else:
                    self.msg(channel, "You aren't authorized for reload.")
            #KICK
            elif command == 'kick':
                if self.auth.isUserAuthorized('kick', user):
                    if self.nickname not in msg.rsplit()[index + 1:]:
                        for i in msg.rsplit()[index + 1:]:
                            self.kick(channel, i, 'Later broseph.')
                    else:
                        self.msg(channel, "Nope, not happening.")
                else:
                    self.kick(channel, user, 'Sorry bro, nothing personal.')
            else:
                '''
                External script execution goes here
                '''
                if self.auth.isUserAuthorized(msg.rsplit()[index].lower(),\
                                                                        user):
                    #kick off the async call
                    #channel, command, params
                    self.invokeCommand(channel,\
                                       command,\
                                       (" ".join(msg.rsplit()[index + 1:])))
                else:
                    self.msg(channel, "You aren't authorized for %s." %\
                             (command))
        else:
            '''
            filter processing go here
            '''
            pass

    def invokeCommand(self, channel, command, params):
        tmp = threads.deferToThread(self.__shellCall, channel, command, params)
        tmp.addCallback(self.postToIRC)

    def __shellCall(self, channel, command, params):
        command = self.sanitize(command)
        params = self.sanitize(params)
        command = "exec python ./bin/%s.py %s 2> /dev/null" % (command, params)
        self.p = Popen(
            command,
            stderr=STDOUT,
            stdout=PIPE,
            close_fds=True,
            shell=True)
        out, err = self.p.communicate()  # @UnusedVariable
        return (channel, out.splitlines())

    def sanitize(self, s):
        for i in self.config['sanitize']:
            s = s.replace(i, '')
        return s

    def postToIRC(self, tpl):
        for i in tpl[1]:
            self.msg(tpl[0], i)

    def userJoined(self, user, channel):
        channel_dict = channel.replace('#', '')
        if self.config['channels'][channel_dict]['enable_autoop'] and\
                    user in self.config['channels'][channel_dict]['autoop']:
            self.mode(channel, set, 'o', None, user)

        if self.config['channels'][channel_dict]['enable_greeting']:
            self.msg(channel, "%s: %s" % (user,\
                    self.config['channels'][channel_dict]['greeting']))

    def kickedFrom(self, channel, kicker, message):
        """ called by twisted,
        if the bot was kicked
        """
        channel = channel.replace('#', '')
        if channel in self.config['channels'].keys() and\
            self.config['channels'][channel]['autojoin']:

            self.join(channel, self.config['channels'][channel]['key'])
        self.msg(kicker, "Why would you do that to me brah?")


class botFactory(protocol.ClientFactory):
    """
    Factory for producing "bot"
    """
    protocol = bot

    def __init__(self, channel, configManager, auth):
        self.startChannel = channel
        self.configManager = configManager
        self.config = self.configManager.getConfig()
        self.auth = auth

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

        n = self.config['network']
        p = self.config['port']
        b = botFactory(self.startChannel, self.configManager, self.auth)
        reactor.connectTCP(n, p, b)  # @UndefinedVariable
        reactor.run()                # @UndefinedVariable

    def reloadConfig(self):
        self.config = self.configManager.getConfig()

### dummy code below
h = Hydra()
