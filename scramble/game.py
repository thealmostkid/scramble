import scramble.puzzle
# GET /game/gameid returns puzzle.js.  
# 
# puzzle.js GET /game/gameid/userid for puzzle id
# PUT /game/gameid/userid to switch puzzles and update metrics
# GET /game/gameid/puzzle/puzzle_id for json puzzle representation
# PUT /game/gameid/puzzle/puzzle_id to solve
# polls /game/gameid/puzzle/puzzle_id for server-side updates
# Hidden scrambles are updated server-side and revealed via polling
# at end of round puzzle_id returns "locked"

# transition screen when game is locked
class Game(object):
    def __init__(self, users):
        self.users = users

        # TODO: load from puzzle database
        self.puzzles = list()
        self.puzzles_index = dict()
        for i in xrange(3):
            puzzle = scramble.puzzle.Puzzle('jeremy%d' % i, str(i))
            if i > 0:
                puzzle.prev_puzzle = self.puzzles[i - 1]
                puzzle.prev_puzzle.next_puzzle = puzzle
            self.puzzles.append(puzzle)
            self.puzzles_index[puzzle.nonce] = puzzle

    def get_puzzle(self, pid):
        return self.puzzles_index[pid]
