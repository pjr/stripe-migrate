import os
import dotenv
import click
import stripe
import logging
import sys
from pprint import pformat
from datetime import datetime

dotenv.load_dotenv()

### Things to migrate:
### * Subscriptions
### * 

#def logsetup():
    #logging.basicConfig(filename='stripe-migratee.log', encoding='utf-8', level=logging.DEBUG)
#    pass

def main():
    """Simple program that migrates productsfrom one account to
    another"""

    # Setup the logger configuration
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.DEBUG)
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

    # Not applicable: livemode, object, updated, default_price, created. 
    # Did you mean default_price_data?
    PRODUCT_KEYS_CP = ['id', 'active', 'attributes', 'description', 'images', 'metadata', 'name', 'package_dimensions', 'shippable', 'statement_descriptor', 'tax_code', 'unit_label', 'url']
    PRICE_KEYS_CP = [ 'currency', 'unit_amount_decimal', 'recurring', 'tax_behavior' ]


    # Retrieve the products from the source account
    for prod in stripe.Product.list(api_key=STRIPE_SOURCE_KEY):
        price = stripe.Price.retrieve(prod['default_price'], api_key=STRIPE_SOURCE_KEY)
        logger.info("Price = [%s]" % pformat(price))

        # Filter the attributes to the ones we need for creation
        prod_t = { key: prod[key] for key in prod.keys() if key in PRODUCT_KEYS_CP }
        # Set the price data on the target obj to the price obj we got from the source

        prod_t['default_price_data'] = {
            'currency'              : price['currency'],
            'unit_amount_decimal'   : price['unit_amount_decimal'],
            'tax_behavior'          : price['tax_behavior'],
            'recurring'             : {
                'interval' : price['recurring']['interval'],
                'interval_count' : price['recurring']['interval_count']
           }
        }


        logger.info("Product = [%s]" % pformat(prod))
        stripe.Product.create(**prod_t, api_key=STRIPE_TARGET_KEY)
        logger.info("Product: Created in target: %s[%s]" % (prod['name'], prod['id']))

if __name__ == '__main__':
    main()
