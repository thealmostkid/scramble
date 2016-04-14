'''
Logic for running a puzzle.
'''

'''
puzzle:
    scrambled letters
    guess board
    submit button
    activity view
    left
    right
'''
import random
def mutate(string):
    result = string[2:] + string[0:2]
    return result

class Puzzle(object):
    def __init__(self, value, nonce):
        self.value = value
        self.nonce = nonce
        self.state = None
        self.prev_puzzle = None
        self.next_puzzle = None

    def guess(self, submission):
        return self.value == submission

    def solve(self):
        self.state = 'solved'

    def scramble(self):
        return mutate(self.value)

    def js_object(self):
        result = '{pid:"%s",scramble:"%s"' % (self.nonce, self.scramble())
        if self.prev_puzzle is not None:
            result += ',previous:"%s"' % self.prev_puzzle.nonce
        if self.next_puzzle is not None:
            result += ',next:"%s"' % self.next_puzzle.nonce
        if self.state is not None:
            result += ',state:"%s"' % self.state
        # TODO: previous, next
        result += '}'
        return result
