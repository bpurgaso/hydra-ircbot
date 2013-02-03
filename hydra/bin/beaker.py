import sys

input = ' '.join(sys.argv[1:])  # @ReservedAssignment
output = ''

for i in input.rsplit():
    word = 'm'
    word += 'e' * (len(i) - 2)
    if len(i) > 1:
        word += 'p'
        output += ' %s' % word

print output
