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
    #logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.DEBUG)
    logger = logging.getLogger('ch.stripe.migrate')
    logger.setLevel(logging.DEBUG)
    fhnd = logging.StreamHandler()
    fhnd.setFormatter(logging.Formatter("%(asctime)s %(levelname)-8s %(message)s"))
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

    # Pre-flight checks

    logger.info("*** Pre-flight checks ***")
    subs_s = stripe.Subscription.list(api_key=STRIPE_SOURCE_KEY)
    # TODO change
    subs_t = stripe.Subscription.list(api_key=STRIPE_TARGET_KEY)
    cust_t_with_subs = [ sub['customer'] for sub in subs_t ]

    logger.info("Total Subs on source: %d", len(subs_s))
    for sub in subs_s:
        # Retrieve the customer object associated with the sub on the source
        # and confirm there's an email there 
        cust_src = stripe.Customer.retrieve(sub['customer'], api_key=STRIPE_SOURCE_KEY)
        if not 'email' in cust_src or cust_src['email'] is None:
            logger.error("Customer [%s] has no email associated with the account", cust_src['id'])

        logger.info("Sub [%s] - Customer email: [%s]" % (sub['id'], cust_src['email']))
        cust_search_qry = ("email: '%s'" % cust_src['email'])
        logger.info("    -> Search on target: %s" % cust_search_qry)
        cust_search_target = stripe.Customer.search(query=cust_search_qry, api_key=STRIPE_TARGET_KEY)

        # Triple check we only got one customer record back
        if len(cust_search_target) == 0:
            logger.error("Did not find customer '%s' on target stripe account. Exiting" % cust_src['email'])
            sys.exit(1)
        elif len(cust_search_target) > 1:
            logger.error("Multiple records (%d) for '%s' on target stripe. Must be 1 exactly." % (len(cust_search_target), cust_src['email']))
            sys.exit(1)
        else:
            logger.info("    -> 1 exact match found. Cust id[%s]" % cust_search_target['data'][0]['id'])


    logger.info("*** Starting the migration *** ")
    # Now run the migration
    for sub in subs_s:
        logger.info(" *** MIGRATING sub[%s] " % sub['id'])

        # Get the product id from the target
        # which we expect to be the same as the source. 
        # lookup the new price id on the target
        prod_id = sub['items']['data'][0]['price']['product']
        prod = stripe.Product.retrieve(prod_id, api_key=STRIPE_TARGET_KEY)
        price_id_t = prod['default_price']

        # Get the old customer id and confirm new customer id is available on the source.
        cust_s = stripe.Customer.retrieve(sub['customer'], api_key=STRIPE_SOURCE_KEY)
        cust_search_qry = ("email: '%s'" % cust_s['email'])
        cust_t = stripe.Customer.search(query=cust_search_qry, api_key=STRIPE_TARGET_KEY)['data'][0]

        # Double check if this customer has a subscription
        logger.info("Checking if %s:%s is in %s" % (cust_t['email'], cust_t['id'], pformat(cust_t_with_subs)))
        if cust_t['id'] in cust_t_with_subs:
            logger.warning("Customer [%s] already has a subscription. Not adding a second" % cust_t['email'])
            continue


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
            'customer'              : cust_t['id'],
            'items'                 : [ { 'price' : price_id_t } ],
            'coupon'                : sub['discount']['coupon']['id'],
            'collection_method'     : 'charge_automatically',
            'billing_cycle_anchor'  : sub['current_period_end'],
            'trial_end'             : sub['current_period_end']
        }
        logger.info("new sub = [%s]", pformat(sub_n))
        stripe.Subscription.create(**sub_n, api_key=STRIPE_TARGET_KEY)

if __name__ == '__main__':
    main()
