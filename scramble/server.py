# box score on credits page
# server maintenance/uptime, etc
# no one can play until all have clicked start
# text editing
# survey on new screen
# more control of game layout

import BaseHTTPServer
import cgi
import json
import time
import urlparse
import operator

import scramble.engine
import scramble.puzzle

SERVER_PORT = 8001

# transition screen when game is locked

def MakeHandlerClassFromArgv(engine):
    '''
    Class Factory to wrap variables in Custom Handler.
    '''
    class ScrambleServer(BaseHTTPServer.BaseHTTPRequestHandler, object):

        def do_GET(self):
            paths = dict()
            paths['admin'] = self.do_GET_admin
            paths['game'] = self.do_GET_game
            paths['lobby'] = self.do_GET_lobby
            paths['user'] = self.do_GET_user

            incoming = urlparse.urlparse(self.path)
            qs = urlparse.parse_qs(incoming.query)
            path_parts = incoming.path.split('/')
            while len(path_parts) > 0 and path_parts[0] == '':
                path_parts.pop(0)

            if len(path_parts) == 0:
                path = ['login.html']
                self._html(path, qs)
                return
            elif path_parts[0] in paths:
                paths[path_parts[0]](path_parts, qs)
                return
            elif incoming.path.endswith('.js'):
                self.load_js(incoming.path, qs)
                return
            elif incoming.path.endswith('.html'):
                self._html(path_parts, qs)
                return
            elif incoming.path.endswith('.css'):
                self._css(path_parts, qs)
                return
            else:
                self.send_error(500, 'Get not implemented for %s' % incoming.path)
                return

        #
        # admin API
        #

# GET /admin/
        def do_GET_admin(self, path_parts, params):
            assert(path_parts[0] == 'admin')
            if len(path_parts) == 1:
                path = ['admin.html']
                self._html(path, params)
                return

            cmd = path_parts[1]
            if 'stats.csv' == cmd:
                self.send_response(200)
                self.send_header('Content-type', 'text/csv')
                self.end_headers()
                self.wfile.write('timestamp,event,value1,value2\n')
                for stat in engine.stats:
                    self.wfile.write('%s\n' % ','.join(stat))
                return
            elif 'puzzles' == cmd:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write('<html><body>')
                self.wfile.write('<a href="/admin">Back To Admin</a>')

                # upload
                self.wfile.write('<h2>Upload</h2>')
                self.wfile.write('<form action="/admin/puzzles" method="post" enctype="multipart/form-data">')
                self.wfile.write('<input type="file" name="puzzles_file" id="puzzles_file">')
                self.wfile.write('<input type="submit" value="Upload">')
                self.wfile.write('</form>')

                # write out jumbles
                self.wfile.write('<h2>Jumbles</h2>')
                self.wfile.write('<table border=1 cellpadding=5>')
                self.wfile.write('<tr><th>Name</th><th>Value</th><th>Jumble</th></tr>')
                for name in sorted(engine.puzzle_database.jumbles.keys()):
                    jumble = engine.puzzle_database.jumbles[name]
                    self.wfile.write('<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % \
                            (jumble.name, jumble.value, jumble.jumble))
                self.wfile.write('</table>')

                # write out puzzles
                self.wfile.write('<h2>Puzzles</h2>')
                self.wfile.write('<table border=2 cellpadding=1>')
                self.wfile.write('<tr><th>Name</th><th>Time Limit</th><th>Scrambles</th></tr>')
                for puzzle in engine.puzzle_database.puzzles:
                    self.wfile.write('<tr>')
                    self.wfile.write('<td>%s</td>' % puzzle.name)
                    self.wfile.write('<td>%g seconds</td>' % puzzle.seconds)
                    self.wfile.write('<td>')
                    self.wfile.write('<table border=1 cellpadding=5>')
                    self.wfile.write('<tr><td>Jumble Name</td><td>Keys</td><td>Mystery</td></tr>')
                    for _scramble in puzzle.scrambles:
                        self.wfile.write('<tr>')
                        self.wfile.write('<td>%s</td>' % _scramble.name)
                        self.wfile.write('<td>%s</td>' % ', '.join([str(key) for key in _scramble.keys]))
                        self.wfile.write('<td>%s</td>' % _scramble.mystery)
                        self.wfile.write('</tr>')
                    self.wfile.write('</table>')
                    self.wfile.write('</td>')
                    self.wfile.write('</tr>')
                self.wfile.write('</table>')

                self.wfile.write('<a href="/admin">Back To Admin</a>')
                self.wfile.write('</body></html>')
            elif 'config' == cmd:
                source_file = 'html/config.html'
                try:
                    f = open(source_file)
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    for line in f:
                        if 'LOCAL' in line:
                            mystery_algo = 0
                            for i in xrange(len(scramble.engine.MYSTERY_ALGOS)):
                                if engine.mystery_algo == scramble.engine.MYSTERY_ALGOS[i]:
                                    mystery_algo = i
                            values = {
                                    'time_limit': engine.time_limit,
                                    'group_size': engine.required_user_count,
                                    'game_count': 0,
                                    'survey': engine.survey_url,
                                    'solvers': scramble.engine.MYSTERY_ALGOS,
                                    'solver_index': mystery_algo,
                                    }
                            self.wfile.write('var local=%s;\n' % json.dumps(values))
                        else:
                            self.wfile.write(line)
                    f.close()
                except IOError:
                    self.send_error(501, 'failed to load %s' % source_file)
                    return
            elif 'status' == cmd:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write('<html><body>')
                self.wfile.write('<a href="/admin">Back To Admin</a>')
                self.wfile.write('<h1>Active games</h1>')
                self.wfile.write('<table border=1>')

                def dump_user(user, output):
                    output.write('<tr>')
                    output.write('<td>%s</td>' % user.uid)
                    output.write('<td>%s</td>' % user.real_name)
                    if user.scramble is not None:
                        output.write('<td>%s</td>' % user.scramble.pid)
                    else:
                        output.write('<td>None</td>')
                    output.write('<td>%s</td>' % user.mystery_solver)
                    output.write('<td>%s</td>' % user.pay_type)
                    output.write('</tr>')

                # active games
                for game in engine.games.values():
                    self.wfile.write('<tr>')
                    self.wfile.write('<th>Game %s (seconds remaining: %d)</th>' % (game.gid, game.timer()))
                    self.wfile.write('</tr>')

                    self.wfile.write('<tr><td>')
                    self.wfile.write('<table border=2>')
                    self.wfile.write('<tr><th>user</th><th>name</th><th>Scramble</th><th>mystery</th><th>pay type</th></tr>')
                    # users
                    for user in game.users:
                        dump_user(user, self.wfile)
                    self.wfile.write('</table>')
                    self.wfile.write('</td></tr>')

                    # scrambles
                    self.wfile.write('<tr><td>')
                    self.wfile.write('<table border=2>')
                    for i, puzzle in enumerate(game.puzzles):
                        self.wfile.write('<tr><th>Puzzle %s</th></tr>' % i)
                        self.wfile.write('<tr><th>scramble</th><th>name</th><th>mystery</th><th>solved</th></tr>')
                        for scrambl in puzzle:
                            self.wfile.write('<tr>')
                            self.wfile.write('<td>%s</td>' % scrambl.pid)
                            self.wfile.write('<td>%s</td>' % scrambl.pretty_name)
                            self.wfile.write('<td>%s</td>' % scrambl.mystery)
                            self.wfile.write('<td>%s</td>' % scrambl.solved)
                            self.wfile.write('</tr>')
                    self.wfile.write('</table>')
                    self.wfile.write('</td></tr>')

                self.wfile.write('</table>')

                # inactive users
                self.wfile.write('<h1>Waiting Users</h1>')
                self.wfile.write('<table border=1>')
                self.wfile.write('<tr><th>id</th><th>name</th><th>Scramble</th><th>mystery</th></tr>')
                for user in engine.users.values():
                    if user.game is None:
                        dump_user(user, self.wfile)
                self.wfile.write('</table>')

                self.wfile.write('<br>')
                self.wfile.write('<a href="/admin">Back To Admin</a>')
                self.wfile.write('</body></html>')
            elif 'solved' == cmd:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write('<html><body>')
                self.wfile.write('<a href="/admin">Back To Admin</a>')

                self.wfile.write('<table border=1>')
                self.wfile.write('<tr><th>Workstation ID</th><th>Scramble Sets Solved</th><th>Mystery Solver</th><th>Pay Type</th></tr>')
                for game in engine.games.values():
                    player_stats = self._solved_game_stats(game)
                    for stats in player_stats.values():
                        self.wfile.write('<tr><td>')
                        self.wfile.write(str(stats['real_name']))
                        self.wfile.write('</td><td>')
                        #self.wfile.write(str(stats['solved'] + stats['mystery']))
                        self.wfile.write(str(stats['sets']))
                        self.wfile.write('</td><td>')
                        for player in game.users:
                            if stats['real_name'] == player.real_name:
                                self.wfile.write(str(player.mystery_solver))
                        #self.wfile.write(str(stats['solved'] + stats['mystery']))
                        self.wfile.write('</td><td>')
                        self.wfile.write(str(stats['pay_type']))
                        self.wfile.write('</td></tr>')
                self.wfile.write('</table>')

                self.wfile.write('<a href="/admin">Back To Admin</a>')
                self.wfile.write('</body></html>')

            else:
                self.send_error(404)

        #
        # lobby API
        #
        def do_GET_lobby(self, path_parts, params):
            assert(path_parts[0] == 'lobby')
            uid = path_parts[1]
            try:
                user = engine.user(uid)
            except KeyError:
                self.send_error(404, 'Cannot find user id %s' % uid)
                return

            source_file = 'html/lobby.html'
            try:
                f = open(source_file)
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                for line in f:
                    if 'LOCAL' in line:
                        values = {
                                'uid': user.uid,
                                'game_name': user.game_name
                                }
                        self.wfile.write('var local=%s;\n' % json.dumps(values))
                    else:
                        self.wfile.write(line)
                f.close()
            except IOError:
                self.send_error(501, 'failed to load %s' % source_file)
                return
            return

        #
        # user API
        #
        def extract_user_stats(self, uid):
            results = { 'mystery_guesses': 0,
                    'mystery_solved': 0,
                    'mystery_keys': 0,
                    'regular_guesses': 0,
                    'regular_solved': 0,
                    'regular_keys': 0,
                    'puzzle_start': 0,
                    'puzzle_solve': 0,
                    'puzzle_failed': 0,
                    'attempted': 0 }
            stats = sorted([stat for stat in engine.stats if stat[3] == uid], key=operator.itemgetter(1))
            mystery = False
            gid = None
            for stat in stats:
                if stat[1] == 'mystery_solver':
                    mystery = True
                    gid = stat[2]
                elif stat[1] == 'regular_solver':
                    mystery = False
                    gid = stat[2]
                elif stat[1] == 'scramble_start':
                    results['attempted'] = results['attempted'] + 1
                elif stat[1] == 'scramble_guess':
                    if mystery:
                        results['mystery_guesses'] = results['mystery_guesses'] + 1
                    else:
                        results['regular_guesses'] = results['regular_guesses'] + 1
                elif stat[1] == 'scramble_solve':
                    if mystery:
                        results['mystery_solved'] = results['mystery_solved'] + 1
                    else:
                        results['regular_solved'] = results['regular_solved'] + 1
                elif stat[1] == 'scramble_keys':
                    if mystery:
                        results['mystery_keys'] = results['mystery_keys'] + int(stat[2])
                    else:
                        results['regular_keys'] = results['regular_keys'] + int(stat[2])
                else:
                    raise ValueError('unknown stat %s' % stat[1])

            assert(gid is not None)
            game_stats = sorted([stat for stat in engine.stats if stat[2] == gid], key=operator.itemgetter(1))
            for stat in game_stats:
                if stat[1] == 'puzzle_solve':
                    results['puzzle_solve'] = results['puzzle_solve'] + 1
                elif stat[1] == 'puzzle_expired':
                    results['puzzle_failed'] = results['puzzle_failed'] + 1
                elif stat[1] == 'puzzle_start':
                    results['puzzle_start'] = results['puzzle_start'] + 1
            return results

        def do_GET_user(self, path_parts, params):
            assert(path_parts[0] == 'user')
            uid = path_parts[1]
            try:
                user = engine.user(uid)
            except KeyError:
                self.send_error(404, 'Cannot find user id "%s"' % uid)
                return

            if len(path_parts) > 2:
                cmd = path_parts[2]
                if cmd == 'stats':
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    user_stats = self.extract_user_stats(uid)
                    self.wfile.write('%s' % json.dumps(user_stats))
                    return
                else:
                    self.send_error(404, 'Unknown user command: %s' % cmd)
                    return

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            values = {
                    'name': user.real_name,
                    'uid': user.uid,
                    'game_name': user.game_name,
                    }
            if user.game is not None:
                values['gid'] = user.game.gid
            else:
                values['gid'] = None
            self.wfile.write('%s' % json.dumps(values))
            return

        #
        # game API
        #
# GET /game/<gid> - get game status (json)
        def do_GET_game(self, path_parts, params):
            '''
            Entry point for all GET endpoints for /game/<gid>
            '''
            assert(path_parts[0] == 'game')
            if len(path_parts) < 2:
                self.send_error(404, 'Game id is missing')
                return

            gid = path_parts[1]
            try:
                game = engine.game(gid)
            except KeyError:
                self.send_error(404, 'Unknown game id %s' % gid)
                return

            if len(path_parts) == 2:
                return self.do_GET_game_status(path_parts, params)

            action = path_parts[2]
            if action == 'user':
                return self.do_GET_game_user(path_parts, params)
            elif action == 'results':
                return self.do_GET_game_results(path_parts, params)
            else:
                self.send_error(404)
            return

# GET /game/<gid>
        def do_GET_game_status(self, path_parts, params):
            gid = path_parts[1]
            try:
                game = engine.game(gid)
            except KeyError:
                self.send_error(404, 'Cannot find information for game id %s' % gid)
                return

            # list of each user
            time_remaining = game.timer()
            state = None
            if game.solved:
                state = '<b><u>Closed Scramble Solved!</u></b><br><br>Beginning next round.'
            elif time_remaining <= 0:
                state = '<b><u>Time expired.</u></b><br><br>Beginning next round.'
            player_stats = self._solved_puzzle_stats(game)

            values = {'timer': time_remaining if time_remaining > 0 else 0,
                    'state': state,
                    'player_stats': player_stats}
            users = list()
            for user in game.users:
                users.append({'name': user.game_name,
                    'mystery': user.mystery_solver,
                    'scramble': user.scramble.pretty_name if user.scramble is not None else ''})
            values['users'] = users
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write('%s' % json.dumps(values))
            return

# GET /game/<gid>/scramble/<pid>
        def do_GET_game_scramble(self, path_parts, params):
            '''
            GET endpoint for /game/<gid>/user/<uid>/scramble/<pid>
            '''
            if len(path_parts) < 6:
                self.send_error(404, 'Invalid request for "%s"' % '/'.join(path_parts))
                return

            assert(path_parts[4] == 'scramble')
            gid = path_parts[1]
            try:
                game = engine.game(gid)
            except KeyError:
                self.send_error(404, 'Unknown game id %s' % gid)
                return
            uid = path_parts[3]
            try:
                user = game.get_user(uid)
            except KeyError:
                self.send_error(404, 'Unknown userid "%s"' % uid)
                return

            pid = path_parts[5]
            try:
                scrambl = game.get_scramble(pid)
            except KeyError:
                self.send_error(404, 'Unknown scramble "%s"' % pid)
                return

            solvers = list()
            mystery_solver = ''
            for u in game.users:
                if scrambl.mystery:
                    if u.mystery_solver:
                        solvers.append(u.game_name)
                else:
                    solvers.append(u.game_name)
                if u.mystery_solver:
                    mystery_solver = u.game_name

            values = {
                    'scramble': scrambl.scramble,
                    'solved': scrambl.solved,
                    'hidden': (scrambl.mystery and not user.mystery_solver),
                    'message': scrambl.message,
                    'scramble_name': user.scramble.pretty_name if user.scramble is not None else '',
                    'solvers': ', '.join(solvers),
                    'mystery_solver': mystery_solver,
                    }
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write('%s' % json.dumps(values))
            return

# GET /game/<gid>/user/<uid> - get screen for user
        def do_GET_game_user(self, path_parts, params):
            '''
            GET endpoint for /game/<gid>/user/<uid>
            '''
            if len(path_parts) < 4:
                self.send_error(404, 'Invalid request for "%s"' %
                        '/'.join(path_parts))
                return

            assert(path_parts[2] == 'user')
            if len(path_parts) > 4:
                action = path_parts[4]
                if action == 'scramble':
                    return self.do_GET_game_scramble(path_parts, params)
                else:
                    self.send_error(404, 'Invalid action "%s"' %
                            '/'.join(path_parts))
                    return

            gid = path_parts[1]
            try:
                game = engine.game(gid)
            except KeyError:
                self.send_error(404, 'Unknown game id %s' % gid)
                return
            uid = path_parts[3]
            try:
                user = game.get_user(uid)
            except KeyError:
                self.send_error(404, 'Unknown userid "%s"' % uid)
                return

            if user.scramble == scramble.game.DUMMY_SCRAMBLE:
                game.user_ready(uid)
                engine.record_stat(time.time(), 'scramble_start',
                        user.scramble.pid, user.uid)

            if game.completed():
                return self.load_credits(game, user)
            elif not game.all_users_ready():
                return self.load_wait_screen(game, user)
            else:
                message = None
                if 'message' in params:
                    message = params['message'][0]
                return self.load_scramble(game, user, message)

        def load_wait_screen(self, game, user):
            try:
                f = open('html/wait_screen.html')
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                for line in f:
                    if 'LOCAL' in line:
                        values = {
                                'uid': user.uid,
                                'gid': game.gid,
                                'game_name': user.game_name,
                                }
                        self.wfile.write('var local=%s;\n' % json.dumps(values))
                    else:
                        self.wfile.write(line)
                f.close()
            except IOError:
                self.send_error(501, 'failed to load %s' % source_file)
                return
            return

        #########################################
        # Stats
        #########################################
        def _default_stats(self, game):
            # TODO: only the concluding puzzle/round
            players = dict()
            # stats:
            # solved
            # mystery solved
            # letters uncovered
            # list of puzzle ids
            default_stats = {
                    'name': 'Unknown',
                    'real_name': 'Unknown',
                    'is_mystery': False,
                    'pay_type': 'Unknown',
                    'solved': 0,
                    'mystery': 0,
                    'letters': 0,
                    'sets': 0,
                    'scrambles': None,
                    }
            for player in game.users:
                players[player.game_name] = dict(default_stats)
                players[player.game_name]['name'] = player.game_name
                players[player.game_name]['real_name'] = player.real_name
                players[player.game_name]['is_mystery'] = player.mystery_solver
                players[player.game_name]['pay_type'] = player.pay_type
            return players

        def _puzzle_stats(self, players, puzzle):
            for scrambl in puzzle.scrambles:
                if scrambl.solved is not None:
                    solver = scrambl.solved
                    if solver not in players:
                        players[solver] = dict(default_stats)
                    if scrambl.mystery:
                        players[solver]['mystery'] += 1
                    else:
                        players[solver]['solved'] += 1
                    players[solver]['letters'] += len(scrambl.indices)
                    if players[solver]['scrambles'] is None:
                        players[solver]['scrambles'] = list()
                    players[solver]['scrambles'].append(scrambl.pid)
            return players

        def _solved_puzzle_stats(self, game):
            players = self._default_stats(game)
            self._puzzle_stats(players, game.puzzles[game.puzzle])
            for stats in players.values():
                if game.solved:
                    # TODO: this is always 1
                    stats['sets'] = 1
            return players

        def _solved_game_stats(self, game):
            players = self._default_stats(game)
            for puzzle in game.puzzles:
                self._puzzle_stats(players, puzzle)
            for stats in players.values():
                stats['sets'] = game.solved_count
            return players

        def load_credits(self, game, user):
            try:
                f = open('html/credits.html')
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                for line in f:
                    if 'LOCAL' in line:
                        players = self._solved_game_stats(game)
                        values = {
                                'uid': user.uid,
                                'game_name': user.game_name,
                                'players': players,
                                'url': engine.survey_url,
                                }
                        self.wfile.write('var local=%s;\n' % json.dumps(values))
                    else:
                        self.wfile.write(line)
                f.close()
            except IOError:
                self.send_error(501, 'failed to load %s' % source_file)
                return
            return

        def load_scramble(self, game, user, message):
            try:
                f = open('html/scramble.html')
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                for line in f:
                    if 'LOCAL' in line:
                        values = {
                                'pid': user.scramble.pid,
                                'scramble_name': user.scramble.pretty_name,
                                'uid': user.uid,
                                'game_name': user.game_name,
                                'gid': game.gid,
                                'scramble_len': len(user.scramble.value),
                                'scramble_indices': user.scramble.indices,
                                'message': message,
                                }
                        if user.scramble.next_scramble is not None:
                            values['next'] = user.scramble.next_scramble.pid
                        else:
                            values['next'] = None
                        if user.scramble.prev_scramble is not None:
                            values['previous'] = user.scramble.prev_scramble.pid
                        else:
                            values['previous'] = None

                        self.wfile.write('var local=%s;\n' % json.dumps(values))
                        if message is not None:
                            self.wfile.write('var message=%s;\n' % json.dumps(message))
                    else:
                        self.wfile.write(line)
                f.close()
            except IOError:
                self.send_error(501, 'failed to load %s' % source_file)
                return
            return

# GET /game/<gid>/stats - get stats for this game
        def do_GET_game_results(self, path_parts, params):
            '''
            GET endpoint for /game/<gid>/results
            '''
            if len(path_parts) < 3:
                self.send_error(404, 'Invalid request for "%s"' %
                        '/'.join(path_parts))
                return

            assert(path_parts[2] == 'results')
            gid = path_parts[1]
            try:
                game = engine.game(gid)
            except KeyError:
                self.send_error(404, 'Unknown game id %s' % gid)
                return

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            results = []
            for puzzle in game.puzzles:
                for scrambl in puzzle:
                    results.append([scrambl.pid,
                        scrambl.solved,
                        len(scrambl.indices)])
            self.wfile.write('%s' % json.dumps(results))
            return

        #
        # POST
        #
        def do_POST(self):
            paths = dict()
            paths['admin'] = self.do_POST_admin
            paths['game'] = self.do_POST_game
            paths['user'] = self.do_POST_user

            incoming = urlparse.urlparse(self.path)
            path_parts = incoming.path.split('/')
            while path_parts[0] == '':
                path_parts.pop(0)

            form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={'REQUEST_METHOD':'POST',
                        'CONTENT_TYPE':self.headers['Content-Type'],
                        })
            qs = dict()
            for key in form.keys():
                value = form.getvalue(key)
                if type(value) != type(list()):
                    value = [value]
                qs[key] = value

            if path_parts[0] in paths:
                return paths[path_parts[0]](path_parts, qs)
            else:
                self.send_error(404, 'Post not implemented for %s' % self.path)
            return

        #
        # admin API
        #
        def do_POST_admin(self, path_parts, params):
            assert(path_parts[0] == 'admin')
            if len(path_parts) == 1:
                parts = ['admin']
                return self.do_GET_admin(parts, params)

            cmd = path_parts[1]
            if cmd == 'puzzles':
                try:
                    engine.puzzle_database = scramble.parser.parse(params['puzzles_file'][0])
                except Exception as e:
                    self.send_error(400, 'Invalid puzzle list')
                    self.wfile.write('<h3>File Error:</h3><p><i>%s</i></p>' % e)
                    self.wfile.write('<a href="/admin/puzzles">Back</a>')
                    raise e
                parts = ['admin', 'puzzles']
                return self.do_GET_admin(parts, params)
            elif cmd == 'config':
                errors = ''
                try:
                    time_limit = int(params['time_limit'][0])
                    if time_limit <= 0:
                        errors += 'Invalid time limit (%d)<br>' % time_limit
                    else:
                        engine.time_limit = time_limit
                except ValueError as ve:
                    errors += 'Invalid time limit (%s)<br>' % ve
                except KeyError:
                    errors += 'Missing time limit<br>'

                try:
                    user_count = int(params['group_size'][0])
                    if user_count <= 0:
                        errors += 'Invalid group size (%d)<br>' % user_count
                    else:
                        engine.required_user_count = user_count
                except ValueError as ve:
                    errors += 'Invalid group size (%s)<br>' % ve
                except KeyError:
                    errors += 'Missing group size<br>'

                try:
                    survey = params['survey'][0]
                    if len(survey) <= 0:
                        errors += 'Invalid survey url "%s"<br>' % survey
                    else:
                        engine.survey_url  = survey
                except KeyError:
                    errors += 'Missing survey url<br>'

                try:
                    algo = params['solver'][0]
                    if algo not in scramble.engine.MYSTERY_ALGOS:
                        errors += 'Invalid mystery solver selection "%s"' % algo
                    else:
                        engine.mystery_algo = algo
                except KeyError:
                    errors += 'Missing mystery solver selection<br>'

                # TODO: implement these
                #print 'GAME COUNT = %d' % int(params['game_count'][0])

                if len(errors) > 0:
                    self.send_error(400, 'Invalid configuration')
                    self.wfile.write('<h3><font color=red>Error:</font></h3><p><i>%s</i></p>' % errors)
                    self.wfile.write('<br><a href="/admin/config">Back</a>')
                    return

                parts = ['admin', 'config']
                return self.do_GET_admin(parts, params)
            else:
                self.send_error(404, 'Post admin not implemented for %s' % self.path)
                return

# POST /user/create - make a new user
        def do_POST_user(self, path_parts, params):
            assert(path_parts[0] == 'user')

            if path_parts[1] == 'create':
                if 'real-name' not in params:
                    self.send_error(404, 'real-name missing from create.')
                    return
                real_name = params['real-name'][0]
                user = engine.create_user(real_name)
                engine.record_stat(time.time(), 'user_create', real_name, user.uid)
                engine.poll_for_new_game()
                path = ['lobby', user.uid]
                return self.do_GET_lobby(path, params)

# POST /game/create - make new game

        def do_POST_game(self, path_parts, params):
            '''
            Entry point for all POST requests to game endpoints /game/<gid>.
            '''
            'POST GAME "%s" + "%s"' % (path_parts, params)
            assert(path_parts[0] == 'game')

            if len(path_parts) < 2:
                self.send_error(404)
                return

            if len(path_parts) < 3:
                self.send_error(404)
                return

            command = path_parts[2]
            if 'scramble' == command:
                return self.do_POST_game_scramble(path_parts, params)
            elif 'user' == command:
                return self.do_POST_game_user(path_parts, params)
            elif 'advance' == command:
                return self.do_POST_game_advance(path_parts, params)
            else:
                self.send_error(404)
                return

# POST /game/<gid>/user/<uid>?action=next_scramble - change user scramble
        def do_POST_game_user(self, path_parts, params):
            if len(path_parts) < 4:
                self.send_error(404)
                return

            assert(path_parts[0] == 'game')
            assert(path_parts[2] == 'user')

            if 'scramble' not in params:
                self.send_error(404)
                return
            scramble_change = params['scramble'][0]

            gid = path_parts[1]
            try:
                game = engine.game(gid)
            except KeyError:
                self.send_error(404, 'Unknown game id %s' % gid)
                return
            uid = path_parts[3]
            try:
                user = game.get_user(uid)
            except KeyError:
                self.send_error(404, 'Unknown userid "%s"' % uid)
                return

            if scramble_change == 'next':
                if user.scramble.next_scramble is not None:
                    user.scramble = user.scramble.next_scramble
            elif scramble_change == 'prev':
                if user.scramble.prev_scramble is not None:
                    user.scramble = user.scramble.prev_scramble
            else:
                self.send_error(404,
                        'Unknown scramble action: "%s"' % scramble_change)
                return
            path = ['game', gid, 'user', uid]
            engine.record_stat(time.time(), 'scramble_start', user.scramble.pid,
                    user.uid)
            return self.do_GET_game_user(path, params)

# POST /game/<gid>/scramble/<pid> - guess scramble
        def do_POST_game_scramble(self, path_parts, params):
            if len(path_parts) < 4:
                self.send_error(404)
                return

            assert(path_parts[0] == 'game')
            assert(path_parts[2] == 'scramble')

            if 'uid' not in params:
                self.send_error(404, 'Post request missing "uid"')
                return

            gid = path_parts[1]
            try:
                game = engine.game(gid)
            except KeyError:
                self.send_error(404, 'Unknown game id %s' % gid)
                return

            pid = path_parts[3]

            try:
                scrambl = game.get_scramble(pid)
            except KeyError:
                self.send_error(404, 'Unknown scramble "%s"' % pid)
                return

            keys = sorted([key for key in params.keys() if key.startswith('l')])
            guess = ''
            for key in keys:
                for char in params[key]:
                    guess += char
            guess_message = 'Guess "%s" is ' % guess

            uid = params['uid'][0]
            engine.record_stat(time.time(), 'scramble_guess', pid, uid)

            if scrambl.guess(guess):
                game.solve(pid, uid)
                ts = time.time()
                engine.record_stat(ts, 'scramble_solve', pid, uid)
                engine.record_stat(ts, 'scramble_keys',
                        len(game.get_scramble(pid).indices), uid)
                if game.solved:
                    engine.record_stat(ts, 'puzzle_solve', game.gid,
                            game.puzzle)
                guess_message += 'correct'
            else:
                guess_message += 'incorrect'
            params['message'] = [guess_message]
            path = ['game', gid, 'user', uid]
            return self.do_GET_game_user(path, params)

   # POST /game/<gid>/advance - guess scramble
        def do_POST_game_advance(self, path_parts, params):
            if len(path_parts) < 3:
                self.send_error(404)
                return

            assert(path_parts[0] == 'game')
            assert(path_parts[2] == 'advance')

            if 'uid' not in params:
                self.send_error(404, 'Post request missing "uid"')
                return

            gid = path_parts[1]
            try:
                game = engine.game(gid)
            except KeyError:
                self.send_error(404, 'Unknown game id %s' % gid)
                return

            restart = False
            if game.solved:
                restart = True
            elif game.timer() <= 0:
                engine.record_stat(time.time(), 'puzzle_expired', game.gid, game.puzzle)
                restart = True

            if restart:
                # load next level
                game.start_puzzle(game.puzzle + 1)
                if not game.completed():
                    engine.record_stat(game.start, 'puzzle_start', game.gid, game.puzzle)
                    for user in game.users:
                        engine.record_stat(game.start, 'scramble_start',
                                user.scramble.pid, user.uid)

            uid = params['uid'][0]
            path = ['game', gid, 'user', uid]
            return self.do_GET_game_user(path, params)

        def load_js(self, url, params):
            f = open('js/%s' % self.path)
            self.send_response(200)
            self.send_header('Content-type', 'application/javascript')
            self.end_headers()
            self.wfile.write(f.read())
            f.close()
            return

        def _html(self, path_parts, params):
            f = open('html/%s' % path_parts[-1])
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f.read())
            f.close()
            return

        def _css(self, path_parts, params):
            f = open('html/%s' % path_parts[-1])
            self.send_response(200)
            self.send_header('Content-type', 'text/css')
            self.end_headers()
            self.wfile.write(f.read())
            f.close()
            return

    return ScrambleServer

def run(server_class=BaseHTTPServer.HTTPServer,
        handler_class=BaseHTTPServer.BaseHTTPRequestHandler,
        port=SERVER_PORT):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

def main(engine, port):
    #for i in xrange(engine.required_user_count):
    #    engine.create_user('faker')
    engine.poll_for_new_game()
    HandlerClass = MakeHandlerClassFromArgv(engine)
    run(handler_class=HandlerClass, port=port)

if __name__ == '__main__':
    main(scramble.engine.Engine())
