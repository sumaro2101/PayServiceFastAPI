from enum import Enum


class ErrorCode(str, Enum):
    PRODUCT_NOT_FOUND = 'PRODUCT_NOT_FOUND'
    PRODUCT_ALREADY_ACTIVE = 'PRODUCT_ALREADY_ACTIVE'
