from player import Bank, Player


class Square:

    name = ""

    def __init__(self, *args, rules=None, **kwargs):
        """Start a Monopoly game."""

    def land(self, board, player, *args, **kwargs):
        """Defines what happens when the player lands on the place."""
        print("Landing", player, "on", self)

    def pass_on(self, board, player, *args, **kwargs):
        """Defines what happens when the player lands on the place."""
        # print("Passing", player, "on", self)

    def can_be_bought(self):
        """Can this property be bought."""
        return False

    def is_owner(self, player):
        """Is the square owned by the player."""
        return False

    def get_owner(self):
        """Return the owner if it exists, None otherwise."""
        return None

    def get_ownership(self):
        return None

    def count_houses(self):
        return None

    def __repr__(self):
        return "|{0}|".format(self.name)


class Start(Square):
    """The start position."""

    name = "Start"
    cash_on_pass = 200

    def pass_on(self, board, player, *args, **kwargs):
        """The player receives an amount."""
        super().pass_on(board, player, *args, **kwargs)
        board.transaction_to_player(Bank(), self.cash_on_pass, player)


class Buyable(Square):
    """A square that can be bought."""

    price = 0
    owner = None

    def land(self, board, player, *args, **kwargs):
        """Land the player on a buyable property."""
        # if the property is owned, then we compute the rent price, and remove it
        # from the player and give it to the owner
        if self.owner is None or self.owner == player:
            return

        rent_price = self.compute_rent(thr=kwargs["thr"])
        board.transaction_to_player(player, rent_price, self.owner)
        print("RENT:", player, "paying rent of", rent_price, "to", self.owner)

    def can_be_bought(self):
        """Can this property be bought."""
        return self.owner is None

    def set_owner(self, player):
        """Set the owner."""
        self.owner = player

    def remove_owner(self):
        """We remove the owner of the property."""
        self.owner = None

    def is_owner(self, player):
        """Is the square owned by the player."""
        return self.owner == player

    def get_owner(self):
        """Return the owner if it exists, None otherwise."""
        return self.owner

    def get_ownership(self):
        """Return an id for the owership."""
        if self.owner is not None:
            return self.owner.uid

    def get_price(self):
        """Return the price of the property."""
        return self.price

    def get_house_price(self):
        """Return the price of the property."""
        return 0

    def buy_house(self):
        """Buy a house in the property."""
        return

    def rent_price(self, *args, **kwargs):
        """Return the rent price."""
        return 0

    def __repr__(self):
        if self.owner:
            return "|{0} of {1}|".format(self.name, self.owner.name)

        return "|{0}|".format(self.name)


class Property(Buyable):
    """A Property."""

    rent = None
    property_group = None
    monopoly_rent = 0
    mortgage = 0
    building_costs = 0

    def __init__(
        self,
        name,
        price,
        group,
        rent=None,
        monopoly_rent=None,
        mortgage=None,
        building_costs=None,
        *args,
        **kwargs
    ):
        """Init a property."""
        super().__init__(
            name,
            price,
            group,
            rent=None,
            monopoly_rent=None,
            mortgage=None,
            building_costs=None,
            *args,
            **kwargs
        )
        self.name = name
        self.price = price
        self.property_group = group
        self.house_count = 0
        self.hotel_count = 0
        group.add_property(self)

        # rent for: none, 1 house, 2 houses, 3 houses, 4 houses, 1 hotel
        self.rent = rent
        self.monopoly_rent = monopoly_rent
        self.mortgage = mortgage
        self.building_costs = building_costs

    def remove_owner(self):
        """We remove the owner of the property."""
        self.owner = None
        self.house_count = 0
        self.hotel_count = 0

    def compute_rent(self, *args, **kwargs):
        """Return the rent price."""
        return self.rent[self.house_count]

    def get_house_price(self):
        """Return the price of the property."""
        if self.house_count < len(self.rent):
            return self.building_costs

    def count_houses(self):
        """Count the number of houses."""
        return self.house_count

    def count_hotels(self):
        """Count the number of hotels."""
        return self.hotel_count

    def buy_house(self):
        """Buy a house in this property."""
        # make sure we can buy more houses
        self.house_count += 1
        if self.house_count >= len(self.rent):
            raise Exception("You can't buy more houses")

    def __repr__(self):
        if self.owner:
            return "|{0} of {1} Houses:{2} Hotels:{3}|".format(
                self.name, self.owner.name, self.count_houses(), self.count_hotels()
            )

        return "|{0}|".format(self.name)


class PropertyGroup:
    """A grouping of properties."""

    name = ""

    def __init__(self, name):
        """Init a property list."""
        self.name = name
        self.property_list = []

    def add_property(self, property):
        """Add a property to the group."""
        self.property_list.append(property)

    def __repr__(self):
        """Print the group."""
        return "PropetyGroup ('{0}'): {1}".format(
            self.name, "|".join(map(lambda x: "{0}".format(x), self.property_list))
        )


class Utility(Buyable):
    """A Utility square."""

    price = 150
    multiplier = [4.0, 10.0]
    mortgage = 75

    def count_houses(self):
        """Count the number of houses."""
        return 0

    def count_hotels(self):
        """Count the number of hotels."""
        return 0

    def compute_rent(self, *args, **kwargs):
        """Return the rent price."""
        # check how many utilities does the owner has
        utility_count = 0
        for square in self.owner.property_list:
            if issubclass(square.__class__, Utility):
                utility_count += 1

        print(kwargs["thr"], self.multiplier, utility_count)

        # TODO: Utilities are group... right? So it is needed to code each  group in a differnt way
        # for now we just max at index 1 and it shoud work
        utility_count = min([1, utility_count])

        return kwargs["thr"].get_amount() * self.multiplier[utility_count]


class ElectricCompany(Utility):

    name = "Electric Company"


class WaterWorks(Utility):

    name = "Water Works"


class TrainStation(Buyable):
    """A train station."""

    # rent for: 1 to 4 railroads owned
    price = 200
    rent = [25, 50, 100, 200]
    mortgage = 100

    def __init__(self, name, *args, **kwargs):
        """Start a Monopoly game."""
        super().__init__(name, *args, *kwargs)
        self.name = name

    def count_houses(self):
        """Count the number of houses."""
        return 0

    def count_hotels(self):
        """Count the number of hotels."""
        return 0

    def compute_rent(self, *args, **kwargs):
        """Return the rent price."""
        return self.rent[0]


class CommunityChest(Square):

    name = "Community Chest"

    def land(self, board, player, *args, **kwargs):
        """Take a new card, perform the action and return the card if it is not owned."""
        super().land(board, player, *args, **kwargs)
        card = board.get_next_community_card()
        card.action(board, player, *args, **kwargs)

        if not card.has_owner():
            board.receive_community_card(card)


class Chance(Square):

    name = "Chance"

    def land(self, board, player, *args, **kwargs):
        """Take a new card, perform the action and return the card if it is not owned."""
        super().land(board, player, *args, **kwargs)
        card = board.get_next_chance_card()
        card.action(board, player, *args, square=self, **kwargs)

        if not card.has_owner():
            board.receive_chance_card(card)


class IncomeTax(Square):

    name = "Income Tax"
    cash_on_land = -200

    def land(self, board, player, *args, **kwargs):
        """The player loses amount."""
        super().land(board, player, *args, **kwargs)
        board.transaction_to_player(Bank(), self.cash_on_land, player)


class LuxuryTax(Square):

    name = "Luxury Tax"
    cash_on_land = -100

    def land(self, board, player, *args, **kwargs):
        """The player loses amount."""
        super().land(board, player, *args, **kwargs)
        board.transaction_to_player(Bank(), self.cash_on_land, player)


class Jail(Square):
    """A train station."""

    name = "Jail"


class GoToJail(Square):
    """A train station."""

    name = "Go to Jail"


class FreeParking(Square):
    """A train station."""

    name = "Free Parking"
