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
    """Simple program that migrates stripe stuff from one account to
    another"""

    # Setup the logger configuration
    #logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO)
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

    # Print out the list of products
    # Print out the list of plans
    # Print out the list of coupons
    # Print out the list of subscriptions
    #   - id 
    #   - customer reference
    #   - currency
    #   - current period end
    #   - status

    # Check the customer list from the source to the destination
    # Throw an error if it doesn't exist
    notfound = False
    for cust in stripe.Customer.list(api_key=STRIPE_SOURCE_KEY):
        logger.info("Cust: %s[%s]" % (cust['email'], cust['id']))
        logger.info("Checking customer exists on destination account")
        try:
            ret = stripe.Customer.retrieve(cust['id'], api_key=STRIPE_TARGET_KEY)
        except stripe.error.InvalidRequestError:
            logger.info("Could not find customer")
            # TODO: turn back on if you want to error.
            #notfound = True

    if notfound == True:
        logger.error("Not all customers exist on the target account. Exiting")
        sys.exit(1)

    # Print out the subscriptions
    for sub in stripe.Subscription.list(api_key=STRIPE_SOURCE_KEY):
        period_start = datetime.fromtimestamp(sub['current_period_start']).strftime('%Y-%m-%d')
        period_end = datetime.fromtimestamp(sub['current_period_end']).strftime('%Y-%m-%d')
        anchor = datetime.fromtimestamp(sub['billing_cycle_anchor']).strftime('%Y-%m-%d')
        logger.info("Sub: %-30s %-18s %s -> %s [%s]" % (sub['id'], sub['status'], period_start, period_end, anchor))
        print(sub)
        #print("%s, %s, %s, %s, %s" % (sub['id'], sub['status']. sub['currency'], sub['current_period_start'], sub['current_period_end']))
        #print(stripe.Product.list(limit=100))

    # Print out the products
    for prod in stripe.Product.list(api_key=STRIPE_SOURCE_KEY):
        price = stripe.Price.retrieve(prod['default_price'], api_key=STRIPE_SOURCE_KEY)
        price_s = "%s %s [%s]" % (int(price['unit_amount'])/100, price['currency'], price['id'])
        logger.info("Prod: %s[%s] %s %s " % (prod['name'], prod['id'], prod['active'], price_s))

    # Print out the coupons
    for cpn in stripe.Coupon.list(api_key=STRIPE_SOURCE_KEY):
        if cpn['percent_off']:
            off_s = "%s%%" % cpn['percent_off']
        else:
            off_s = "%s %s" % (int(cpn['amount_off'])/100, cpn['currency'])
        logger.info("Coupon: %s[%s] %s " % (cpn['name'], cpn['id'], off_s))

    # Print out all the prices
    for price in stripe.Price.list(api_key=STRIPE_SOURCE_KEY):
        logger.info("Price: %s", price["id"])


if __name__ == '__main__':
    main()
