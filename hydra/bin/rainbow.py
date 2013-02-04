import sys
import random


colors = ['02', '03', '04', '05', '06', '07', '08', '09', '10',\
          '11', '12', '13', '14', '15']
prefix = '\x03'
s = ' '.join(sys.argv[1:])
cs = ''
for i in s.rstrip():
    flast = 0
    fnew = 0

    while flast == fnew:  # or blast == bnew or fnew == bnew:
        fnew = random.randint(1, len(colors) - 1)
    #bnew = random.randint(1, len(colors)-1)
    cs += "%s%s%s" % (prefix, colors[fnew], i)
    flast = fnew
    #blast = bnew
cs += prefix
print cs
