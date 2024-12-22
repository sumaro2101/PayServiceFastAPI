from sqlalchemy import func, Text
from sqlalchemy.orm import mapped_column

from functools import partial


ADD_NOW_TIME = partial(mapped_column,
                       insert_default=func.now(),
                       server_default=func.now(),
                       )

EMPTY_TEXT_DEFAULT = partial(mapped_column,
                             Text,
                             default='',
                             server_default='',
                             )

NULL_FIELD_INSTANCE = partial(mapped_column,
                              nullable=True,
                              default=None,
                              )
