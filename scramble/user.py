import json

class User(object):
    def __init__(self, uid):
        self.puzzle = None
        self.uid = uid

    def to_JSON(self):
        values = {'name': self.uid, 'puzzle': self.puzzle.pid}
        return json.dumps(values)
