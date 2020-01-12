import random
import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout

ALL_MOVES = [[0,0],[0,1],[1,0],[1,1]]

class Move():
    def __init__(self, player:int, move):
        self.move = move
        self.player = player # 0 or 1
        self.non_player = 1 - player # 0 or 1
        assert move in ALL_MOVES       

class Board():
    def __init__(self, player1:tuple, player2:tuple):
        self.state = [player1, player2]
        
        
    def moves_available(self, player:int=0) -> list: # make this have a Board as input
        # [[0,0],[0,1],[1,0],[1,1]] # 'll', 'lr', 'rl', 'rr'
        moves = []
        active = player
        inactive = 1-player
        
        # player1 left hand not 0 and player2 left hand not 0
        if self.state[active][0] != 0 and self.state[inactive][0] != 0:
            moves.append([0,0])
            
        # player1 left hand not 0 and player2 left hand not 0
        if self.state[active][0] != 0 and self.state[inactive][1] != 0:
            moves.append([0,1])
            
        # player1 right hand not 0 and player2 left hand not 0
        if self.state[active][1] != 0 and self.state[inactive][0] != 0:
            moves.append([1,0])
            
        # player1 right hand not 0 and player2 left hand not 0
        if self.state[active][1] != 0 and self.state[inactive][1] != 0:
            moves.append([1,1])

        return moves
        
    def display(self):
        return str(self.state[0][0])+str(self.state[0][1])+ \
               str(self.state[1][0])+str(self.state[1][1])
    
    
    def is_winner(self):
        # player1 left hand == 0 and player1 right hand == 0
        if self.state[0][0] == 0 and self.state[0][1] == 0:
            return True
            
        # player2 left hand == 0 and player2 right hand == 0
        if self.state[1][0] == 0 and self.state[1][1] == 0:
            return True      
        
        return False


        
class RandomPlayer():
    def __init__(self, name, idx):
        self.name = name
        self.idx = idx
    
    def select_move(self, board) -> Move:
        moves_available = board.moves_available(self.idx)
        move = random.choice(moves_available)
        return Move(self.idx, move)
    
    
def search(board:Board, max_depth=3):
    """
    Run game simulations from current game state to a maximum number
    of moves ahead (max_depth)
    Return the graph of possible moves and outcomes
    state = [(1,1), (1,1)]
    """

    n = 0 # node label which also serves as a node counter
    depth = 0
    
    G = nx.DiGraph()
    G.add_node(0, move=None, winner=None, player=depth%2, board=board.state, board_p = board.display())
    
    # First branch in look ahead
    newleavelist=[]
    parent_node = n
    parent_board = Board(G.nodes[n]['board'][0], G.nodes[n]['board'][1])
    
    for move in ALL_MOVES:
        moves_available = parent_board.moves_available(player=depth)
        if move not in moves_available:
            continue
        
        # Do move
        new_board = update_board(Move(player=depth%2, move=move), parent_board)
        
        # Add move node to graph
        n=n+1
        G.add_node(n, move=move, winner=new_board.is_winner(), player=depth%2, board=new_board.state, board_p = new_board.display())
        G.add_edge(parent_node, n)
        if new_board.is_winner():
            continue
        newleavelist.append(n)
    
    depth=1
    # subsequent branches
    while depth < max_depth:
        leavelist = newleavelist[:]
        newleavelist = []
        for leave in leavelist:
            
            # Get parent board
            parent_board = Board(G.nodes[leave]['board'][0], G.nodes[leave]['board'][1])
            for move in ALL_MOVES:
                moves_available = parent_board.moves_available(player=depth%2)
                if move not in moves_available:
                    continue
                
                # Do move
                new_board = update_board(Move(player=depth%2, move=move), parent_board)
                
                # Add move node to graph
                n=n+1
                G.add_node(n, move=move, 
                           winner=new_board.is_winner(), 
                           player=depth%2, board=new_board.state, 
                           board_p=new_board.display())
                G.add_edge(leave, n)
                if new_board.is_winner():
                    continue
                    
                newleavelist.append(n)
        depth=depth+1
    return G    
    


def update_board(move:Move, board):
    new_state = list(map(list, board.state))
    # Apply move
    new_state[move.non_player][move.move[1]] += board.state[move.player][move.move[0]]
    # If any hand > 4, set to zero (out of the game)
    if new_state[move.non_player][move.move[1]] > 4:
        new_state[move.non_player][move.move[1]] = 0

    new_board = Board(new_state[0], new_state[1])
    return new_board

def draw_graph(G, fig_size = (5,5), labels=None):
    f, ax = plt.subplots(figsize=fig_size)
    G.graph.setdefault('graph', {})['rankdir'] = 'LR'
    # color nodes based on winner
    node_color = []
    for node in G.nodes(data=True):
        if node[1]['winner']:
            if node[1]['player'] == 0:
                node_color.append('green')
            if node[1]['player'] == 1:
                node_color.append('red')
        else:
            node_color.append('lightgray')
    pos = graphviz_layout(G, prog='dot')
    if labels:
        ax = nx.draw_networkx(G, pos=pos, labels=nx.get_node_attributes(G, labels), node_color=node_color, node_size=20)
    else:
        ax = nx.draw_networkx(G, pos=pos, with_labels=False, node_color=node_color, node_size=20)
    return ax

