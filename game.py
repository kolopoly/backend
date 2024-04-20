class Game:
    players = {}
    is_started = False
    host_id = None
    game_id = None
    
    def __init__(self, game_id, host_id):
        self.players = []
        self.round = 0
        self.game_id = game_id
        self.host = host_id        
                
    def add_player(self, player):
        if self.is_started:
            return False
        self.players.append({player.get_id(): player})
        return True