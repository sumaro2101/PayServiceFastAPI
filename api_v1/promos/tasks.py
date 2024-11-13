from config.rabbitmq.connection import app
from api_stripe.api import (
    CreateDiscountCoupon,
    UpdateDiscountCoupon,
    DeleteDiscountCoupon,
    )


@app.task
async def create_coupon_stripe_task(args: dict):
    stripe = CreateDiscountCoupon(args)
    await stripe.action()


@app.task
async def update_coupon_stripe_task(args: dict):
    stripe = UpdateDiscountCoupon(args)
    await stripe.action()


@app.task
async def delete_coupon_stripe_task(args: dict):
    stripe = DeleteDiscountCoupon(args)
    await stripe.action()
