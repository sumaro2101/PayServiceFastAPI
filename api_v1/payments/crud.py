from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select, and_
from sqlalchemy.orm import joinedload

from fastapi import HTTPException, status

from loguru import logger
from config.models import User, Basket, Order
from api_stripe.api import ExpireSession


class PaymentManager:
    """
    Менеджер для делигирования поступающих
    сведений о платежах
    """

    def __init__(self,
                 user: User,
                 unique_code: str,
                 session: AsyncSession,
                 ) -> None:
        self.user = user
        self.unique_code = unique_code
        self._session = session

    @classmethod
    def check_unique_code(cls,
                          unique_code: str,
                          ) -> None:
        if not unique_code:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                        detail=dict(order='Permission Denied'),
                        )

    def _check_basket(self,
                      basket: Basket,
                      ) -> None:
        if not basket:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=dict(order='Permission Denied'),
                                )

    async def _reset_basket_state(self,
                                  basket: Basket,
                                  session: AsyncSession,
                                  with_cancel: bool = False,
                                  ) -> Basket:
        if not with_cancel:
            basket.products.clear()
            basket.coupon_id = None
        basket.unique_temporary_id = None
        basket.session_id = None
        await session.commit()
        return basket

    async def _expire_session(self,
                              session_id: str,
                              ) -> None:
        await ExpireSession(session_id=session_id).expire_session()

    async def _get_basket(self,
                          user_id: int,
                          unique_code: str,
                          session: AsyncSession,
                          ) -> Basket | None:
        stmt = (Select(Basket)
            .where(and_(Basket.user_id == user_id,
                        Basket.unique_temporary_id == unique_code))
            .options(joinedload(Basket.products)))
        basket: Basket = await session.scalar(statement=stmt)
        self._check_basket(basket=basket)
        return basket

    async def _get_order(self,
                         order_id: int,
                         session: AsyncSession,
                         ) -> Order:
        stmt = (Select(Order)
                .where(Order.id == order_id)
                .options(joinedload(Order.products)))
        order: Order = await session.scalar(statement=stmt)
        return order

    async def _create_order(self,
                            user_id: int,
                            coupon_id: int,
                            session: AsyncSession,
                            ) -> Order:
        order_values = dict(user_id=user_id,
                        coupon_id=coupon_id)
        order_model = Order(**order_values)
        session.add(order_model)
        await session.commit()
        await session.refresh(order_model)
        order = await self._get_order(
            order_id=order_model.id,
            session=session,
        )
        return order

    async def _switch_products_to_order(self,
                                        basket: Basket,
                                        order: Order,
                                        session: AsyncSession,
                                        ) -> Order:
        order.products.extend(basket.products)
        return order

    async def _get_fill_order(self,
                              user: User,
                              unique_code: str,
                              session: AsyncSession,
                              ) -> Order:
        user_id = user.id
        self.check_unique_code(
            unique_code=unique_code,
        )
        basket = await self._get_basket(
            user_id=user_id,
            unique_code=unique_code,
            session=session,
        )
        coupon_id = basket.coupon_id
        order = await self._create_order(
            user_id=user_id,
            coupon_id=coupon_id,
            session=session,
        )
        fill_order = await self._switch_products_to_order(
            basket=basket,
            order=order,
            session=session,
        )
        await self._reset_basket_state(
            basket=basket,
            session=session,
        )
        return fill_order

    async def _cancel_payment(self,
                              user: User,
                              unique_code: str,
                              session: AsyncSession,
                              ) -> None:
        user_id = user.id
        self.check_unique_code(
            unique_code=unique_code,
        )
        basket = await self._get_basket(
            user_id=user_id,
            unique_code=unique_code,
            session=session,
        )
        session_id = basket.session_id
        await self._expire_session(
            session_id=session_id,
        )
        await self._reset_basket_state(
            basket=basket,
            session=session,
            with_cancel=True,
        )
        return

    async def get_order(self):
        """
        Получение созданного заказа
        """
        order = await self._get_fill_order(
            user=self.user,
            unique_code=self.unique_code,
            session=self._session,
        )
        return order

    async def cancel_payment(self):
        """
        Отмена текущего платежа
        """
        await self._cancel_payment(
            user=self.user,
            unique_code=self.unique_code,
            session=self._session,
        )
        return
