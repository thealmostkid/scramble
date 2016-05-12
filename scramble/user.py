import json

class User(object):
    def __init__(self, uid, real_name):
        self.uid = uid
        self.real_name = real_name
        self.puzzle = None
        self.game = None
        self.mystery_solver = False
