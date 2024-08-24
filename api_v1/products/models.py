from sqlalchemy.orm import Mapped

from config.models.base import Base


class Product(Base):
    """Модель товара
    """
    name: Mapped[str]
    description: Mapped[str]
    price: Mapped[int]
