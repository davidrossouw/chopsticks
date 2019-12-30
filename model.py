class Hand():
    def __init__(self, side='l'):
        self.count = 1
        self.side = {'l': 'left', 'r': 'right'}.get(side)


class Player():
    def __init__(self, name):
        self.name = name
        self.left = Hand('l')
        self.right = Hand('r')
        self.winner = False

    def get_state(self):
        return (self.left.count, self.right.count)


class Game():
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.turns = 0
        self.state = "in progress"
        self.active = player1
        self.inactive = player2

    def attack(self, attack):

        if attack == 'll':
            self.inactive.left.count += self.active.left.count
        elif attack == 'lr':
            self.inactive.right.count += self.active.left.count
        elif attack == 'rr':
            self.inactive.right.count += self.active.right.count
        elif attack == 'rl':
            self.inactive.left.count += self.active.right.count
        else:
            # input not recognized
            return

        # Go to zero if exceeds 4:
        if self.inactive.left.count > 4:
            self.inactive.left.count = 0
        if self.inactive.right.count > 4:
            self.inactive.right.count = 0

        return

    def is_won(self):
        if self.player1.left.count == 0 and self.player1.right.count == 0:
            self.player2.winner == True
            self.state = f"{self.player2.name} won!"
            return self.player2
        elif self.player2.left.count == 0 and self.player2.right.count == 0:
            self.player1.winner == True
            self.state = f"{self.player1.name} won!"
            return self.player1
        else:
            return None
