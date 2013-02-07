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
        self.config = self.lastKnownGoodConfig = self.loadConfigFromDisk()
        self.listeners = []

    def loadConfigFromDisk(self):
        f = open('config.yaml')
        tmp = yaml.load(f)
        f.close()
        return tmp

    def reload(self):
        self.lastKnownGoodConfig = self.config
        self.config = self.loadConfigFromDisk()
        for i in self.listeners:
            try:
                i.reloadConfig()
            except:
                print 'Reload Config Fail:  %s' % str(i)

    def rollBack(self):
        self.config = self.lastKnownGoodConfig
        for i in self.listeners:
            try:
                i.reloadConfig()
            except:
                print 'Reload Config Fail:  %s' % str(i)

    def getConfig(self):
        return self.config

    def registerListener(self, obj):
        self.listeners.append(obj)

    def saveConfigToDisk(self, config):
        f = open('config.yaml', 'w')
        f.write(yaml.dump(config, default_flow_style=False))
        f.close()
        self.reload()
