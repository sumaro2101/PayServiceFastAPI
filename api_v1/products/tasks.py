from config import celery_app
from api_stripe.api import (
    CreateStripeItem,
    UpdateStripeItem,
    ActivateStipeItem,
    DeactivateStripeItem,
    )


@celery_app.task
async def create_stripe_item_task(args: dict):
    stripe = CreateStripeItem(args)
    await stripe.action()


@celery_app.task
async def update_stripe_item_task(args: dict):
    stripe = UpdateStripeItem(args)
    await stripe.action()


@celery_app.task
async def activate_stripe_item_task(args: dict):
    stripe = ActivateStipeItem(args)
    await stripe.action()


@celery_app.task
async def deactivate_stripe_item_task(args: dict):
    stripe = DeactivateStripeItem(args)
    await stripe.action()
