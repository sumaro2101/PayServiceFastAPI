from typing import Optional, TypeVar, Union, TypeAlias

import stripe


TargerItem = TypeVar('TargerItem', bound=dict[str, Optional[Union[str, int, bool]]])
StripeType = TypeVar('StripeType', bound=stripe.Product)
StipeResult: TypeAlias = stripe.SearchResultObject
SessionParams: TypeAlias = list[stripe.checkout.Session.CreateParamsLineItem]
Session: TypeAlias = stripe.checkout.Session
