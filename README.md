# Title
Данный проект является большим онлайн магазином. (Стадия разработки)

# TO DO
## Stripe
Проект реализует интеграцию с внешним API платежной системы Stripe.
Реализованны Классы для интеграции:
- Stripe # Абстрактный класс определяющий каркасс
- CreateStripeItem # Создание Stripe объекта
- UpdateStripeItem # Обновление Stripe объекта
- ActivateStipeItem # Активация Stripe объекта
- DeactivateStripeItem # Деактивация Stripe объекта
- StripeItems # Список Stripe объектов
- CreateDiscountCoupon # Создание скидочного купона
- UpdateDiscountCoupon # Обновление скидочного купона
- DeleteDiscountCoupon # Удаление скидочного купона
- StripeSession # Создание Stripe Сессии для оплаты
- ExpireSession # Отмена Stripe Cессии

Создание Stripe объекта
```python
values = dict(
    id=1,
    name='Stripe',
    price=50000,
)
stripe = CreateStripeItem(values)
await stripe.action()
```

Обновление Stripe объекта
```python
values = dict(
    id=1,
    name='Updated_Stripe',
)
stripe = UpdateStripeItem(values)
await stripe.action()
```

Деактивация Stripe объекта
```python
values = dict(
    id=1,
)
stripe = DeactivateStripeItem(values)
await stripe.action()
```

Активация Stripe объекта
```python
values = dict(
    id=1,
)
stripe = ActivateStipeItem(values)
await stripe.action()
```

Список Stripe объектов
```python
list_items = [
    <Product1>,
    <Product2>,
    <Product3>,
    ]
stripe = StripeItems(
    products=list_items,
    add_key=True,
)
# add_key необходим в случае ручного использования,
# для того что бы система автоматически добавила API_KEY
# к запросу Stripe
```

Создание скидочного купона
```python
values = dict(
    id=1,
    number='COUPON',
    discount=22.0,
    end_at=8043214523, # UNIX-time required
)
stripe = CreateDiscountCoupon(values)
await stripe.action()
```

Обновление скидочного купона
```python
values = dict(
    id=1,
    number='NEWCOUPON',
)
stripe = UpdateDiscountCoupon(values)
await stripe.action()
```

Удаление скидочного купона
```python
values = dict(
    id=1,
)
stripe = DeleteDiscountCoupon(values)
await stripe.action()
```

Создание Сессии для платежа
```python
user = <User1>
list_items = [
    <Product1>,
    <Product2>,
    <Product3>,
    ]
unique_code = int_to_base36(getrandbits(41))
promo = 1
session = StripeSession(
    user=user,
    products=list_items,
    unique_code=unique_code,
    promo=promo,
)
session.get_session_payments()
# unique_code неоходим для защиты сессии от злоумышленного
# использования. Этот код идентифицирует текущую корзину.
# При совершении покупки и создании заказа этот код удаляется из текущей корзины,
# по этому создать дополнительные заказы просто посредством перехода на ту же ссылку
# не возможно.
```

Отмена Stripe Сессии
```python
basket = <Basket1>
ExpireSession(
    session_id=basket.session_id,
).expire_session()
```

# Dependencies
В проекте используются зависимости:
- fastapi
- pydantic
- pydantic-settings
- sqlalchemy
- asyncpg
- psycopg2-binary
- alembic
- pyjwt
- bcrypt
- python-multipart
- stripe
- pytz
- uvicorn
- python-dotenv

## SQLAlchemy
SQLAlchemy используется асинхронный.
Реализованн специальный класс для поддежки подключения и 
делегированнием сессий.
- DataBaseHelper

```python
# Инициализация соединения с Базой Данных на текущий HTTP запрос
async with db_helper.engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
    yield # Событие HTTP запроса
await db_helper.dispose()

# "Протаскивание" текущей сессии для запросов к Базе данных на этот HTTP запрос
async def get_session(session: AsyncSession = Depends(db_helper.session_geter)):
    current_session = session
    return session
```
