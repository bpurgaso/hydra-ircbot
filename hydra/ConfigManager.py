'''
Created on Feb 3, 2013

@author: bpurgaso
'''


import yaml


class ConfigManager(object):
    '''
    Configuration Manager
    Handles all IO to config.yaml
    Objects registering as listeners must have a reloadConfig(), and register
    themselves as listeners to receive automatic config updates after a write
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.config = self.loadConfigFromDisk()
        self.sanityCheck()
        self.listeners = []

    def loadConfigFromDisk(self):
        f = open('config.yaml')
        tmp = yaml.load(f)
        f.close()
        return tmp

    def reload(self):
        self.loadConfigFromDisk()
        for i in self.listeners:
            try:
                i.reloadConfig()
            except:
                print 'Reload Config Fail:  %s' % str(i)

    def getConfig(self):
        return self.config

    def registerListener(self, obj):
        self.listeners.append(obj)

    def saveConfigToDisk(self):
        f = open('config.yaml', 'w')
        f.write(yaml.dump(self.config, default_flow_style=False))
        f.close()
        self.reload()

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
