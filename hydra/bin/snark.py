import yaml
import random


class Snark(object):

    def __init__(self):
        f = open('./bin/snark.yaml')
        self.snarks = yaml.load(f)
        f.close()

    def selectRandomSnark(self, type):
        l = self.snarks[type]
        index = random.randint(0, len(l) - 1)
        return l[index]

s = Snark()
print s.selectRandomSnark('snarks')
