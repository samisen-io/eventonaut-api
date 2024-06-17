from enum import Enum

class PaymentStatus(Enum):
    UNPAID = 'unpaid'
    PAID = 'paid'
    CANCELLED = 'cancelled'