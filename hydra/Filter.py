'''
Created on Feb 3, 2013

@author: bpurgaso
'''


'''
I need to take time to carefully consider how to go about
implementing this functionality.
'''


class FilterManager(object):
    '''
    classdocs
    '''

    def __init__(self, configManager):
        '''
        Constructor
        '''
        self.configManager = configManager
        self.configManager.registerListener(self)
        self.config = self.reloadConfig()

    def reloadConfig(self):
        self.config = self.configManager.getConfig()

    def filterMsg(self, message, user, channel):
        pass
