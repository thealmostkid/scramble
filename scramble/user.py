import json

class User(object):
    def __init__(self, uid, real_name):
        self.uid = uid
        self.real_name = real_name
        self.puzzle = None
        self.gid = None

    def join_game(self, gid):
        self.gid = gid

    def to_JSON(self):
        values = {'name': self.uid, 'puzzle': self.puzzle.pid}
        return json.dumps(values)
