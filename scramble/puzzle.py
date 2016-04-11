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

class Puzzle(object):
    def __init__(self, value, nonce):
        self.value = value
        self.nonce = nonce

    def guess(self, submission):
        return self.value == submission

    def scramble(self):
        return mutate(self.value)
