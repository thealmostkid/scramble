import scramble.puzzle
import time

class Game(object):
    def __init__(self, gid, time_limit, users, puzzle_database):
        self.gid = gid
        self.time_limit = time_limit
        self.solved = False

        self.users = users
        self.users_index = dict()
        for user in self.users:
            self.users_index[user.uid] = user

        # load puzzle database
        self.puzzles = list()
        for g in xrange(len(puzzle_database)):
            scrambles = list()
            puzzle = puzzle_database[g]
            for p in xrange(len(puzzle) - 1):
                parts = puzzle[p]
                scrambl = scramble.puzzle.Scramble('%sp%ds%d' % (gid, g, p),
                        str(p + 1), parts[0], parts[1])
                # set indices
                if len(parts) > 2:
                    scrambl.indices = parts[2]
                if p > 0:
                    scrambl.prev_scramble = scrambles[-1]
                    scrambl.prev_scramble.next_scramble = scrambl
                scrambles.append(scrambl)

            # special mystery scramble
            mystery = scramble.puzzle.Scramble('%sp%dm' % (gid, g), 'Mystery', puzzle[-1][0], '')
            mystery.mystery = True
            mystery.prev_scramble = scrambles[-1]
            mystery.prev_scramble.next_scramble = mystery
            scrambles.append(mystery)

            self.puzzles.append(scrambles)

        self.scrambles_index = dict()
        for puzzle in self.puzzles:
            for scrambl in puzzle:
                self.scrambles_index[scrambl.pid] = scrambl

        # set up game for first puzzle
        self.start_puzzle(0)

    def completed(self):
        return self.puzzle >= len(self.puzzles)

    def start_puzzle(self, gindx):
        self.puzzle = gindx
        if self.completed():
            return
        self.start = time.time()
        self.solved = False
        # all players start game at first scramble
        for user in self.users:
            user.scramble = self.puzzles[self.puzzle][0]

    def timer(self):
        elapsed = int(time.time() - self.start)
        return self.time_limit - elapsed

    def get_scramble(self, pid):
        return self.scrambles_index[pid]

    def get_user(self, uid):
        return self.users_index[uid]

    def solve(self, pid, uid):
        scrambl = self.get_scramble(pid)
        scrambl.solve(uid)
        mystery = self.puzzles[self.puzzle][-1]
        for index in scrambl.indices:
            mystery.scramble += scrambl.value[index - 1]
        self.solved = True
        for scrambl in self.puzzles[self.puzzle]:
            self.solved = scrambl.solved and self.solved
