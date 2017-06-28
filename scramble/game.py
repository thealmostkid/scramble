import scramble.puzzle
import time

DUMMY_SCRAMBLE = scramble.puzzle.Scramble('000', '0', '', '')

class Game(object):
    def __init__(self, gid, time_limit, users, puzzle_database):
        self.gid = gid
        self.time_limit = time_limit
        self.solved = False
        self.solved_count = 0

        self.users = users
        self.users_index = dict()
        for i, user in enumerate(self.users):
            self.users_index[user.uid] = user
            user.game_name = 'Player %d' % (i + 1)

        # load puzzle database
        self.puzzles = list()
        g = 0
        for puzzle in puzzle_database.puzzles:
            p = 0
            scrambles = list()
            for s in puzzle.scrambles:
                jumble = puzzle_database.jumbles[s.name]
                scrambl = scramble.puzzle.Scramble('%sp%ds%d' % (gid, g, p),
                        str(p + 1), jumble.value, jumble.jumble)
                scrambl.indices = s.keys
                if p > 0:
                    scrambl.prev_scramble = scrambles[-1]
                    scrambl.prev_scramble.next_scramble = scrambl
                scrambl.mystery = s.mystery
                if scrambl.mystery:
                    # reset because it will be filled with key letters
                    scrambl.scramble = ''
                scrambles.append(scrambl)
                p = p + 1

            pzl = scramble.parser.Puzzle(puzzle.name, puzzle.seconds, scrambles)
            self.puzzles.append(pzl)
            
            g = g + 1

        self.scrambles_index = dict()
        for puzzle in self.puzzles:
            for scrambl in puzzle.scrambles:
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
            user.scramble = DUMMY_SCRAMBLE

    def all_users_ready(self):
        for user in self.users:
            if user.scramble == DUMMY_SCRAMBLE:
                return False
        return True

    def user_ready(self, uid):
        user = self.get_user(uid)
        user.scramble = self.puzzles[self.puzzle].scrambles[0]
        # timer for first puzzle starts when all users are ready
        self.start = time.time()

    def timer(self):
        try:
            elapsed = int(time.time() - self.start)
            return self.puzzles[self.puzzle].seconds - elapsed
        except IndexError:
            return 0

    def get_scramble(self, pid):
        return self.scrambles_index[pid]

    def get_user(self, uid):
        return self.users_index[uid]

    def solve(self, pid, uid):
        scrambl = self.get_scramble(pid)
        if scrambl.solved is not None:
            return

        user = self.get_user(uid)
        scrambl.solve(user.game_name)
        mystery = self.puzzles[self.puzzle].scrambles[-1]
        for index in scrambl.indices:
            mystery.scramble += scrambl.value[index - 1]
        self.solved = mystery.solved is not None
        if self.solved:
            self.solved_count += 1
