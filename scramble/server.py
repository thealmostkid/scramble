import BaseHTTPServer
import cgi
import urlparse
import random
import json

import scramble.game
import scramble.user


# POST /login?user=someone - redirects to lobby.  Cookie?
# GET /lobby - returns lobby js code.
#       lobby.js shows pending game info and polls server for start
# GET /game/id/user - returns current page for a given game.  polls for updates.
# PUT /game/id/user?switch=[left|right] - updates state for that user, for the
# game, and stores metrics
# Client js code detects when puzzle is solved.  Use simple cipher to
# obfuscate the puzzle

#
# puzzle.js(puzzle_url) - reads obfuscated word definition.  how to do final
# hidden puzzle?
# lobby.js

# GET /puzzle/puzzle_id - returns word definition

# login.html:
# form data to post to /login

# POST /login: redirects to /lobby/userid
# GET /lobby/userid returns lobby.js code for that userid.

# lobby.js:
# Prints "Hello.  Waiting for the puzzles to start...".  Polls /lobby/userid
# /lobby/userid returns empty or gameid

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

# POST /login
# read userid from form data.  Add userid to lobby state.
# redirect to /lobby/userid
# GET /lobby/userid returns gameid
# POST /game/gameid?user=userid returns puzzle.js for the userid

# GET /game/gameid/userid returns json

games = dict()

#class Game(object):
#    def __init__(self, gameid):
#        self.puzzles = list()
#        self.level = 0
#        self.users = dict()
#        pass
#
#    def add_user(self, userid):
#        pass
#
#    def get_puzzle(self, userid):
#        return puzzles[users[userid].puzzle_id]
#
#    def change_puzzle(self, userid, direction):
#        users[userid].change_puzzle(direction)

class Engine(object):
    def __init__(self):
        games = dict()

    def get_game(self, gameid):
        return games[gameid]

    def new_game(self):
        gid = new_id()
        games[gid] = Game(gid)

class Lobby(object):
    # TODO: how are conditions specified?
    def create_user(self, userid):
        self.users = dict()
        pass

    def check_userid(self, userid):
        # conditions not met
        if False:
            return None
        else:
            return Game()

def MakeHandlerClassFromArgv(game):
    '''
    Class Factory to wrap variables in Custom Handler.
    '''
    class ScrambleServer(BaseHTTPServer.BaseHTTPRequestHandler, object):

        def do_GET(self):
            paths = dict()
            paths['poll'] = self.poll_get
            paths['game'] = self.do_GET_game
    
            incoming = urlparse.urlparse(self.path)
            qs = urlparse.parse_qs(incoming.query)
            print 'qs = %s' % qs
    
            path_parts = incoming.path.split('/')
            while path_parts[0] == '':
                path_parts.pop(0)
    
            print 'PARTS %s' % path_parts
            if path_parts[0] in paths:
                paths[path_parts[0]](path_parts, qs)
            elif incoming.path.endswith('.js'):
                self.load_js(incoming.path, qs)
            elif incoming.path.endswith('.html'):
                self._html(path_parts, qs)
            else:
                self.send_error(500, 'Get not implemented for %s' % incoming.path)
       
        #
        # game API
        #
        def do_GET_game_status(self, path_parts, params):
            gid = path_parts[1]

            # list of each user
            values = {'timer': game.timer()}
            users = list()
            for user in game.users:
                users.append({'name': user.uid,
                    'puzzle': user.puzzle.pid})
            values['users'] = users
            print 'Status = "%s"' % values
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write('%s' % json.dumps(values))
            return

# GET /game/<gid> - get game status (json)
        def do_GET_game(self, path_parts, params):
            '''
            Entry point for all GET endpoints for /game/<gid>
            '''
            print 'GAMING IT on %s' % path_parts
            assert(path_parts[0] == 'game')
            if len(path_parts) < 2:
                self.send_error(404, 'Game id is missing')
                return

            gid = path_parts[1]
            if gid != game.gid:
                self.send_error(404, 'Unknown game id %s' % gid)
                return

            if len(path_parts) == 2:
                return self.do_GET_game_status(path_parts, params)

            action = path_parts[2]
            if action == 'user':
                return self.do_GET_game_user(path_parts, params)
            elif action == 'puzzle':
                return self.do_GET_game_puzzle(path_parts, params)
            else:
                self.send_error(404)
            return

# GET /game/<gid>/puzzle/<pid>
        def do_GET_game_puzzle(self, path_parts, params):
            '''
            GET endpoint for /game/<gid>/puzzle/<pid>
            '''
            if len(path_parts) < 4:
                self.send_error(404, 'Invalid request for "%s"' %
                        '/'.join(path_parts))
                return

            assert(path_parts[2] == 'puzzle')
            gid = path_parts[1]
            if gid != game.gid:
                self.send_error(404, 'Unknown game id %s' % gid)
                return
            pid = path_parts[3]
            try:
                puzzle = game.get_puzzle(pid)
            except KeyError:
                self.send_error(404, 'Unknown puzzle "%s"' % pid)
                return

            values = {'scramble': puzzle.scramble(),
                    'solved': puzzle.solved,
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
            gid = path_parts[1]
            if gid != game.gid:
                self.send_error(404, 'Unknown game id %s' % gid)
                return
            uid = path_parts[3]
            try:
                user = game.get_user(uid)
            except KeyError:
                self.send_error(404, 'Unknown userid "%s"' % uid)
                return

            source_file = 'html/puzzle.html'
            try:
                f = open(source_file)
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                for line in f:
                    if 'LOCAL' in line:
                        values = {
                                'pid': user.puzzle.pid,
                                'uid': user.uid,
                                'gid': game.gid,
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
            paths['game'] = self.do_POST_game
    
            incoming = urlparse.urlparse(self.path)
            path_parts = incoming.path.split('/')
            while path_parts[0] == '':
                path_parts.pop(0)
    
            print "======= POST STARTED ======="
            print self.headers
            form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={'REQUEST_METHOD':'POST',
                        'CONTENT_TYPE':self.headers['Content-Type'],
                        })
            print "======= POST VALUES ======="
            for item in form.list:
                print '%s\n' % item
            qs = dict()
            for key in form.keys():
                value = form.getvalue(key)
                if type(value) != type(list()):
                    value = [value]
                qs[key] = value
    
            print 'qs = %s' % qs
            if path_parts[0] in paths:
                return paths[path_parts[0]](path_parts, qs)
            else:
                self.send_error(404, 'Post not implemented for %s' % self.path)
            return

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

            if path_parts[1] == 'create':
                return self.do_POST_game_create(path_parts, params)

            if len(path_parts) < 3:
                self.send_error(404)
                return

            command = path_parts[2]
            if 'puzzle' == command:
                return self.do_POST_game_puzzle(path_parts, params)
            elif 'user' == command:
                return self.do_POST_game_user(path_parts, params)
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
            if gid != game.gid:
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
            assert(gid == game.gid)

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
            print 'Guess string = "%s"' % guess
            print 'correct ?%s' % puzzle.guess(guess)
            guess_message = 'Guess "%s" is ' % guess

            uid = params['uid'][0]
            if puzzle.guess(guess):
                puzzle.solve(uid)
                guess_message += 'correct'
            else:
                guess_message += 'incorrect'
            # TODO: put gid, uid into params
            params['message'] = [guess_message]
            path = ['game', gid, 'user', uid]
            return self.do_GET_game_user(path, params)
    
        def poll_get(self, path_parts, params):
            self.send_response(200)
            self.send_header('Content-type',    'application/json')
            self.end_headers()
            self.wfile.write('[1,2]')
            return
    
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

    return ScrambleServer

def run(server_class=BaseHTTPServer.HTTPServer,
        handler_class=BaseHTTPServer.BaseHTTPRequestHandler):
    server_address = ('', 8001)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

if __name__ == '__main__':
    users = list()
    for i in xrange(2):
        users.append(scramble.user.User('u%d' % i))
    game = scramble.game.Game('g1', users)
    HandlerClass = MakeHandlerClassFromArgv(game)
    run(handler_class=HandlerClass)
