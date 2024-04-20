class Game:
    players = {}
    is_started = False
    host_id = None
    game_id = None
    
    def __init__(self, game_id, host_id):        
        self.round = 0
        self.game_id = game_id
        self.host = host_id        
                
    def add_player(self, player):
        if self.is_started:
            return False
        self.players[player.get_id()] = player
        return True
    
    def get_users(self):
        res = []
        for player in self.players:
            res.append(self.players.get(player).get_id())
        return res