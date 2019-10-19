from strategy import HumanRandom


class PlayerException(Exception):
    pass


class PlayerNoFunds(Exception):
    pass


class GeneralPlayer:

    pass


class Bank(GeneralPlayer):

    name = "Bank"

    def transfer(self, amount):
        """Accept all amounts."""

    def __repr__(self):
        """Return the name."""
        return "BANK"


class Player(GeneralPlayer):

    name = "Player"

    def __init__(self, uid=0, token=None, strategy=HumanRandom()):
        """Set the name of the player."""
        if token is not None:
            self.name = token
        self.strategy = strategy
        self.uid = uid

        self.cards = []
        self.community_cards = []
        self.cash = 1500
        self.property_list = []
        self.in_jail_count = None

    def transfer(self, amount):
        """Transfer money from the player account."""
        # check bankrupt
        if self.will_bankrupt(amount):
            raise PlayerNoFunds

        # perform the transaction
        self.cash += amount

    def will_bankrupt(self, amount):
        """Check if a user is bankrupt."""
        if self.cash + amount >= 0:
            return False

        # TODO: try to solve bankruptcy using a mortgage or selling items

        return True

    def set_bankrupt(self, board, player):
        """The player will become bankrupt."""
        # move all remaining value to the player
        board.transaction_to_player(self, self.cash, player)
        self.property_list = []

    def get_cash(self):
        """Return the amount of cash the user has."""
        return self.cash

    def go_to_jail(self):
        """Player will go to jail."""
        self.in_jail_count = 0

    def is_in_jail(self):
        """Is the player in jail?"""
        return self.in_jail_count is not None

    def count_failed_leave_fail(self):
        """Count the user to leave jail."""
        self.in_jail_count += 1

    def count_failed_attempts_fail(self):
        """Return the number of failed attempts at leaving jail."""
        return self.in_jail

    def leave_jail(self):
        """The user leaves jail."""
        self.in_jail_count = None

    def add_card(self, card):
        """Add a card."""
        self.cards.append(card)

    def has_card(self, card_class):
        """Determine if the user has a card."""
        for i in range(len(self.cards)):
            if self.cards[i].__class__ == card_class:
                return True
        return False

    def get_card(self, card_class):
        """Return a user's card."""
        for i in range(len(self.cards)):
            if self.cards[i].__class__ == card_class:
                card = self.cards.pop(i)
                return card

        raise Exception

    def add_property(self, square):
        """Add a property to the user."""
        self.property_list.append(square)

    def count_houses(self):
        """Count the houses of a player."""
        result = 0
        for p in self.property_list:
            result += p.count_houses()
        return result

    def count_hotels(self):
        """Count the hotels of a player."""
        result = 0
        for p in self.property_list:
            result += p.count_hotels()
        return result

    def __str__(self):
        return "{0} (${1})".format(self.name, self.cash)

    def full(self):
        """Return the name."""
        return "{0} (${1}, P:{2})\n\t{3}\n".format(
            self.name,
            self.cash,
            len(self.property_list),
            "\n\t".join(map(str, self.property_list)),
        )
