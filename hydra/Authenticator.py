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
        self.sanityCheck()

    def die(self, msg):
        print msg
        exit()

    def loadConfigFromDisk(self):
        f = open('config.yaml')
        tmp = yaml.load(f)
        f.close()
        return tmp

    def sanityCheck(self):
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

        if not sane:
            self.die('System not sane, halting.')

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

####dummy code (driver / test code)
#at = Authenticator()
#print "Moderator inherits from:  %s" % at.inheritsFrom('moderator')
#print "Creator inherits from:  %s" % at.inheritsFrom('creator')
#print "Commands available to creator:  %s" % at.getAvailableCommandsForGroup(
#                                                                    'creator')
#print "Commands available to admin:  %s" % at.getAvailableCommandsForGroup(
#                                                                    'admin')
