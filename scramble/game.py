import scramble.puzzle
import time
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
    def __init__(self, gid, users):
        self.gid = gid
        self.users = users
        self.users_index = dict()
        for user in self.users:
            self.users_index[user.uid] = user

        # TODO: load from puzzle database
        self.puzzles = list()
        self.puzzles_index = dict()
        for i in xrange(3):
            puzzle = scramble.puzzle.Puzzle('jeremy%d' % i, str(i))
            if i > 0:
                puzzle.prev_puzzle = self.puzzles[i - 1]
                puzzle.prev_puzzle.next_puzzle = puzzle
            self.puzzles.append(puzzle)
            self.puzzles_index[puzzle.pid] = puzzle

        # all players start game at first puzzle
        for user in users:
            user.puzzle = self.puzzles[0]

        self.start = time.time()

    def timer(self):
        return int(time.time() - self.start)

    def get_puzzle(self, pid):
        return self.puzzles_index[pid]

    def get_user(self, uid):
        print 'looking for %s in %s' % (uid, self.users_index)
        return self.users_index[uid]
