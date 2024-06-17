from enum import Enum

class TransactionType(Enum):
    """Enum for transaction types"""
    PAYMENT = 1
    REFUND = 2