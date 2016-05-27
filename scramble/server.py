import BaseHTTPServer
import cgi
import json
import time
import urlparse

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
        def dump_scramble(self, scramble, scramble_type, output):
            output.write('<tr>')
            output.write('<td>%s</td>' % scramble_type)
            output.write('<td>%s</td>' % scramble[0])
            output.write('<td>')
            if len(scramble) > 1:
                output.write(scramble[1])
            output.write('</td>')

            output.write('<td>')
            if len(scramble) > 2:
                output.write(','.join([str(indx) for indx in scramble[2]]))
            output.write('</td>')

            output.write('</tr>')

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
                for puzzle in engine.puzzle_database:
                    self.wfile.write('<table border=1>')
                    for j in xrange(len(puzzle) - 1):
                        scramble = puzzle[j]
                        self.dump_scramble(scramble, 'puzzle', self.wfile)
                    scramble = puzzle[-1]
                    self.dump_scramble(scramble, 'mystery', self.wfile)
                    self.wfile.write('</table>')
                self.wfile.write('<form action="/admin/puzzles" method="post" enctype="multipart/form-data">')
                self.wfile.write('<input type="file" name="puzzles_file" id="puzzles_file">')
                self.wfile.write('<input type="submit" value="Upload">')
                self.wfile.write('</form>')
                self.wfile.write('</body></html>')

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
                        values = {'uid': user.uid}
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
        def do_GET_user(self, path_parts, params):
            assert(path_parts[0] == 'user')
            uid = path_parts[1]
            try:
                user = engine.user(uid)
            except KeyError:
                self.send_error(404, 'Cannot find user id "%s"' % uid)
                return
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            values = {'name': user.real_name, 'uid': user.uid}
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
                state = 'solved'
            elif time_remaining <= 0:
                state = 'expired'
            values = {'timer': time_remaining if time_remaining > 0 else 0,
                    'state': state}
            users = list()
            for user in game.users:
                users.append({'name': user.uid,
                    'mystery': user.mystery_solver,
                    'puzzle': user.puzzle.pretty_name})
            values['users'] = users
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write('%s' % json.dumps(values))
            return

# GET /game/<gid>/puzzle/<pid>
        def do_GET_game_puzzle(self, path_parts, params):
            '''
            GET endpoint for /game/<gid>/user/<uid>/puzzle/<pid>
            '''
            if len(path_parts) < 6:
                self.send_error(404, 'Invalid request for "%s"' % '/'.join(path_parts))
                return

            assert(path_parts[4] == 'puzzle')
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
                puzzle = game.get_puzzle(pid)
            except KeyError:
                self.send_error(404, 'Unknown puzzle "%s"' % pid)
                return

            values = {'scramble': puzzle.scramble,
                    'solved': puzzle.solved,
                    'hidden': (puzzle.pid == 'r0m' and not user.mystery_solver),
                    'message': puzzle.message}
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
                if action == 'puzzle':
                    return self.do_GET_game_puzzle(path_parts, params)
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

            if not game.completed():
                source_file = 'html/puzzle.html'
            else:
                source_file = 'html/credits.html'

            try:
                f = open(source_file)
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                for line in f:
                    if 'LOCAL' in line:
                        values = {
                                'pid': user.puzzle.pid,
                                'puzzle_name': user.puzzle.pretty_name,
                                'uid': user.uid,
                                'gid': game.gid,
                                'puzzle_len': len(user.puzzle.value),
                                'puzzle_indices': user.puzzle.indices
                                }
                        if user.puzzle.next_puzzle is not None:
                            values['next'] = user.puzzle.next_puzzle.pid
                        else:
                            values['next'] = None
                        if user.puzzle.prev_puzzle is not None:
                            values['previous'] = user.puzzle.prev_puzzle.pid
                        else:
                            values['previous'] = None

                        self.wfile.write('var local=%s;\n' % json.dumps(values))
                        if 'message' in params:
                            self.wfile.write('var message=%s;\n' % json.dumps(params['message'][0]))
                    else:
                        self.wfile.write(line)
                f.close()
            except IOError:
                self.send_error(501, 'failed to load %s' % source_file)
                return
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
                    engine.puzzle_database = scramble.puzzle.parse(params['puzzles_file'][0].split('\n'))
                except Exception as e:
                    self.send_error(400, 'Invalid puzzle list')
                    self.wfile.write('<h3>File Error:</h3><p><i>%s</i></p>' % e)
                    self.wfile.write('<a href="/admin/puzzles">Back</a>')
                    return
                parts = ['admin', 'puzzles']
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
            if 'puzzle' == command:
                return self.do_POST_game_puzzle(path_parts, params)
            elif 'user' == command:
                return self.do_POST_game_user(path_parts, params)
            elif 'advance' == command:
                return self.do_POST_game_advance(path_parts, params)
            else:
                self.send_error(404)
                return

# POST /game/<gid>/user/<uid>?action=next_puzzle - change user puzzle
        def do_POST_game_user(self, path_parts, params):
            if len(path_parts) < 4:
                self.send_error(404)
                return

            assert(path_parts[0] == 'game')
            assert(path_parts[2] == 'user')

            if 'puzzle' not in params:
                self.send_error(404)
                return
            puzzle_change = params['puzzle'][0]

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

            if puzzle_change == 'next':
                if user.puzzle.next_puzzle is not None:
                    user.puzzle = user.puzzle.next_puzzle
            elif puzzle_change == 'prev':
                if user.puzzle.prev_puzzle is not None:
                    user.puzzle = user.puzzle.prev_puzzle
            else:
                self.send_error(404,
                        'Unknown puzzle action: "%s"' % puzzle_change)
                return
            path = ['game', gid, 'user', uid]
            engine.record_stat(time.time(), 'puzzle_start', user.puzzle.pid,
                    user.uid)
            return self.do_GET_game_user(path, params)

# POST /game/<gid>/puzzle/<pid> - guess puzzle
        def do_POST_game_puzzle(self, path_parts, params):
            if len(path_parts) < 4:
                self.send_error(404)
                return

            assert(path_parts[0] == 'game')
            assert(path_parts[2] == 'puzzle')

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
                puzzle = game.get_puzzle(pid)
            except KeyError:
                self.send_error(404, 'Unknown puzzle "%s"' % pid)
                return

            keys = sorted([key for key in params.keys() if key.startswith('l')])
            guess = ''
            for key in keys:
                for char in params[key]:
                    guess += char
            guess_message = 'Guess "%s" is ' % guess

            uid = params['uid'][0]
            engine.record_stat(time.time(), 'puzzle_guess', pid, uid)

            if puzzle.guess(guess):
                game.solve(pid, uid)
                engine.record_stat(time.time(), 'puzzle_solve', pid, uid)
                if game.solved:
                    engine.record_stat(time.time(), 'round_solve', game.gid,
                            game.group)
                guess_message += 'correct'
            else:
                guess_message += 'incorrect'
            # TODO: put gid, uid into params
            params['message'] = [guess_message]
            path = ['game', gid, 'user', uid]
            return self.do_GET_game_user(path, params)

   # POST /game/<gid>/advance - guess puzzle
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
                engine.record_stat(time.time(), 'round_expired', game.gid, game.group)
                restart = True

            if restart:
                # load next level
                game.start_group(game.group + 1)
                if not game.completed():
                    engine.record_stat(game.start, 'round_start', game.gid, game.group)
                    for user in game.users:
                        engine.record_stat(game.start, 'puzzle_start',
                                user.puzzle.pid, user.uid)

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
        handler_class=BaseHTTPServer.BaseHTTPRequestHandler):
    server_address = ('', SERVER_PORT)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

def main():
    engine = scramble.engine.Engine()
    for i in xrange(scramble.engine.REQUIRED_USER_COUNT):
        engine.create_user('faker')
    engine.poll_for_new_game()
    HandlerClass = MakeHandlerClassFromArgv(engine)
    run(handler_class=HandlerClass)

if __name__ == '__main__':
    main()
