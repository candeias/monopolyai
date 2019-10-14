from random import randint


class Throw:
    @classmethod
    def simple_amount(cls, n=2):
        """Return a random ammount."""
        return randint(n, 6 * n)

    def __init__(self, n=2):
        """Create a new throw."""
        self.amount = 0
        self.double = True
        last_amount = None

        for i in range(n):
            new_amount = randint(1, 6)
            if last_amount is not None and last_amount != new_amount:
                self.double = False

            last_amount = new_amount
            self.amount += last_amount

    def get_amount(self):
        """Return the amount."""
        return self.amount

    def is_double(self):
        """Return if this is a double."""
        return self.double
