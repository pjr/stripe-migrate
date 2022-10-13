#!/usr/bin/env python3

import os
import dotenv
import click
import stripe
import logging
import sys
from datetime import datetime

dotenv.load_dotenv()

### Things to migrate:
### * Subscriptions
### * 

#def logsetup():
    #logging.basicConfig(filename='stripe-migratee.log', encoding='utf-8', level=logging.DEBUG)
#    pass

def main():
    """Simple program that migrates coupons from one account to
    another"""

    # Setup the logger configuration
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.DEBUG)
    logger = logging.getLogger('ch.stripe.migrate')
    logger.setLevel(logging.DEBUG)
    fhnd = logging.StreamHandler()
    fhnd.setFormatter(logging.Formatter("format='%(asctime)s %(levelname)-8s %(message)s"))
    logger.addHandler(fhnd)


    # Load stripe keys 
    STRIPE_SOURCE_KEY = os.environ['STRIPE_SOURCE_KEY']
    STRIPE_TARGET_KEY = os.environ['STRIPE_TARGET_KEY']
    logger.info("Loaded source key[%s..%s] and target key [%s..%s]" % (
        STRIPE_SOURCE_KEY[:12],
        STRIPE_SOURCE_KEY[-6:],
        STRIPE_TARGET_KEY[:12],
        STRIPE_TARGET_KEY[-6:]
    ))

    # Not applicable: livemode, object, valid, created, times_redeemed
    COUPON_KEYS_CP = [
        'id', 'amount_off', 'currency', 'duration', 'duration_in_months', 
        'max_redemptions', 'name', 'percent_off', 'redeem_by' 
    ]

    # Retrieve the coupons from the source & recreate in the target.
    for cpn in stripe.Coupon.list(api_key=STRIPE_SOURCE_KEY):
        cpn_t = { key: cpn[key] for key in cpn.keys() if key in COUPON_KEYS_CP }

        logger.info("Coupon: New object = %s" % cpn_t)
        stripe.Coupon.create(**cpn_t, api_key=STRIPE_TARGET_KEY)
        logger.info("Coupon: Created in target: %s[%s]" % (cpn_t['name'], cpn_t['id']))

if __name__ == '__main__':
    main()
