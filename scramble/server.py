import BaseHTTPServer

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

class Puzzle(object):
    def __init__(self, definition):
        self.defintion = definition
        self.state = locked

    def to_json(self):
        state['word'] = obfuscate(definition.solution)
        state['scramble'] = definition.scramble
        state['state'] = self.state

class User(object):
    def __init__(self, userid):
        self.puzzle_id = 0
        pass

class Game(object):
    def __init__(self, gameid):
        self.puzzles = list()
        self.level = 0
        self.users = dict()
        pass

    def add_user(self, userid):
        pass

    def get_puzzle(self, userid):
        return puzzles[users[userid].puzzle_id]

    def change_puzzle(self, userid, direction):
        users[userid].change_puzzle(direction)

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

class ScrambleServer(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        if '/poll' == self.path:
            self._poll()
        elif self.path.endswith('.js'):
            self.load_js()
        elif self.path.endswith('.html'):
            self._html()
        else:
            self.send_error(500, 'Not implemented for %s' % self.path)

    def _poll(self):
        self.send_response(200)
        self.send_header('Content-type',    'application/json')
        self.end_headers()
        self.wfile.write('[1,2]')
        return

    def load_js(self):
        f = open('js/%s' % self.path)
        self.send_response(200)
        self.send_header('Content-type',    'application/javascript')
        self.end_headers()
        self.wfile.write(f.read())
        f.close()
        return

    def _html(self):
        f = open('html/%s' % self.path)
        self.send_response(200)
        self.send_header('Content-type',    'text/html')
        self.end_headers()
        self.wfile.write(f.read())
        f.close()
        return

def run(server_class=BaseHTTPServer.HTTPServer,
        handler_class=BaseHTTPServer.BaseHTTPRequestHandler):
        server_address = ('', 8001)
        httpd = server_class(server_address, handler_class)
        httpd.serve_forever()

if __name__ == '__main__':
    run(handler_class=ScrambleServer)
