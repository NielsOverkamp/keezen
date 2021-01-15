import json;
import random;
from player import Player, Color;
from command import Command, Option

suits = ["Harten", "Schoppen", "Klaver", "Ruiten"]
denoms = ["Aas", "Heer", "Vrouw", "Boer", "10", "9", "8", "7", "6", "5", "4", "3", "2"]


class Game(object):
    """description of class"""

    def __init__(self):
        self.__init([ 
            Player(Color.RED, "Rood"), 
            Player(Color.BLUE, "Blauw"), 
            Player(Color.YELLOW, "Geel"), 
            Player(Color.GREEN, "Groen")])

    def __init__(self, players):
        self.stock = []
        random.seed()
        self.numberOfCards = 0

        self.players = dict((player.color, player) for player in players)

        for player in self.players.values():
            player.options = [Option(Command.DEAL, None, "Delen")]
            player.message = "Wie begint er met delen?"


    def shuffle(self):
        deck = [x + " " + y for x in suits for y in denoms] + ["Joker" for i in range(3)]
        self.stock = deck * 2

        for n in range(len(self.stock)):
            x = random.randint(0, len(self.stock) - n);
            value = self.stock[x]
            self.stock[x] = self.stock[n]
            self.stock[n] = value


    def deal(self, playerColor):
        player = self.players[playerColor]

        self.currentPlayer = player

        if self.numberOfCards <= 2:
            self.shuffle()
            self.numberOfCards = 6
        else:
            self.numberOfCards -= 1

        for player in self.players.values():
            player.hand = self.stock[:self.numberOfCards]
            self.stock = self.stock[self.numberOfCards:]
            player.options = [Option(Command.CHANGECARD, [card], card) for card in player.hand]
            player.message = "Kies een kaart om te wisselen"
            player.selectedCard = None
            player.cardIsChanged = False

        return self.players


    def changeCard(self, playerColor, card):
        player = self.players[playerColor]

        player.hand.remove(card)
        mate = self.mate(player)

        if mate.selectedCard is None:
            player.selectedCard = card
            player.message = "Wacht op je maat"
            player.options = [Option(Command.UNDOCARD, None, "Terug")]
            return self.players

        player.hand.append(mate.selectedCard)
        mate.selectedCard = None
        mate.hand.append(card)
        player.cardIsChanged = True
        mate.cardIsChanged = True
        mate.options.clear()
        player.options.clear()
        player.message = ""

        if all(player.cardIsChanged for player in self.players.values()):
            self.nextTurn()
        else:
            player.message = "Wacht op het andere team"
            mate.message = "wacht op het andere team"

        return self.players


    def playCard(self, playerColor, card):
        player = self.players[playerColor]

        player.hand.remove(card)
        player.selectedCard = card
        player.options = [Option(Command.UNDOCARD, None, "Terug"), Option(Command.READY, None, "Klaar")]
        player.message = f"Je speelt {card}"

        for other in self.players.values():
            if other.color != player.color:
                other.message = f"{player.name} speelt {card}"

        return self.players


    def ready(self, playerColor):
        player = self.players[playerColor]

        player.options.clear()
        player.selectedCard = None
        self.nextTurn()

        return self.players


    def undoCard(self, playerColor):
        player = self.players[playerColor]

        player.hand.append(player.selectedCard)
        player.selectedCard = None

        if player.cardIsChanged:
            self.turn()
        else:
            player.options = [Option(Command.CHANGECARD, [card], card) for card in player.hand]
            player.message = "Kies een kaart om te wisselen"

        return self.players

    def playOption(self, player, option):
        if option.command == Command.DEAL:
            return self.deal(player.color)
        elif option.command == Command.CHANGECARD:
            return self.changeCard(player.color, option.args[0])
        elif option.command == Command.PLAYCARD:
            return self.playCard(player.color, option.args[0])
        elif option.command == Command.READY:
            return self.ready(player.color)
        elif option.command == Command.UNDOCARD:
            return self.undoCard(player.color)
        else:
            raise Exception(f"Unknown command {option.command}")


    def nextPlayer(self, player):
        if player.color == Color.RED:
            return self.players[Color.BLUE]
        elif player.color == Color.BLUE:
            return self.players[Color.YELLOW]
        elif player.color == Color.YELLOW:
            return self.players[Color.GREEN]
        elif player.color == Color.GREEN:
            return self.players[Color.RED]
        else:
            raise Exception(f"Unknown color {player.Color}")


    def nextTurn(self):
        self.currentPlayer = self.nextPlayer(self.currentPlayer)
        self.turn()


    def turn(self):
        if len(self.currentPlayer.hand) > 0:
            self.currentPlayer.options = [Option(Command.PLAYCARD, [card], card) for card in self.currentPlayer.hand]
            self.currentPlayer.message = "Kies een kaart om te spelen"
            otherMessage = ""
        else:
            self.currentPlayer.options = [Option(Command.DEAL, None, "Delen")]
            self.currentPlayer.message = f"Jij bent aan de beurt om te delen."
            otherMessage = " om te delen"

        for player in self.players.values():
            if player.color != self.currentPlayer.color:
                player.message = f"{self.currentPlayer.name} is aan de beurt" + otherMessage


    def mate(self, player):
        if player.color == Color.RED:
            return self.players[Color.YELLOW]
        elif player.color == Color.BLUE:
            return self.players[Color.GREEN]
        elif player.color == Color.YELLOW:
            return self.players[Color.RED]
        elif player.color == Color.GREEN:
            return self.players[Color.BLUE]
        else:
            raise Exception(f"Unknown color {player.Color}")


if __name__ == "__main__":
    game = Game()

    #game.deal(Color.BLUE)
    #game.changeCard(Color.YELLOW, game.players[Color.YELLOW].hand[4])
    #game.changeCard(Color.RED, game.players[Color.RED].hand[2])
    #game.changeCard(Color.GREEN, game.players[Color.GREEN].hand[0])
    #game.changeCard(Color.BLUE, game.players[Color.BLUE].hand[5])
    #game.playCard(Color.YELLOW, game.players[Color.YELLOW].hand[1])
    #game.undoCard(Color.YELLOW)

    colors = [Color.BLUE, Color.YELLOW, Color.GREEN, Color.RED]

    for round in range(2):
        for deal in [6, 5, 4, 3, 2]:
            color = colors[0]
            print(color)
            game.deal(color)
            game.changeCard(Color.YELLOW, game.players[Color.YELLOW].hand[deal - 1])
            game.changeCard(Color.RED, game.players[Color.RED].hand[1])
            game.changeCard(Color.GREEN, game.players[Color.GREEN].hand[0])
            game.changeCard(Color.BLUE, game.players[Color.BLUE].hand[-1])

            colors = colors[1:] + [colors[0]]

            for turn in range(deal):
                for color in colors:
                    game.playCard(color, game.players[color].hand[0])
                    game.ready(color)

    for player in game.players.values():
        print(player.__dict__, end="\n\n")

    print(game.stock, end="\n\n")