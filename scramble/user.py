import json

class User(object):
    def __init__(self, uid, real_name):
        self.uid = uid
        self.real_name = real_name
        self.pay_type = None
        self.game_name = 'Undefined'
        self.scramble = None
        self.game = None
        self.mystery_solver = False
