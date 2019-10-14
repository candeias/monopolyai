from random import randint, shuffle

from cards import GetOutJailFree

from dice import Throw
from player import Bank, Player

from strategy import HumanRandom
from board_config import BoardConfig


class BoardException(Exception):
    pass


class PlayerNotFound(BoardException):
    pass


class SquareNotFound(BoardException):
    pass


class Board(BoardConfig):
    def __init__(
        self,
        player_count=4,
        strategy=[HumanRandom(), HumanRandom(), HumanRandom(), HumanRandom()],
        rules=None,
    ):
        """Create a board with all of the sqares."""
        # shuffle the cards
        shuffle(self.community_cards)
        shuffle(self.chance_cards)

        self.player_positions = [0] * player_count
        self.current_player = randint(0, player_count - 1)
        self.player_list = []
        for i in range(player_count):
            self.player_list.append(
                Player(uid=i, token=self.token[i], strategy=strategy[i])
            )
        self.full_turn_count = 1

    def compute_new_position_from_dice(self, player_index, thr):
        """Compute the new position on the board."""
        new_position = self.player_positions[player_index] + thr.get_amount()

        if new_position >= len(self.squares):
            new_position -= len(self.squares)

        return new_position

    def player_observable_variables(self):
        """Export the variables that human users would be able to see."""
        # token positions
        token_position = self.player_positions
        square_ownership = []
        square_houses = []

        for i in range(len(self.squares)):
            square_ownership.append(self.squares[i].get_ownership())
            square_houses.append(self.squares[i].count_houses())

        print(token_position)
        print(square_ownership)
        print(square_houses)

    def turn(self):
        """Play a turn until it need human interaction."""
        # 1 throw the dice
        if (
            not self.player_list[self.current_player].is_in_jail()
            or self.try_leave_jail()
        ):
            thr = Throw()
            while thr is not None:
                # check in where the current player will land
                new_position = self.compute_new_position_from_dice(
                    self.current_player, thr
                )
                self.move_player_to(self.current_player, new_position, thr=thr)

                if thr.is_double():
                    thr = Throw()
                else:
                    thr = None
                print("------------------------------")

                self.player_observable_variables()

        # move turn to next player
        self.current_player += 1
        if self.current_player >= len(self.player_list):
            self.current_player = 0
            self.full_turn_count += 1
            print("**********************")
            print(
                "Full turn:",
                self.full_turn_count,
                "\n",
                "\n".join(map(lambda x: x.full(), self.player_list)),
            )
            print("**********************")

    def try_leave_jail(self):
        """Make a player to try to leave jail."""
        player = self.player_list[self.current_player]

        print(player, "trying to leave jail")

        if player.strategy.get_out_of_jail_with_card(self, player=player):
            # we just leave jail using the card.
            card = player.get_card(GetOutJailFree)
            if len(self.chance_cards) > len(self.community_cards):
                self.receive_community_card(card)
            else:
                self.receive_chance_card(card)
            player.leave_jail()
            return True

        if player.strategy.get_out_of_jail_with_cash(self, player):
            self.transaction_to_player(Bank(), -50, player)
            # now roll the dice, an mov
            thr = Throw()
            new_position = self.compute_new_position_from_dice(self.current_player, thr)
            self.move_player_to(self.current_player, new_position, thr=thr)
            player.leave_jail()
            return True

        # just try to roll the dice
        thr = Throw()
        if thr.is_double():
            new_position = self.compute_new_position_from_dice(self.current_player, thr)
            self.move_player_to(self.current_player, new_position, thr=thr)
            player.leave_jail()
            return True
        player.count_failed_leave_fail()

        if player.count_failed_attempts_fail() > 3:
            # just play and leave
            self.transaction_to_player(Bank(), -50, player)
            # now roll the dice, an mov
            thr = Throw()
            new_position = self.compute_new_position_from_dice(self.current_player, thr)
            self.move_player_to(self.current_player, new_position, thr=thr)
            player.leave_jail()
            return True

        return False

    def get_player_index(self, player):
        """Return the index for the player."""
        # find the player by going through the list
        for i in range(len(self.player_list)):
            if player == self.player_list[i]:
                return i
        raise PlayerNotFound

    def get_square_index(self, square):
        """Return the index of the square."""
        # find the player by going through the list
        for i in range(len(self.squares)):
            if square == self.squares[i]:
                return i
        raise SquareNotFound

    def get_square_index_by_name(self, square_name, from_square=None):
        """Return the first square of a given name."""
        if from_square is not None:
            # don't start at the begining
            raise Exception

        for i in range(len(self.squares)):
            print(self.squares[i].name, square_name)
            if self.squares[i].name == square_name:
                return i

        raise SquareNotFound

    def get_square_by_class(self, square_class, from_square=None):
        """Return the first square of a given class."""
        start_index = 0
        if from_square is not None:
            # don't start at the begining
            for i in range(0, len(self.squares)):
                if self.squares[i] == from_square:
                    start_index = i
                    break

        while True:
            if issubclass(self.squares[start_index].__class__, square_class):
                return self.squares[start_index]
            start_index += 1
            if start_index >= len(self.squares):
                start_index = 0

        raise SquareNotFound

    def move_player_n_square(
        self, player_index, n, player=None, pass_on_squares=True, thr=None
    ):
        """Move a player to the n."""
        if player is not None:
            player_index = self.get_player_index(player)

        square_index = self.player_positions[player_index] + n
        if square_index < 0:
            square_index = -square_index
        if square_index >= len(self.squares):
            square_index -= len(self.squares)

        self.move_player_to(
            player_index, square_index, pass_on_squares=pass_on_squares, thr=thr
        )

    def move_player_to(
        self,
        player_index,
        square_index,
        player=None,
        square=None,
        pass_on_squares=True,
        thr=None,
        process_square=True,
    ):
        """Move a player to the index."""
        if player is not None:
            player_index = self.get_player_index(player)

        if square is not None:
            square_index = self.get_square_index(square)

        print(
            self.full_turn_count,
            self.player_list[player_index],
            "moving to",
            self.squares[square_index],
            pass_on_squares,
        )

        if pass_on_squares:
            # we need to send the pass action to each square
            # determine the number of square we need to move
            moves = 0
            if self.player_positions[player_index] < square_index:
                moves = square_index - self.player_positions[player_index] - 1
            else:
                # then the number of moves is just the square_index (minus 1) and the move
                # to get to the Start square_index
                moves = (
                    square_index
                    - 1
                    + (self.player_positions[player_index] - len(self.squares))
                )

            while moves > 0:
                self.player_positions[player_index] += 1
                if self.player_positions[player_index] >= len(self.squares):
                    self.player_positions[player_index] = 0

                self.squares[self.player_positions[player_index]].pass_on(
                    self, self.player_list[player_index]
                )

                moves -= 1

            #  lastly increase the position to peform the land afterwards
            self.player_positions[player_index] += 1
            if self.player_positions[player_index] >= len(self.squares):
                self.player_positions[player_index] = 0

        else:
            # we mode directly to the new square
            self.player_positions[player_index] = square_index

        square = self.squares[square_index]
        player = self.player_list[player_index]

        if not process_square:
            return

        square.land(self, player, thr=thr)

        if square.is_owner(player):
            # check if the player should build a house
            if player.strategy.should_buy_house(self, player, square):
                # buy a house
                self.buy_house(player, square)
            return

        # determine if we should buy the property
        if not square.can_be_bought():
            return

        # check if the player wants to buy the property
        if player.strategy.should_buy_property(self, player, square):
            # buy it
            self.buy_property(player, square)
            return

        # make the auction

    def remove_player(self, player):
        """Remove the player from the board."""
        print("REMOVING", player)
        player_index = self.get_player_index(player)

        # if we are the current player, move back the index once
        if self.current_player == player_index:
            self.current_player -= 1
            if self.current_player < 0:
                self.current_player = len(self.player_list) - 2

        self.player_positions.pop(player_index)
        self.player_list.pop(player_index)

        # TODO: put any cards owned by the player back in to the cards list

    def buy_property(self, player, square):
        """Buy this property for the player."""
        # pay the bank
        print(player, "buying", square)
        self.transaction_to_player(Bank(), -square.get_price(), player)

        # set the owner on the property, and on the player
        square.set_owner(player)
        player.add_property(square)

    def buy_house(self, player, square):
        """Buy this house for the player."""
        # pay the bank
        house_price = square.get_house_price()
        if house_price is None:
            return

        print(player, "buying a house on", square)
        self.transaction_to_player(Bank(), -house_price, player)

        # set the owner on the house, and on the player
        square.buy_house()

    def transaction_to_player(self, origin, amount, receiver):
        """Peform a transaction between 2 players."""
        print("Transfering", amount, origin, "->", receiver)
        try:
            origin.transfer(-amount)
        except:
            # the origin will became bankrupt, so declare it and remove it from the game
            origin.set_bankrupt(self, receiver)
            self.remove_player(origin)
            return

        try:
            receiver.transfer(amount)
        except:
            # the receiver will became bankrupt, so declare it
            receiver.set_bankrupt(self, origin)
            self.remove_player(receiver)

    def transaction_to_player_from_all(self, amount, receiver):
        """Peform a transaction between 2 players."""
        print("Transfering", amount, "From all players ->", receiver)
        i = 0
        while i < len(self.player_list):
            if self.player_list[i] is not receiver:
                self.transaction_to_player(self.player_list[i], amount, receiver)
            i += 1

    def get_next_chance_card(self):
        """Return the next chance card."""
        return self.chance_cards.pop(0)

    def receive_chance_card(self, card):
        """Receive a chance card."""
        self.chance_cards.append(card)

    def get_next_community_card(self):
        """Return the next community card."""
        return self.community_cards.pop(0)

    def receive_community_card(self, card):
        """Receive a chance card."""
        self.community_cards.append(card)

    def game_running(self):
        return len(self.player_list) > 1
