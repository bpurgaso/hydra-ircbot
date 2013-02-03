import yaml
import random


class Snark(object):

    def __init__(self):
        f = open('./bin/broism.yaml')
        self.snarks = yaml.load(f)
        f.close()

    def selectRandomBroism(self):
        l = self.snarks['broisms'].values()
        index = random.randint(0, len(l) - 1)
        return "Article %s:  %s" % (index, l[index])


s = Snark()
print s.selectRandomBroism()
