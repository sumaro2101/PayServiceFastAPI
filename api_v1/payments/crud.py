from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from stripe import _error

from api_stripe.handler import error_stripe_handle
from config.models import User, Basket, Order
from api_stripe.api import ExpireSession
from api_v1.basket.dao import BasketDAO
from api_v1.orders.dao import OrderDAO


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
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=dict(order='Permission Denied'),
                )

    def _check_basket(self,
                      basket: Basket,
                      ) -> None:
        if not basket:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
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
        try:
            await ExpireSession(session_id=session_id).expire_session()
        except _error.InvalidRequestError as ex:
            message = error_stripe_handle(ex)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=dict(payment=message))

    async def _get_basket(self,
                          user_id: int,
                          unique_code: str,
                          session: AsyncSession,
                          ) -> Basket | None:
        basket = await BasketDAO.find_item_by_args(
            session=session,
            user_id=user_id,
            unique_temporary_id=unique_code,
            many_to_many=(Basket.products,),
        )
        self._check_basket(basket=basket)
        return basket

    async def _get_order(self,
                         order_id: int,
                         session: AsyncSession,
                         ) -> Order:
        return await OrderDAO.find_item_by_args(
            session=session,
            id=order_id,
            many_to_many=(Order.products,),
        )

    async def _create_order(self,
                            user_id: int,
                            coupon_id: int,
                            session: AsyncSession,
                            ) -> Order:
        order_values = dict(
            user_id=user_id,
            coupon_id=coupon_id,
            )
        order_instance = await OrderDAO.add(
            session=session,
            **order_values,
        )
        order = await self._get_order(
            order_id=order_instance.id,
            session=session,
        )
        return order

    async def _switch_products_to_order(self,
                                        basket: Basket,
                                        order: Order,
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
