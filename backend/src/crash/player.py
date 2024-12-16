from crash.records import Cashout
from typing import Optional


class PlayingPlayer:
    def __init__(self, name: str):
        self.name = name
        self.bid_value: int = -1
        self.has_bid: bool = False
        self.cashout_record: Optional[Cashout] = None

    def cashout(self, mult: float) -> Cashout:
        assert (
            self.bid_value > 0
        ), f"Player is cashing out when they haven't bid (bid = {self.bid})"
        self.cashout_record = Cashout(mult, self.bid_value * mult)
        return self.cashout_record

    def bid(self, amount: int) -> bool:
        if amount > 0 and not self.has_bid:
            self.bid_value = amount
            self.has_bid = True
            return True
        return False


class Player:
    def __init__(self, name: str, cash: int):
        self.name = name
        self.cash = cash
        self.bid_history = []
        self.gain_history = []
