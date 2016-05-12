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

def select_mystery_solver(user_list):
    return user_list[0]

class Game(object):
    def __init__(self, gid, users):
        self.gid = gid
        self.users = users
        self.users_index = dict()
        for user in self.users:
            self.users_index[user.uid] = user
        select_mystery_solver(self.users).mystery_solver = True

        # load puzzle database
        self.group = 0
        puzzle_database = scramble.puzzle.parse(
                scramble.puzzle.DEFAULT.split('\n'))
        self.groups = list()
        for g in xrange(len(puzzle_database)):
            puzzles = list()
            group = puzzle_database[g]
            for p in xrange(len(group) - 1):
                parts = group[p]
                puzzle = scramble.puzzle.Puzzle('r%dp%d' % (g, p),
                        parts[0], parts[1])
                # set indices
                if len(parts) > 2:
                    puzzle.indices = parts[2]
                if p > 0:
                    puzzle.prev_puzzle = puzzles[-1]
                    puzzle.prev_puzzle.next_puzzle = puzzle
                puzzles.append(puzzle)

            # special mystery puzzle
            mystery = scramble.puzzle.Puzzle('r%dm' % g, group[-1][0], '')
            mystery.prev_puzzle = puzzles[-1]
            mystery.prev_puzzle.next_puzzle = mystery
            puzzles.append(mystery)

            self.groups.append(puzzles)

        self.puzzles_index = dict()
        for group in self.groups:
            for puzzle in group:
                self.puzzles_index[puzzle.pid] = puzzle

        # all players start game at first puzzle
        for user in users:
            user.puzzle = self.groups[self.group][0]

        self.start = time.time()

    def timer(self):
        return int(time.time() - self.start)

    def get_puzzle(self, pid):
        return self.puzzles_index[pid]

    def get_user(self, uid):
        return self.users_index[uid]

    def solve(self, pid, uid):
        puzzle = self.get_puzzle(pid)
        puzzle.solve(uid)
        # TODO: dynamic based on round
        mystery = self.get_puzzle('r0m')
        for index in puzzle.indices:
            mystery.scramble += puzzle.value[index - 1]

