'''
Logic for running a puzzle.
'''

#DEFAULT = '''
#round
#puzzle DRAWN DNRAW 2,3,4
#puzzle IRONY INROY 1,5
#puzzle WALNUT AWLUTN 2
#puzzle PENCIL CILNEP
#puzzle STYLE TESYL
#puzzle MELODY DYLOME
#mystery AIRWAY
#round
#puzzle DRAWN DNRAW 2,3,4
#puzzle WALNUT AWLUTN 2
#puzzle PENCIL CILNEP 5
#puzzle STYLE TESYL 3
#puzzle IRONY INROY
#puzzle MELODY DYLOME
#mystery AIRWAY'''

DEFAULT = '''
round
puzzle DRAWN DNRAW 2,3,4
mystery AIRWAY
round
puzzle WALNUT AWLUTN 2
mystery AIRWAY'''

def parse(lines):
    rounds = list()
    current_round = None
    for line in lines:
        line = line.strip()
        if line == '':
            continue
        parts = line.split()

        # round
        if parts[0] == 'round':
            if current_round is not None:
                if len(current_round) == 0:
                    raise ValueError('No puzzles specified for the round')
                rounds.append(current_round)
            current_round = list()
        # puzzle
        elif parts[0] == 'puzzle':
            if len(parts) < 3:
                raise ValueError('No scramble specified: "%s"' % line)
            puzzle = [parts[1], parts[2]]
            if len(parts) > 3:
                # raises ValueError if not an integer
                indices = [int(index) for index in parts[3].split(',')]
                puzzle.append(indices)

            current_round.append(puzzle)
        # mystery
        elif parts[0] == 'mystery':
            current_round.append([parts[1]])
        # failure
        else:
            raise ValueError('Unknown input: "%s"' % line)

    if current_round is None:
        raise ValueError('"round" not specified')
    elif len(current_round) == 0:
        raise ValueError('No puzzles specified for the round')

    rounds.append(current_round)
    return rounds

def test_parse():
    print 'TEST PARSE'
    for database in [
            [''],
            ['round'],
            ['round','puzzle foo'],
            ['round','puzzle foo ofo a,b,c'],
            ['round','jumble foo ofo 1,2,3'],
            ]:
        try:
            parse(database)
            print 'Unexpectedly parsed %s' % database
        except ValueError as ve:
            print ve

    for database in [
            ['round','puzzle dude ddeu 2,4','mystery eu'],
            DEFAULT.split('\n'),
            ]:
        try:
            result = parse(database)
            print result
            validate_puzzles(result)
            print 'Parsed'
        except ValueError as ve:
            print 'Unexpected error %s' % ve

def validate_scramble(solution, scramble):
    validate = dict()
    for i in xrange(len(solution)):
        char = solution[i]
        if char not in validate:
            validate[char] = 0
        validate[char] += 1
    for i in xrange(len(scramble)):
        char = scramble[i]
        if char not in validate:
            raise ValueError('Unknown letter for "%s": (%s)' % (solution, char))
        validate[char] -= 1
    for (char, counter) in validate.items():
        if counter > 0:
            raise ValueError('Missing letter for "%s": (%s)' % (solution, char))
        elif counter < 0:
            raise ValueError('Extra letter for "%s": (%s)' % (solution, char))

def validate_puzzles(database):
    for group in database:
        mystery_scramble = ''
        for puzzle in group:
            if len(puzzle) > 1:
                validate_scramble(puzzle[0], puzzle[1])
                if puzzle[0] == puzzle[1]:
                    raise ValueError('Scramble is same as solution for "%s"' % (puzzle[0]))
            if len(puzzle) > 2:
                for index in puzzle[2]:
                    if index > len(puzzle[0]):
                        raise ValueError('Index %d is out of bounds (%s)' %
                                (index, puzzle[0]))
                    mystery_scramble += puzzle[0][index - 1]
        mystery = group[-1][0]
        validate_scramble(mystery, mystery_scramble)

def test_validate():
    print 'TEST VALIDATE'
    # failure cases
    for database in [
        [[['foo', 'ofo', [1]], ['of']]],
        [[['foo', 'ofo', [1]], ['box', 'xbo', [2]], ['foo']]],
        [[['foo', 'ofo', [2,3]], ['box', 'xbo', [2]], ['oo']]],
        [[['fox', 'ofx', [1,2,3]], ['ox']]],
        [[['fox', 'mxo', [2,3]], ['ox']]],
        [[['man', 'man', [2]], ['a']]],
        ]:
        try:
            validate_puzzles(database)
            print 'Nothing wrong'
        except ValueError as ve:
            print ve
            continue

def mutate(string):
    result = string[2:] + string[0:2]
    return result

class Puzzle(object):
    def __init__(self, pid, name, value, scramble):
        self.pid = pid
        self.pretty_name = name
        self.value = value
        self.scramble = scramble
        self.indices = list()

        self.solved = False
        self.message = None
        self.prev_puzzle = None
        self.next_puzzle = None

    def guess(self, submission):
        return self.value.lower() == submission.lower()

    def solve(self, uid):
        self.solved = True
        self.message = 'solved by %s' % uid

def main():
    test_validate()
    test_parse()

if __name__ == '__main__':
    main()
