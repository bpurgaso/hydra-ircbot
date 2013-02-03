'''
Created on Jan 31, 2013

@author: bpurgaso
'''


import yaml


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
        self.config = self.reloadConfig()
        self.sanityCheck()

    def reloadConfig(self):
        self.conf = self.configManager.getConfig()

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
            group = self.config['groups'][group]['inherits_from']
            commands.extend(self.config['groups'][group]['commands'])
            if self.config['groups'][group]['inherits_from'] == 'None':
                break
        return commands

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
