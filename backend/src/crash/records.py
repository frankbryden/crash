from dataclasses import dataclass


@dataclass
class Cashout:
    mult: float
    gain: float


@dataclass
class CashoutMessage:
    cashout: Cashout
    bid: int
