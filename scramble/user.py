import json

class User(object):
    def __init__(self, userid):
        self.puzzleid = None
        self.userid = userid
        pass

    def to_JSON(self):
        values = {'name': self.userid, 'puzzle': self.puzzleid}
        return json.dumps(values)
