#!/usr/bin/env python3

import os
import dotenv
import click
import stripe
import logging
import sys
from datetime import datetime
from pprint import pformat

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

    for sub in stripe.Subscription.list(api_key=STRIPE_SOURCE_KEY):
        #coupon = stripe.Coupon.retrieve(
        logger.info("Sub = [%s]" % pformat(sub))

        # Get the product id from the target
        # which we expect to be the same as the source. 
        # lookup the new price id on the target
        prod_id = sub['items']['data'][0]['price']['product']
        prod = stripe.Product.retrieve(prod_id, api_key=STRIPE_TARGET_KEY)
        price_id_t = prod['default_price']

        # Creating a subscription:
        # customer - customer identifier
        # items = [ { 'price' : price_id } ]
        # currency =  
        # discount = hash of the discount object
        # collection_method: charge_automatically
        # billing_cycle_anchor = current_period_end
        # set id of sub to the same
        # 
        sub_n = {
            'customer'  : 'cus_MbnaT0uLjlzm3Z',
            #'customer'  : sub['customer']
            'items'     : [ { 'price' : price_id_t } ],
            'discount'  : sub['discount'],
            'collection_method' : 'charge_automatically',
            'billing_cycle_anchor' : sub['current_period_end'],
            'trial_end' : sub['current_period_end']
        }
        logger.info("new sub = [%s]", pformat(sub_n))
        stripe.Subscription.create(**sub_n, api_key=STRIPE_TARGET_KEY)
        sys.exit(1)


if __name__ == '__main__':
    main()
