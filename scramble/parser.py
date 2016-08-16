#!/usr/bin/env python
import shlex

class ParseError(Exception):
    pass

class Jumble(object):
    '''Represent a Jumble.'''
    def __init__(self, name, value, jumble):
        self.name = name
        self.value = value
        self.jumble = jumble

    def __str__(self):
        return '%s(%s, %s, %s)' % (self.__class__.__name__, self.name,
                self.value, self.jumble)

    def __repr__(self):
        return str(self)

def parse_jumble(lexer):
    '''Extract a jumble.'''
    name = lexer.get_token()
    if name is None:
        raise ParseError('Incomplete jumble: missing identifier')
    value = lexer.get_token()
    if value is None:
        raise ParseError('Incomplete jumble: missing word for "%s"' % name)
    jumble = lexer.get_token()
    if jumble is None:
        raise ParseError('Incomplete jumble: missing jumble for "%s"' % name)
    return Jumble(name, value, jumble)

def validate_jumble(jumble):
    '''Validate a jumble.'''
    validate = dict()
    if jumble.value == jumble.jumble:
        raise ValueError('Invalid Jumble "%s": value and jumble are the same')

    for i in xrange(len(jumble.value)):
        char = jumble.value[i]
        if char not in validate:
            validate[char] = 0
        validate[char] += 1
    for i in xrange(len(jumble.jumble)):
        char = jumble.jumble[i]
        if char not in validate:
            raise ValueError('Invalid Jumble "%s": Unknown letter for "%s": (%s)' % (jumble.name, jumble.value, char))
        validate[char] -= 1
    for (char, counter) in validate.items():
        if counter > 0:
            raise ValueError('Invalid Jumble "%s": Missing letter for "%s": (%s)' % (jumble.name, jumble.value, char))
        elif counter < 0:
            raise ValueError('Invalid Jumble "%s": Extra letter for "%s": (%s)' % (jumble.name, jumble.value, char))


class Scramble(object):
    '''Represent a scramble.'''
    def __init__(self, name, keys=None, mystery=False):
        self.name = name
        if keys is None:
            self.keys = list()
        else:
            self.keys = keys
        self.mystery = mystery

    def __str__(self):
        return '%s(%s, %s, %s)' % (self.__class__.__name__, self.name,
                self.keys, self.mystery)

    def __repr__(self):
        return str(self)

def parse_scramble(lexer):
    '''Extract a scramble.'''
    name = lexer.get_token()
    if name is None:
        raise ParseError('Incomplete scramble: missing identifier')

    keys = None
    mystery = False
    while True:
        token = lexer.get_token()
        if token is None:
            break
        elif token == 'keys':
            keys = lexer.get_token()
            if keys is None:
                raise ParseError('Incomplete scramble: scramble %s missing keys' % name)
            try:
                keys = [int (key) for key in keys.split(',')]
            except ValueError:
                raise ParseError('Invalid scramble: scramble %s bad key "%s"' % (name, keys))
        elif token == 'mystery':
            mystery = True
        else:
            lexer.push_token(token)
            break;
    return Scramble(name, keys, mystery)

def validate_scramble(scramble, jumbles):
    '''Validate a Scramble.'''
    try:
        jumble = jumbles[scramble.name]
    except KeyError:
        raise ValueError('Invalid scramble %s: unknown jumble "%s"' % (scramble.name, scramble.name))
    for key in scramble.keys:
        if key > len(jumble.value):
            raise ValueError('Invalid scramble %s: key %d out-of-bounds' % (scramble.name, key))

class Puzzle(object):
    def __init__(self, name, seconds, scrambles):
        self.name = name
        self.seconds = seconds
        self.scrambles = scrambles

    def __str__(self):
        return '%s(%s, %d, %s)' % (self.__class__.__name__, self.name,
                self.seconds, self.scrambles)

    def __repr__(self):
        return str(self)

def parse_puzzle(lexer, jumbles):
    '''Extract a puzzle.'''
    name = lexer.get_token()
    if name is None:
        raise ParseError('Incomplete puzzle: missing identifier')
    keyword = lexer.get_token()
    if keyword is None or keyword != 'seconds':
        raise ParseError('Incomplete puzzle: puzzle "%s" missing seconds' % name)
    seconds = lexer.get_token()
    if seconds is None:
        raise ParseError('Incomplete puzzle: puzzle "%s" missing seconds' % name)
    try:
        seconds = int(seconds)
    except ValueError:
        raise ParseError('Invalid puzzle: puzzle "%s" invalid seconds "%s"' % (name, seconds))
    token = lexer.get_token()
    scrambles = list()
    while token is not None and token != 'elzzup':
        if token == 'jumble':
            scramble = parse_scramble(lexer)
            print scramble
            validate_scramble(scramble, jumbles)
            scrambles.append(scramble)
        else:
            raise ParseError('Invalid puzzle: puzzle "%s" unknown token "%s"' % (name, token))
        token = lexer.get_token()
    if token != 'elzzup':
        raise ParseError('Invalid puzzle: puzzle not closed with "elzzup"')
    return Puzzle(name, seconds, scrambles)

def validate_puzzle(puzzle, jumbles):
    '''Validate a Puzzle.'''
    if puzzle.seconds <= 0:
        raise ValueError('Invalid puzzle: puzzle %s seconds invalid %d' % (puzzle.name, puzzle.seconds))
    mystery = None
    mystery_jumble = list()
    scrambles = set()
    for scramble in puzzle.scrambles:
        if scramble.name in scrambles:
            raise ValueError('Invalid puzzle: puzzle %s uses jumble "%s" twice' % (puzzle.name, scramble.name))
        scrambles.add(scramble.name)
        jumble = jumbles[scramble.name]
        if scramble.mystery:
            mystery = jumble.value
        for key in scramble.keys:
            mystery_jumble += jumble.value[key - 1]

    if mystery is None:
        raise ValueError('Invalid puzzle: puzzle %s missing mystery' % (puzzle.name))

    mystery_jumble = Jumble('m', mystery, mystery_jumble)
    validate_jumble(mystery_jumble)

class Database(object):
    '''Database of all parsed info.'''
    def __init__(self, jumbles, puzzles):
        self.jumbles = jumbles
        self.puzzles = puzzles

    def __str__(self):
        return '%s(%s, %s)' % (self.__class__.__name__, self.jumbles,
                self.puzzles)

    def __repr__(self):
        return str(self)

def parse(text):
    '''Parse the database.'''
    lexer = shlex.shlex(text, posix=True)
    lexer.whitespace_split = True
    token = lexer.get_token()
    jumbles = dict()
    puzzles = list()
    while token is not None:
        if token == 'jumble':
            jumble = parse_jumble(lexer)
            print jumble
            validate_jumble(jumble)
            jumbles[jumble.name] = jumble
        elif token == 'puzzle':
            puzzle = parse_puzzle(lexer, jumbles)
            print puzzle
            validate_puzzle(puzzle, jumbles)
            puzzles.append(puzzle)
        else:
            print 'Unknown token: "%s"' % token
        token = lexer.get_token()

    return Database(jumbles, puzzles)

def main():
    for failure in ['jumble', 'jumble a', 'jumble a value']:
        try:
            parse(failure)
            raise RuntimeError('Did not fail "%s"' % failure)
        except (ParseError, ValueError) as e:
            print e

    for failure in [
            'jumble a foo of',
            'jumble a foo off',
            'jumble a foo bar',
            'jumble a foo foo',
            ]:
        try:
            parse(failure)
            raise RuntimeError('Did not fail "%s"' % failure)
        except (ParseError, ValueError) as e:
            print e

    for failure in [
            'puzzle p1 seconds 1 jumble',
            'puzzle p1 seconds 1 jumble s1 keys',
            'puzzle p1 seconds 1 jumble s1',
            'puzzle p1 seconds 1 jumble s1 keys notanumber',
            'puzzle p1 seconds 1 jumble s1 keys 0 elzzup',
            'jumble s1 of fo puzzle p1 seconds 1 jumble s1 keys 99',
            ]:
        try:
            parse(failure)
            raise RuntimeError('Did not fail "%s"' % failure)
        except (ParseError, ValueError) as e:
            print e

    for failure in [
            'jumble s1 ab ba puzzle',
            'jumble s1 ab ba puzzle p1',
            'jumble s1 ab ba puzzle p1 seconds',
            'jumble s1 ab ba puzzle p1 seconds 90',
            'jumble s1 ab ba puzzle p1 seconds notanumber elzzup',
            'jumble s1 ab ba puzzle p1 seconds 1 jumble s1 foobar',
            'jumble s1 ab ba puzzle p1 seconds -1 elzzup',
            'jumble s1 ab ba puzzle p1 seconds 0 elzzup',
            'jumble s1 ab ba puzzle p1 seconds 1 jumble s1 elzzup',
            'jumble s1 ab ba puzzle p1 seconds 1 jumble s1 mystery elzzup',
            'jumble s1 ab ba puzzle p1 seconds 1 jumble s1 mystery jumble s1 elzzup',
            'jumble s0 no on jumble s1 ab ba puzzle p1 seconds 1 jumble s0 keys 1,2 jumble s1 mystery elzzup',
            ]:
        try:
            parse(failure)
            raise RuntimeError('Did not fail "%s"' % failure)
        except (ParseError, ValueError) as e:
            print e

    test = '''
jumble s1 AFFORD DFROFA
jumble s2 UPPER PRPUE
jumble s3 BELLS SELBL
jumble s4 INJURY IRJUYN
jumble s5 BLURRY BULYRR
jumble s6 NAVAL NVALA
jumble s7 BURLAP PLRUBA

jumble s8 TIMING TGMINI
jumble s9 ANYHOW OWHANY
jumble s10 FLOCK CKOLF 1,3
jumble s11 NOODLE DNOLEO 2,4,6
jumble s12 LUCKY KUYLC 1
jumble s13 BELLY LEYLB
jumble s14 FOOLED FOODLE

puzzle p1 seconds 300
jumble s1
jumble s2 keys 1,2,5
jumble s3
jumble s4
jumble s5 keys 1
jumble s6 keys 2,5
jumble s7 mystery
elzzup

puzzle p2 seconds 120
jumble s10 keys 1,3
jumble s11 keys 2,4,6
jumble s12 keys 1
jumble s14 mystery
elzzup
'''
    database = parse(test)
    print database
    return 0

if __name__ == '__main__':
    exit(main())
