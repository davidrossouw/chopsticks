import random
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout


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
        
        
class RandomPlayer():
    def __init__(self, name):
        self.name = name
        self.left = Hand('l')
        self.right = Hand('r')

    def get_state(self):
        return (self.left.count, self.right.count)
    
    def reset(self):
        self.left = Hand('l')
        self.right = Hand('r')
    
    @staticmethod
    def move(game) -> str:
        possible_moves = game.get_possible_moves()
        move = random.choice(possible_moves)        
        return move
        

class MinMaxPlayer():
    def __init__(self, name, max_depth=5):
        self.name = name
        self.left = Hand('l')
        self.right = Hand('r')
        self.max_depth = max_depth

    def get_state(self):
        return (self.left.count, self.right.count)
    
    def reset(self):
        self.left = Hand('l')
        self.right = Hand('r')
        
    @staticmethod
    def get_path(G, node_start, node_end, data=None, include_root=False):
        for child in G.predecessors(node_end):
            path = [G.nodes[node_end].get(data)]
            while child != node_start:
                path.insert(0, G.nodes[child].get(data))
                child = next(G.predecessors(child))

            if include_root:
                path.insert(0, G.nodes[node_start].get(data))
            return path
    
    def eval_game_tree(self, game):
        """
        Run game simulations from current game state to a maximum number
        of moves ahead (max_depth)
        Return the graph of possible moves and outcomes, and the current (root) node
        """

        if self.max_depth < 1: return

        G = game.graph.copy()
        all_moves = ['ll','lr', 'rl', 'rr']
        root = game.turn-1
        n = root # node label which also serves as a node counter
        newleavelist=[]
        # First branch in look ahead
        #game.switch_players()
        for attack in all_moves:
            n=n+1
            # Add move node to graph
            G.add_node(n, attack=attack, winner=None, player=None)
            G.add_edge(root, n)
            attack_sequence = self.get_path(G, 0, n, 'attack', include_root=False)
            ## Gun game simulation:
            minigame = Game(Player(game.active.name), Player(game.inactive.name))
            is_legal = minigame.check_moves(attack_sequence)
            if not is_legal:
                G.remove_node(n)
                continue
            G.nodes[n]['player'] = minigame.inactive.name
            if minigame.winner:
                G.nodes[n]['winner'] = minigame.winner
                continue

            newleavelist.append(n)
        depth=1
        # subsequent branches
        while depth < self.max_depth:
            leavelist = newleavelist[:]
            newleavelist = []
            for leave in leavelist:
                for attack in all_moves:
                    n=n+1
                    # Add move node to graph
                    G.add_node(n, attack=attack, winner=None, player=None)
                    G.add_edge(leave, n)
                    attack_sequence = self.get_path(G, 0, n, 'attack', include_root=False)
                    ## Gun game simulation:
                    minigame = Game(Player(game.active.name), Player(game.inactive.name))
                    is_legal = minigame.check_moves(attack_sequence)
                    if not is_legal:
                        G.remove_node(n)
                        continue
                    G.nodes[n]['player'] = minigame.inactive.name
                    if minigame.winner:
                        # print(minigame.winner, attack_sequence)
                        # stop path when result
                        G.nodes[n]['winner'] = minigame.winner
                        G.nodes[n]['attack'] = attack
                        continue
                    newleavelist.append(n)
            depth=depth+1
        return G, root
    
    @staticmethod
    def minimax(G, n):
        """Perform minimax from node n on a NetworkX graph G.
        Assume node n is a maximiser node.
        Return node corresponding to best move
        """

        maxplayer = True
        minplayer = False
        def _minimax(G, n, player):

            # Base case, winning node found
            if G.nodes[n]["winner"]:
                score = {'player1': 1, 'player2': -1}.get(G.nodes[n]['winner'])
                G.nodes[n].update({'score': score})
                return score

            if player == maxplayer:
                bestv = -1
                for child in G.successors(n):
                    v = _minimax(G, child, minplayer)
                    G.nodes[child].update({'score': v})
                    bestv = max(bestv, v)
            else:
                bestv = 1
                for child in G.successors(n):
                    v = _minimax(G, child, maxplayer)
                    G.nodes[child].update({'score': v})
                    bestv = min(bestv, v)
            return bestv

        # Find the best first move from the given node
        # Assume given node n is a maximiser node.
        best_move = None
        bestv = -1

        for child in G.successors(n):
            v = _minimax(G, child, minplayer)
            G.nodes[child].update({'score': v})

            if v > bestv:
                best_move = child
                bestv = v
            
        if best_move:
            return G.nodes[best_move]['attack']
        else:
            return None
    
    def move(self, game) -> str:
        G, root = self.eval_game_tree(game)
        best_move = self.minimax(G, root)
        if best_move is None:
            # make random move
            return random.choice(game.get_possible_moves())
        else:
            return best_move




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

    def select_move(self):
        possible_moves = self.get_possible_moves()
        # random move
        move = random.choice(possible_moves)        
        return move
        
        
    def do_move(self, move):
        if move == 'll':
            self.inactive.left.count += self.active.left.count
        elif move == 'lr':
            self.inactive.right.count += self.active.left.count
        elif move == 'rr':
            self.inactive.right.count += self.active.right.count
        elif move == 'rl':
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
        self.graph.add_node(self.turn, attack=move, winner=self.winner, player=self.active.name)
        self.graph.add_edge(self.turn-1,self.turn)
        # switch players
        self.switch_players()
        self.turn+=1
        
        return
    
    def check_moves(self, moves):
        '''attacks: a list of attacks eg: ['ll', 'lr', ...]
        returns True if moves are legal, false if not
        '''
        for move in moves:
            if move not in self.get_possible_moves():
                return False       
            
            self.do_move(move)
        return True
    
    def draw(self, fig_size = (5,5), labels=None):
        f, ax = plt.subplots(figsize=fig_size)
        self.graph.graph.setdefault('graph', {})['rankdir'] = 'LR'
        # color nodes based on winner
        node_color = []
        for node in self.graph.nodes(data=True):
            if node[1]['winner'] == 'player1':
                node_color.append('green')
            elif node[1]['winner'] == 'player2':
                node_color.append('red')
            else:
                node_color.append('lightgray')
        pos = graphviz_layout(self.graph, prog='dot')
        if labels:
            ax = nx.draw_networkx(self.graph, pos=pos, labels=nx.get_node_attributes(G, labels), node_color=node_color)
        else:
            ax = nx.draw_networkx(self.graph, pos=pos, node_color=node_color)
        return ax
