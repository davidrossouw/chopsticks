import random
import networkx as nx

class Hand():
    def __init__(self, side='l'):
        self.count = 1
        self.side = {'l': 'left', 'r': 'right'}.get(side)


class Player():
    def __init__(self, name):
        self.name = name
        self.left = Hand('l')
        self.right = Hand('r')

    def get_state(self):
        return (self.left.count, self.right.count)
    
    def reset(self):
        self.left = Hand('l')
        self.right = Hand('r')

class Move():
    def __init__(self, player, attack, turn):
        self.player = player.name
        self.attack = attack
        self.turn = turn
        self.score = None
        assert attack in ['ll', 'lr', 'rl', 'rr']

class Game():
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.turn = 1
        self.state = "in progress"
        self.active = player1
        self.inactive = player2
        self.finished = False
        self.winner = None
        self.moves = []
        self.graph = nx.DiGraph()
        self.graph.add_node(0, attack=None, winner=None, player=None)
        
        
        
    def get_possible_moves(self):
        # 'lr' - use active left hand to attack inactive right hand
        moves = []
        if self.active.left.count != 0:
            if self.inactive.left.count != 0:
                moves.append('ll')
            if self.inactive.right.count != 0:
                moves.append('lr')
        if self.active.right.count != 0:
            if self.inactive.left.count != 0:
                moves.append('rl')
            if self.inactive.right.count != 0:
                moves.append('rr')
        return moves
    
    
    def switch_players(self):
        self.active, self.inactive = self.inactive, self.active
        
    def zero_fingers(self):
        # Go to zero if exceeds 4:
        if self.inactive.left.count > 4:
            self.inactive.left.count = 0
        if self.inactive.right.count > 4:
            self.inactive.right.count = 0
            

    def is_finished(self):
        if self.player2.left.count == 0 and self.player2.right.count == 0:
            self.finished = True
            self.winner = self.player1.name
            
        if self.player1.left.count == 0 and self.player1.right.count == 0:
            self.finished = True
            self.winner = self.player2.name

    def select_move(self) -> Move:
        possible_moves = self.get_possible_moves()
        if self.active.name == 'random_bot':
            move = Move(self.active, random.choice(possible_moves), self.turn)
            
        elif self.active.name == 'human':
            move =  Move(self.active, random.choice(possible_moves), self.turn)
            
        else:
            move = Move(self.active, random.choice(possible_moves), self.turn)
        
        return move
        
        
    def do_move(self, move:Move):
        if move.attack == 'll':
            self.inactive.left.count += self.active.left.count
        elif move.attack == 'lr':
            self.inactive.right.count += self.active.left.count
        elif move.attack == 'rr':
            self.inactive.right.count += self.active.right.count
        elif move.attack == 'rl':
            self.inactive.left.count += self.active.right.count
        else:
            # input not recognized
            return
        
        # Add move to game history
        self.moves.append(move)
        # Zero fingers if move makes finger count > 4
        self.zero_fingers()
        # Check for winner
        self.is_finished()
        # Add node to graph
        self.graph.add_node(self.turn, attack=move.attack, winner=self.winner, player=self.active.name)
        self.graph.add_edge(self.turn-1,self.turn)
        # switch players
        self.switch_players()
        self.turn+=1
        
        return
    
    def check_moves(self, attacks):
        '''attacks: a list of attacks eg: ['ll', 'lr', ...]
        returns True if moves are legal, false if not
        '''
        for attack in attacks:
            move = Move(self.active, attack, self.turn)
            if move.attack not in self.get_possible_moves():
                return False       
            
            self.do_move(move)
        return True
