#!/usr/bin/env python
from board import Board
from strategy import HumanRandom


class Game:
    def __init__(self, rules=None):
        """Start a Monopoly game."""
        self.board = Board()

    def run(self, max_turns=5000):
        """Run a game."""
        while self.board.game_running() and max_turns is not None:
            self.board.turn()
            if max_turns is not None:
                max_turns -= 1
                if max_turns < 0:
                    max_turns = None

    def export_state(self):
        """Export the state of the game."""


if __name__ == "__main__":

    g = Game()
    g.run()
