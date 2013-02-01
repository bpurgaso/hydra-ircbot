'''
Created on Jan 31, 2013

@author: bpurgaso
'''


import yaml


class Authenticator(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.config = self.loadConfigFromDisk()

    def loadConfigFromDisk(self):
        f = open('authenticate.yaml')
        tmp = yaml.load(f)
        f.close()
        return tmp

    def sanityCheck(self):
        pass
        '''
        all inherits_from are valid
        all command entries within a group map to valid commands
        all group entries within a user map to valid group
        '''

    def saveConfigToDisk(self):
        f = open('authenticate.yaml', 'w')
        f.write(yaml.dump(self.config, default_flow_style=False))
        f.close()

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

###dummy code (driver / test code)
at = Authenticator()
print "Moderator inherits from:  %s" % at.inheritsFrom('moderator')
print "Creator inherits from:  %s" % at.inheritsFrom('creator')
print "Commands available to creator:  %s" % at.getAvailableCommandsForGroup(
                                                                    'creator')
print "Commands available to admin:  %s" % at.getAvailableCommandsForGroup(
                                                                    'admin')
