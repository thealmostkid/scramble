'''
Logic for running a scramble.
'''

DEFAULT = '''
puzzle
scramble DRAWN DNRAW 2,3,4
scramble IRONY INROY 1,5
scramble WALNUT AWLUTN 2
scramble PENCIL CILNEP
scramble STYLE TESYL
scramble MELODY DYLOME
mystery AIRWAY'''

NEW_DEFAULT = '''
jumble s1 AFFORD DFROFA 
jumble s2 UPPER PRPUE
jumble s3 BELLS SELBL  
jumble s4 INJURY IRJUYN 
jumble s5 BLURRY BULYRR
jumble s6 NAVAL NVALA
jumble s7 BURLAP PLRUBA

jumble s8 TIMING TGMINI 
jumble s9 ANYHOW OWHANY 
jumble s10 FLOCK CKOLF
jumble s11 NOODLE DNOLEO
jumble s12 LUCKY KUYLC
jumble s13 BELLY LEYLB 
jumble s14 FOOLED FOODLE

puzzle warmup seconds 180
jumble s10 keys 1,3
jumble s11 keys 2,4,6
jumble s12 keys 1
jumble s14 mystery
elzzup

puzzle p1 seconds 300
jumble s1
jumble s2 keys 1,2,5
jumble s3
jumble s4
jumble s5 keys 1
jumble s6 keys 2,5
jumble s7 mystery
elzzup
'''

def parse(lines):
    puzzles = list()
    current_puzzle = None
    for line in lines:
        line = line.strip()
        if line == '':
            continue
        parts = line.split()

        # puzzle
        if parts[0] == 'puzzle':
            if current_puzzle is not None:
                if len(current_puzzle) == 0:
                    raise ValueError('No scrambles specified for the puzzle')
                puzzles.append(current_puzzle)
            current_puzzle = list()
        # scramble
        elif parts[0] == 'scramble':
            if len(parts) < 3:
                raise ValueError('No scramble specified: "%s"' % line)
            scramble = [parts[1], parts[2]]
            if len(parts) > 3:
                # raises ValueError if not an integer
                indices = [int(index) for index in parts[3].split(',')]
                scramble.append(indices)

            current_puzzle.append(scramble)
        # mystery
        elif parts[0] == 'mystery':
            current_puzzle.append([parts[1]])
        # failure
        else:
            raise ValueError('Unknown input: "%s"' % line)

    if current_puzzle is None:
        raise ValueError('"puzzle" not specified')
    elif len(current_puzzle) == 0:
        raise ValueError('No scrambles specified for the puzzle')

    puzzles.append(current_puzzle)
    return puzzles

def test_parse():
    print 'TEST PARSE'
    for database in [
            [''],
            ['puzzle'],
            ['puzzle','scramble foo'],
            ['puzzle','scramble foo ofo a,b,c'],
            ['puzzle','jumble foo ofo 1,2,3'],
            ]:
        try:
            parse(database)
            print 'Unexpectedly parsed %s' % database
        except ValueError as ve:
            print ve

    for database in [
            ['puzzle','scramble dude ddeu 2,4','mystery eu'],
            DEFAULT.split('\n'),
            ]:
        try:
            result = parse(database)
            print result
            validate_scrambles(result)
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

def validate_scrambles(database):
    for puzzle in database:
        mystery_scramble = ''
        for scramble in puzzle:
            if len(scramble) > 1:
                validate_scramble(scramble[0], scramble[1])
                if scramble[0] == scramble[1]:
                    raise ValueError('Scramble is same as solution for "%s"' % (scramble[0]))
            if len(scramble) > 2:
                for index in scramble[2]:
                    if index > len(scramble[0]):
                        raise ValueError('Index %d is out of bounds (%s)' %
                                (index, scramble[0]))
                    mystery_scramble += scramble[0][index - 1]
        mystery = puzzle[-1][0]
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
            validate_scrambles(database)
            print 'Nothing wrong'
        except ValueError as ve:
            print ve
            continue

def mutate(string):
    result = string[2:] + string[0:2]
    return result

class Scramble(object):
    def __init__(self, pid, name, value, scramble):
        self.pid = pid
        self.pretty_name = name
        self.value = value
        self.scramble = scramble
        self.indices = list()

        self.mystery = False
        self.solved = None
        self.message = None
        self.prev_scramble = None
        self.next_scramble = None

    def guess(self, submission):
        return self.value.lower() == submission.lower()

    def solve(self, uid):
        self.solved = uid
        self.message = 'solved by %s' % uid

def main():
    test_validate()
    test_parse()

if __name__ == '__main__':
    main()
