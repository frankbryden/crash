from crash.records import Cashout
from typing import Optional, List, Any, Dict, Type


class PlayingPlayer:
    def __init__(
        self,
        name: str,
        cash: int = 1000,
        bid_history: List[int] = None,
        gain_history: List[int] = None,
        mult_history: List[float] = None,
    ):
        self.name = name
        self.bid_value: int = -1
        self.has_bid: bool = False
        self.cash = cash
        self.cashout_record: Optional[Cashout] = None
        self.bid_history: List[int] = bid_history or []
        self.gain_history: List[int] = gain_history or []
        self.mult_history: List[float] = mult_history or []

    def cashout(self, mult: float) -> Cashout:
        assert (
            self.bid_value > 0
        ), f"Player is cashing out when they haven't bid (bid = {self.bid})"
        self.cashout_record = Cashout(mult, int(self.bid_value * mult))
        return self.cashout_record

    def bid(self, amount: int) -> bool:
        if amount > 0 and not self.has_bid:
            self.bid_value = amount
            self.has_bid = True
            return True
        return False

    def reset_game(self):
        self.cashout_record = None
        self.has_bid = False
        self.bid_value = -1

    def to_db_entry(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "cash": self.cash,
            "bid_history": self.bid_history,
            "gain_history": self.gain_history,
            "mult_history": self.mult_history,
        }

    @staticmethod
    def from_db_entry(db_entry: Dict[str, Any]) -> Type["PlayingPlayer"]:
        # Delete automatic db id to instantiate PlayingPlayer object
        del db_entry["_id"]
        return PlayingPlayer(**db_entry)
