'''
Created on Jan 31, 2013

@author: bpurgaso
'''


class Authenticator(object):
    '''
    classdocs
    '''

    def __init__(self, configManager):
        '''
        Constructor
        '''
        self.configManager = configManager
        self.configManager.registerListener(self)  # reg for config updates
        self.reloadConfig()
        self.sanityCheck(True)

    def die(self, msg):
        print msg
        exit()

    def reloadConfig(self):
        print "Authenticator:  Reloading Config"
        self.config = self.configManager.getConfig()

    #utility methods
    def inheritsFrom(self, group):
        return self.config['groups'][group]['inherits_from']

    def getGroup(self, user):
        try:
            return self.config['users'][user]['group']
        except:
            return self.config['defaultgroup']

    def getAvailableCommandsForUser(self, user):
        return self.getAvailableCommandsForGroup(self.getGroup(user))

    def getAvailableCommandsForGroup(self, group):
        commands = self.config['groups'][group]['commands']

        if '*' == commands[0]:
            return self.getAllCommands()

        while True:
            if self.config['groups'][group]['inherits_from'] == 'None':
                break
            group = self.config['groups'][group]['inherits_from']
            commands.extend(self.config['groups'][group]['commands'])
        tmp = list(set(commands))
        tmp.sort()
        return tmp

    def getAllCommands(self):
        return self.config['commands'].keys()

    #convenience methods
    def isUserAuthorized(self, command, user):
        if command in self.getAvailableCommandsForUser(user):
            return True
        else:
            return False

    def isGroupAuthorized(self, command, group):
        if command in self.getAvailableCommandsForUser(group):
            return True
        else:
            return False

    def getPowerOfGroup(self, group):
        return self.config['groups'][group]['power_level']

    def getPowerOfUser(self, user):
        return self.getPowerOfGroup(self.getGroup(user))

    def getHelpForCommand(self, command):
        return self.config['commands'][command]['help']

    def registerUser(self, uname, group='default'):
        if group == 'default':
            group = self.config['default_register_group']

        if uname in self.config['users'].keys() and group ==\
            self.getGroup(uname):

            return "Username (%s) is already registered." % uname

        self.config['users'][uname] = {'group': group}

        self.configManager.saveConfigToDisk(self.config)
        return "%s is now recognized as a %s" % (uname, group)

    def whoami(self, uname):
        if uname in self.config['users'].keys():
            return "You are %s, %s." % (uname, self.getGroup(uname))
        else:
            return 'I do not recognize you.  Register with the \'register\' '\
                'command.'

    def toggleAutoOp(self, uname, channel, enable):
        channel = channel.replace('#', '')
        print "got here", enable, channel, uname
        if enable:
            if uname not in self.config['channels'][channel]['autoop']:
                self.config['channels'][channel]['autoop'].append(str(uname))
        else:
            try:
                self.config['channels'][channel]['autoop'].remove(str(uname))
            except:
                pass

        self.configManager.saveConfigToDisk(self.config)

        if enable:
            return "autoop enabled for %s in %s." % (uname, '#' + channel)
        return "autoop disabled for %s in %s." % (uname, '#' + channel)

    def createChannelEntry(self, channel):
        self.config['channels'][channel] = {}
        self.config['channels'][channel]['autojoin'] = True
        self.config['channels'][channel]['autoop'] =\
            list(self.config['default_autoop'])
        self.config['channels'][channel]['enable_autoop'] = True
        self.config['channels'][channel]['enable_greeting'] = False
        self.config['channels'][channel]['greeting'] =\
            'Generic greeting and expression of joy.'
        self.config['channels'][channel]['key'] = ''

        self.configManager.saveConfigToDisk(self.config)

    def sanityCheck(self, fatal=False):
        '''
        all inherits_from are valid
        all command entries within a group map to valid commands
        all group entries within a user map to valid group
        '''
        prefix = '[YAML Sanity Failure]  '
        sane = True
        #check all inherits_from
        for i in self.config['groups'].keys():
            inherit_entry = self.config['groups'][i]['inherits_from']
            if inherit_entry not in self.config['groups'].keys()\
             and inherit_entry != 'None':
                print "%sGroup '%s' has invalid inheirts_from entry:  %s." %\
                  (prefix, i, inherit_entry)
                sane = False

        #check all command entries for each group
        for i in self.config['groups'].keys():
            command_list = self.config['groups'][i]['commands']
            for j in command_list:
                if j not in self.getAllCommands() and j != '*':
                    print "%sGroup '%s' has invalid command entry:  %s" %\
                      (prefix, i, j)
                    sane = False

        #check all users for invalid group entries
        for i in self.config['users'].keys():
            group_entry = self.config['users'][i]['group']
            if group_entry not in self.config['groups'].keys():
                print "%sUser '%s' has an invalid group membership:  %s" %\
                  (prefix, i, group_entry)
                sane = False

        #check all power_levels
        for i in self.config['groups'].keys():
            tmp = []
            if self.getPowerOfGroup(i) in tmp:
                sane = False
                print "power_level conflict:  %s" % self.getPowerOfGroup(i)
                tmp.append(i)

        if not sane and fatal:
            self.die('System not sane, halting.')
        elif not sane:
            self.configManager.rollBack()
            return False
        return True
