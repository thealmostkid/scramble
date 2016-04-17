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
            paths['puzzle'] = self.puzzle_get
            paths['poll'] = self.poll_get
            paths['game'] = self.game_get
    
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
    
        def do_POST(self):
            paths = dict()
            paths['puzzle'] = self.puzzle_post
    
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
                paths[path_parts[0]](path_parts, qs)
            else:
                self.send_error(404, 'Post not implemented for %s' % self.path)
    
        #
        # game API
        #
        def _game_status(self, path_parts, params):
            gid = path_parts[2]
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            # list of each user
            users = list()
            for user in game.users:
                users.append({'name': user.userid,
                    'puzzle': user.puzzleid})
            user_string = json.dumps(users)
            self.wfile.write('%s' % user_string)
            return

        def game_get(self, path_parts, params):
            print 'GAMING IT on %s' % path_parts
            if path_parts[1] == 'status':
                return self._game_status(path_parts, params)
            else:
                self.send_error(404)

        #
        # puzzle API
        #
        def puzzle_get(self, path_parts, params):
            '''
            Endpoint for loading puzzles.
            '''
            print 'Puzzle on %s' % params
            print 'puzzle Path parts %s' % path_parts
            print 'Game %s' % game
            assert(path_parts[0] == 'puzzle')
            if len(path_parts) < 2:
                # TODO send_404(msg)
                self.send_response(404)
                self.end_headers()
                self.wfile.write('Puzzle id is missing')
                return
    
            puzzle_id = path_parts[1]
            puzzle = game.get_puzzle(puzzle_id)
            try:
                f = open('html/puzzle.html')
                self.send_response(200)
                self.send_header('Content-type',    'text/html')
                self.end_headers()
                for line in f:
                    if 'LOCAL' in line:
                        # TODO: dump puzzle
                        self.wfile.write('var local=%s;\n' % puzzle.js_object())
                        if 'message' in params:
                            self.wfile.write('var message=%s;\n' % json.dumps(params['message'][0]))
                    else:
                        self.wfile.write(line)
                f.close()
            except IOError:
                self.send_response(404)
                return
            return
    
    
        def puzzle_post(self, path_parts, params):
            print 'Guess on %s' % params
            puzzle_id = path_parts[1]
            puzzle = game.get_puzzle(puzzle_id)
            # TODO: error checking!!!

            keys = sorted([key for key in params.keys() if key.startswith('l')])
            guess = ''
            for key in keys:
                for char in params[key]:
                    guess += char
            print 'Guess string = "%s"' % guess
            print 'correct ?%s' % puzzle.guess(guess)
            guess_message = 'Guess "%s" is ' % guess
            if puzzle.guess(guess):
                puzzle.solve()
                guess_message += 'correct'
            else:
                guess_message += 'incorrect'
            # TODO: put gid, uid into params
            params['message'] = [guess_message]
            return self.puzzle_get(['puzzle', puzzle_id], params)
    
        def poll_get(self, path_parts, params):
            self.send_response(200)
            self.send_header('Content-type',    'application/json')
            self.end_headers()
            self.wfile.write('[1,2]')
            return
    
        def load_js(self, url, params):
            f = open('js/%s' % self.path)
            self.send_response(200)
            self.send_header('Content-type',    'application/javascript')
            self.end_headers()
            self.wfile.write(f.read())
            f.close()
            return
    
        def _html(self, path_parts, params):
            f = open('html/%s' % path_parts[-1])
            self.send_response(200)
            self.send_header('Content-type',    'text/html')
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
    game = scramble.game.Game(users)
    HandlerClass = MakeHandlerClassFromArgv(game)
    run(handler_class=HandlerClass)
