from config.rabbitmq.connection import app
from api_stripe.abs import Stripe


@app.task()
async def crud_stripe_item_task(stripe_cls: Stripe,
                                args: dict,
                                ):
    stripe = stripe_cls(args)
    await stripe.action()
