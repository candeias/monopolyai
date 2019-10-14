from random import random


class Strategy:
    def should_buy_property(self, board, player, property):
        """Determines if the property should be bought."""
        return False

    def auction_property(self, board, player, property):
        """Determines max price the player is willing to buy the auctioned property."""
        return 0

    def should_buy_house(self, board, player, property):
        """Determines buying a house."""
        return False

    def should_buy_hotel(self, board, player, property):
        """Determines buying a hotel."""
        return False

    def get_out_of_jail_with_card(self, board, player):
        """Should the user get out of jail with a card, if it has one."""
        from cards import GetOutJailFree

        if player.has_card(GetOutJailFree):
            return True
        return False

    def get_out_of_jail_with_cash(self, board, player):
        return True


class HumanRandom(Strategy):

    buy_property = 0.3
    buy_house = 0.1

    def should_buy_property(self, board, player, square):
        """Determines if the property should be bought."""
        return player.get_cash() >= square.get_price() and random() < self.buy_property

    def should_buy_house(self, board, player, square):
        """Determines if the property should be bought."""
        return (
            player.get_cash() >= square.get_house_price() and random() < self.buy_house
        )
