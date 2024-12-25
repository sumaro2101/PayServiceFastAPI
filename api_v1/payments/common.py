from enum import Enum


class ErrorCode(str, Enum):
    FORBIDDEN = 'FORBIDDEN'
    STRIPE_EXPIRE_ERROR = 'STRIPE_EXPIRE_ERROR'
