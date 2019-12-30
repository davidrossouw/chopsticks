from flask import Flask, request, render_template
from model import Hand, Player, Game

app = Flask(__name__)
MAX_TURNS = 50

player1 = Player('David')
player2 = Player('Jill')
game = Game(player1, player2)


def reset_game():
    player1 = Player('David')
    player2 = Player('Jill')
    return Game(player1, player2)


@app.route("/", methods=['GET', 'POST'])
def play_game():
    global game

    if "attack" in request.form:
        game.turns += 1

        print('Move:', request.form["attack"])
        game.attack(request.form["attack"])

        # switch players
        game.active, game.inactive = game.inactive, game.active

    if "reset" in request.form:
        game = reset_game()

    if game.is_won():
        print("Game won!!!")

    if game.turns >= MAX_TURNS:
        print("Max turns exceeded!!!")

    return render_template("index.html", game=game)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
