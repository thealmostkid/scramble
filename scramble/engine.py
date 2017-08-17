import random
import time

import scramble.game
import scramble.parser
import scramble.user

GID_PREFIX = 'g'

adjectives = [
'admiring',
'adoring',
'agitated',
'amazing',
'angry',
'awesome',
'backstabbing',
'berserk',
'big',
'boring',
'clever',
'cocky',
'compassionate',
'condescending',
'cranky',
'desperate',
'determined',
'distracted',
'dreamy',
'drunk',
'ecstatic',
'elated',
'elegant',
'evil',
'fervent',
'focused',
'furious',
'gigantic',
'gloomy',
'goofy',
'grave',
'happy',
'high',
'hopeful',
'hungry',
'insane',
'jolly',
'jovial',
'kickass',
'lonely',
'loving',
'mad',
'modest',
'naughty',
'nauseous',
'nostalgic',
'pedantic',
'pensive',
'prickly',
'reverent',
'romantic',
'sad',
'serene',
'sharp',
'sick',
'silly',
'sleepy',
'small',
'stoic',
'stupefied',
'suspicious',
'tender',
'thirsty',
'tiny',
'trusting',
]

names = [
'Adams',
'Alexander',
'Aquinas',
'Aristotle',
'Arthur',
'Augustine',
'Augustus',
'Bach',
'Bacon',
'Beethoven',
'Bismarck',
'Caesar',
'Calvin',
'Charlemagne',
'Charles',
'Churchill',
'Cicero',
'Cleveland',
'Columbus',
'Constantine',
'Cook',
'Copernicus',
'Cromwell',
'Dante',
'Darwin',
'David',
'Descartes',
'Dickens',
'Edison',
'Einstein',
'Elizabeth',
'Elvis',
'Franklin',
'Freud',
'Galileo',
'George',
'Goethe',
'Grant',
'Hamilton',
'Henry',
'Jackson',
'James',
'Jefferson',
'Joan',
'Kant',
'Kennedy',
'Khan',
'Lenin',
'Leonardo',
'Lincoln',
'Linnaeus',
'Locke',
'Louis',
'Luther',
'Madison',
'Marx',
'Michelangelo',
'Mozart',
'Napoleon',
'Newton',
'Nietzsche',
'Nixon',
'Paul',
'Peter',
'Plato',
'Poe',
'Reagan',
'Roosevelt',
'Rousseau',
'Shakespeare',
'Socrates',
'Stalin',
'Tchaikovsky',
'Tesla',
'Truman',
'Twain',
'Victoria',
'Vincent',
'Voltaire',
'Wagner',
'Washington',
'Wilde',
'Woodrow',
]

MYSTERY_ALGOS = [ 'random', 'rotate', 'high' ]
COND_SAME_VARIABLE ='samevariable'
COND_SAME_FIXED = 'samefixed'
COND_MIXED_VARIABLE = 'mixedvariable'
COND_MIXED_FIXED = 'mixfixed'
COND_FIXED = 'fixed'
COND_VARIABLE = 'variable'
PAY_CONDITIONS = [
    COND_SAME_VARIABLE,
    COND_SAME_FIXED,
    COND_MIXED_VARIABLE,
    COND_MIXED_FIXED,
    COND_FIXED,
    COND_VARIABLE
    ]
PAY_VARIABLE = 'Variable'
PAY_FIXED = 'Fixed'

class Engine(object):
    def __init__(self, pay_condition):
        self.pay_condition = pay_condition.lower()
        if self.pay_condition not in PAY_CONDITIONS:
            raise ValueError('Unknown pay condition "%s"' % pay_condition)
        self.games = dict()
        self.users = dict()
        self.stats = list()

        # configurable:
        self.puzzle_database = scramble.parser.parse(scramble.puzzle.DEFAULT)
        self.time_limit = 60 * 7
        self.required_user_count = 3
        self.survey_url = '/survey'
        self.mystery_algo = MYSTERY_ALGOS[0]
        self.game_count = 0

    def user(self, uid):
        return self.users[uid]

    def create_user(self, real_name):
        uid = '%d' % random.randint(0, 100000)
        user = scramble.user.User(uid, real_name)
        self.users[uid] = user
        return user

    def poll_for_new_game(self):
        pending_users = [user for (uid, user) in self.users.items() if
                user.game is None]
        if len(pending_users) >= self.required_user_count:
            self.create_game(pending_users[0:self.required_user_count])
            self.poll_for_new_game()

    def game(self, gid):
        return self.games[gid]

    def _select_mystery_solver(self, user_list):
        # TODO: implement mystery selection
        return user_list[0]

    def _game_time_limit(self):
        # seven minutes
        return self.time_limit

    def _select_pay_type(self, user_list):
        '''Updates the pay types for each user in the list.

        user_list: set of users to modify pay type.
        '''
        # Same Variable
        if self.pay_condition == COND_SAME_VARIABLE:
            for user in user_list:
                if user.mystery_solver:
                    user.pay_type = PAY_VARIABLE
                else:
                    user.pay_type = PAY_FIXED
        # Same Fixed
        elif self.pay_condition == COND_SAME_FIXED:
            for user in user_list:
                if user.mystery_solver:
                    user.pay_type = PAY_FIXED
                else:
                    user.pay_type = PAY_VARIABLE
        # Mixed Variable
        elif self.pay_condition == COND_MIXED_VARIABLE:
            count = 0
            for user in user_list:
                if user.mystery_solver:
                    user.pay_type = PAY_VARIABLE
                    continue
                elif count % 2 == 1:
                    user.pay_type = PAY_VARIABLE
                else:
                    user.pay_type = PAY_FIXED
                count += 1
        # Mixed Fixed
        elif self.pay_condition == COND_MIXED_FIXED:
            count = 0
            for user in user_list:
                if user.mystery_solver:
                    user.pay_type = PAY_FIXED
                    continue
                elif count % 2 == 1:
                    user.pay_type = PAY_VARIABLE
                else:
                    user.pay_type = PAY_FIXED
                count += 1
        # Fixed
        elif self.pay_condition == COND_FIXED:
            for user in user_list:
                user.pay_type = PAY_FIXED
        # Variable
        elif self.pay_condition == COND_VARIABLE:
            for user in user_list:
                user.pay_type = PAY_VARIABLE
        else:
            raise ValueError('Cannot assign pay for condition "%s"' % self.pay_condition)
        for user in user_list:
            self.record_stat(time.time(), 'pay_type', user.uid, user.pay_type)

    def create_game(self, user_list):
        '''Creates a game with the given list of users.

        Users can only belong to a single game at a time.
        user_list: list of User objects to join the game.
        return: New game object.
        raises:
            ValueError - if a user is already in a list.
            ValueError - if the user_list is too small.
        '''
        if len(user_list) != self.required_user_count:
            raise ValueError('Wrong number of users for a game (got %d, expected %d)' %
                    (len(user_list), self.required_user_count))

        for user in user_list:
            if user.game is not None:
                raise ValueError('User %s already in game %s' % (user.uid,
                    user.game.gid))

        indx = 0
        while '%s%d' % (GID_PREFIX, indx) in self.games:
            indx += 1

        gid = '%s%d' % (GID_PREFIX, indx)
        game = scramble.game.Game(gid, self._game_time_limit(), user_list,
                self.puzzle_database)
        self.games[gid] = game
        for user in user_list:
            user.game = game
        mystery_user = self._select_mystery_solver(user_list).mystery_solver = True
        self._select_pay_type(user_list)
        for user in user_list:
            self.record_stat(game.start, 'game_name', user.game_name, user.uid)
            if user.mystery_solver:
                self.record_stat(game.start, 'mystery_solver', game.gid,
                        user.uid)
            else:
                self.record_stat(game.start, 'regular_solver', game.gid,
                        user.uid)

        self.record_stat(game.start, 'puzzle_start', game.gid, game.puzzle)

        return game

    def record_stat(self, timestamp, event_name, item, value):
        self.stats.append(['%d' % timestamp, str(event_name), str(item), str(value)])

def main():
    fail_count = 0

    # variable

    for user_count in [3, 5, 6]:
        for cond in PAY_CONDITIONS:
            print '------ %s -------' % cond
            e = Engine(cond)
            user_list = [e.create_user('%d' % i) for i in range(0, user_count)]
            user_list[1].mystery_solver = True
            e._select_pay_type(user_list)
            for user in user_list:
                print '%s, %s, %s' % (user.real_name, user.pay_type, user.mystery_solver)

    try:
        e = Engine('BadCond')
        print 'Fail constructor bad cond'
        fail_count += 1
    except ValueError as ve:
        print 'Passed'

    try:
        e = Engine(COND_VARIABLE)
        e.pay_condition = 'Foobar'
        e._select_pay_type(user_list)
        print 'Fail pay_type bad cond'
        fail_count += 1
    except ValueError as ve:
        print 'Passed'

    return fail_count

if __name__ == '__main__':
    exit(main())
