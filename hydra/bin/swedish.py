#!/usr/bin/python
import sys

input = ' '.join(sys.argv[1:])
chefSpeak = {'a': 'e', 'f': 'ff', 'i': 'ee', 'o': 'u', 'u': 'oo',\
             'v': 'f', 'w': 'v'}

output = ''
for i in input:
    if i in chefSpeak.keys():
        output += chefSpeak[i]
    else:
        output += i

print output
