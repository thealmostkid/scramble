import random
import time

import scramble.game
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

class Engine(object):
    def __init__(self):
        self.games = dict()
        self.users = dict()
        self.stats = list()
        self.puzzle_database = scramble.puzzle.parse(
                scramble.puzzle.DEFAULT.split('\n'))
        self.time_limit = 60 * 2
        self.required_user_count = 3
        self.survey_url = 'http://localhost/'

    def user(self, uid):
        return self.users[uid]

    def create_user(self, real_name):
        uid = '%s-%s' % (adjectives[random.randint(0, len(adjectives) - 1)],
                names[random.randint(0, len(names) - 1)])
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
        return user_list[0]

    def _game_time_limit(self):
        # seven minutes
        return self.time_limit

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
        self._select_mystery_solver(user_list).mystery_solver = True

        self.record_stat(game.start, 'puzzle_start', game.gid, game.puzzle)
        for user in game.users:
            self.record_stat(game.start, 'scramble_start', user.scramble.pid,
                    user.uid)

        return game

    def record_stat(self, timestamp, event_name, item, value):
        self.stats.append(['%d' % timestamp, str(event_name), str(item), str(value)])
