'''
Logic for running a scramble.
'''

DEFAULT = '''
jumble s1 ADOPT PTOAD
jumble s2 BLOOD DOBOL
jumble s3 RIVER RIERV
jumble s4 INCOME CMEINO
jumble s5 FEMALE MFEEAL
jumble s6 TOWARD ADTWOR
jumble s7 ADMIRE RIEMAD

jumble s8 CHALK LACKH
jumble s9 THANK HNKTA
jumble s10 PLANET NTAPLE
jumble s11 STRESS SETSRS
jumble s12 MONEY ENYOM
jumble s13 CLOUDY YUDCOL
jumble s14 HEALTH HHLATE

jumble s15 DRAWN RNADW
jumble s16 STYLE LTYES
jumble s17 IRONY YONRI
jumble s18 MELODY OLDMEY
jumble s19 PENCIL CLNPIE
jumble s20 WALNUT AWLUTN
jumble s21 AIRWAY RAWIYA

jumble s22 OMEGA GEMAO
jumble s23 ERROR REORR
jumble s24 KNIGHT THINGK
jumble s25 TATTOO TOTOAT
jumble s26 CHAIR HRIAC
jumble s27 LAWYER WYERAL
jumble s28 MATTER MERTAT

jumble s29 HEAVY YEHAV
jumble s30 BLOOM MOLOB
jumble s31 GRAVE RAGEV
jumble s32 LIZARD ZLARDI
jumble s33 FAMOUS SOMUAF
jumble s34 GAMBLE AEMGLB
jumble s35 BAMBOO BOMAOB

jumble s36 GILLS LGSIL
jumble s37 JOLLY YLOJL
jumble s38 GUZZLE ZEGZLU
jumble s39 IMMUNE MIENMU
jumble s40 NUDGE DGENU
jumble s41 COTTON TTOCNO
jumble s42 JUNGLE GLJUNE

jumble s43 FLOSS SLOFS
jumble s44 OVENS NVOSE
jumble s45 ZIPPER PIERPZ
jumble s46 POCKET CPOTKE
jumble s47 BROWN NOBWR
jumble s48 JETLAG TAGEJL
jumble s49 LOSSES LSSOSE

jumble s50 AWFUL FLWUA
jumble s51 JUICY CUYIJ
jumble s52 OFFEND EFFDON
jumble s53 JEWELS SEWJEL
jumble s54 MERGE RGEME
jumble s55 CIRCUS CSUCIR
jumble s56 JOYFUL YOUJLF

jumble s57 JOINT INJOT
jumble s58 GRASS SAGRS
jumble s59 EYELID DEELYI
jumble s60 SUPPLY PLSYUP
jumble s61 DRINK NIRDK
jumble s62 OUTFIT TUFOIT
jumble s63 ESSAYS SSYSAE

puzzle warmup seconds 180
jumble s2
jumble s4
jumble s6 keys 6
jumble s5 keys 3,4
jumble s1
jumble s3 keys 1,2,4
jumble s7 mystery
elzzup

puzzle p1 seconds 180
jumble s12
jumble s11
jumble s8 keys 2,3,4
jumble s10 keys 5
jumble s9 keys 1,2
jumble s13
jumble s14 mystery
elzzup

puzzle p2 seconds 180
jumble s15 keys 2,3,4
jumble s18
jumble s20 keys 2
jumble s16
jumble s17 keys 1,5
jumble s19
jumble s21 mystery
elzzup

puzzle p3 seconds 180
jumble s22 keys 2,3
jumble s23 keys 2
jumble s24
jumble s25 keys 1,2,4
jumble s26
jumble s27
jumble s28 mystery
elzzup

puzzle p4 seconds 180
jumble s29
jumble s31
jumble s33 keys 2,4
jumble s34 keys 4
jumble s30 keys 1,3,5
jumble s32
jumble s35 mystery
elzzup

puzzle p5 seconds 180
jumble s36 keys 1,4
jumble s37 keys 1
jumble s40
jumble s39 keys 4,5,6
jumble s38
jumble s41
jumble s42 mystery
elzzup

puzzle p6 seconds 180
jumble s48 
jumble s47
jumble s43 keys 2,4,5
jumble s44 keys 1,5
jumble s45 keys 5
jumble s46 
jumble s49 mystery
elzzup

puzzle p7 seconds 180
jumble s50
jumble s54
jumble s55
jumble s53 keys 5
jumble s52 keys 1,3
jumble s51 keys 1,2,5
jumble s56 mystery
elzzup

puzzle p8 seconds 180
jumble s57
jumble s62
jumble s59 keys 2,3
jumble s60 keys 1
jumble s61
jumble s58 keys 3,4,5
jumble s63 mystery
elzzup
'''

OLD = '''
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
