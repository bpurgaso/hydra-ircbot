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

    def saveConfigToDisk(self):
        f = open('authenticate.yaml', 'w')
        f.write(yaml.dump(self.config, default_flow_style=False))
        f.close()

    def inheritsFrom(self, group):
        pass

    def canUse(self, user, script):
        pass

    def getGroup(self, user):
        pass

    def getAvailableCommandsForUser(self, user):
        pass

    def getAvailableCommandsForGroup(self, group):
        pass
