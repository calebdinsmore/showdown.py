from collections import deque
from . import utils, user

class Room:
    def __init__(self, room_id, client=None, max_logs=5000):
        self.id = room_id
        self.logs = deque(maxlen=max_logs)
        self.userlist = {}
        self.client = client
        self.title = None

    def __eq__(self, other):
        return isinstance(other, Room) and self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.title)

    def add_content(self, content):
        self.logs.append(content)
        inp_type, params = utils.parse_text_input(content)
        self.update(inp_type, *params)

    def add_user(self, user_str):
        new_user = user.User(user_str, client=self.client)
        self.userlist[new_user.id] = new_user

    def remove_user(self, user_id):
        self.userlist.pop(user_id, None)

    def update(self, inp_type, *params):
        #Title set
        if inp_type == 'title':
            self.title = params[0]

        #Userlist init
        if inp_type == 'users':
            user_strs = params[0].split(',')[1:]
            for user_str in user_strs:
                self.add_user(user_str)

        #User name change
        elif inp_type == 'n':
            user_str, old_id = params
            self.remove_user(old_id)
            self.add_user(user_str)

        #User leave
        elif inp_type == 'l':
            user_id = utils.name_to_id(params[0])
            self.remove_user(user_id)

        #User join
        elif inp_type == 'j':
            user_str = params[0]
            self.add_user(user_str)

    @utils.require_client
    async def request_auth(self, client=None):
        await client.add_output('{}|/roomauth'.format(self.id))

    @utils.require_client
    async def say(self, content, client=None):
        await client.say(self.id, content)

    @utils.require_client
    async def join(self, client=None):
        await client.join(self.id)

    @utils.require_client
    async def leave(self, client=None):
        await client.leave(self.id)

class Battle(Room):
    def __init__(self, room_id, client=None, max_logs=5000):
        Room.__init__(self, room_id, client=client, max_logs=max_logs)
        self.rules = []
        self.players = {
            'p1': None,
            'p2': None
        }
        self.rated = False
        self.ended = False
        self.tier = None
        self.winner, self.loser = None, None
        self.winner_id, self.loser_id = None, None

    def update(self, inp_type, *params): #TODO: Fix this up
        Room.update(self, inp_type, *params)
        if inp_type == 'player':
            player_id, name = params[0], params[1]
            self.players[player_id] = user.User(name, client=self.client)
        elif inp_type == 'rated':
            self.rated = True
        elif inp_type == 'tier':
            self.tier = utils.name_to_id(params[0])
        elif inp_type == 'rule':
            self.rules.append(params[0])
        elif inp_type == 'win': #TODO: definitely clean this up
            winner_name = params[0]
            if self.players['p1'].name_matches(winner_name):
                self.winner = self.players['p1']
                self.winner_id = 'p1'
                self.loser = self.players['p2']
                self.loser_id = 'p2'
            elif self.players['p2'].name_matches(winner_name):
                self.winner = self.players['p2']
                self.winner_id = 'p2'
                self.loser = self.players['p1']
                self.loser_id = 'p1'
            self.ended = True

    @utils.require_client
    async def save_replay(self, client=None):
        await client.save_replay(self.id)
        
    @utils.require_client
    async def forfeit(self, client=None):
        await client.forfeit(self.battle_id)

    @utils.require_client
    async def set_timer_on(self, client=None):
        pass

    @utils.require_client
    async def set_timer_off(self, client=None):
        pass

    @utils.require_client
    async def switch(self, client=None)
        pass #["battle-gen7randombattle-847809604|/choose switch 5|68"]

    @utils.require_client
    async def move(self, client=None)
        pass

    @utils.require_client
    async def undo(self, client=None)
        pass

class_map = {
    'chat': Room,
    'battle': Battle
}