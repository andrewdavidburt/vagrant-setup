from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging
import time

from . import model

log = logging.getLogger(__name__)


def generate_update_token(order_id, project_id, timestamp):
    # XXX
    return 'abcdef'


def verify_update_token(token, order_id, project_id, timestamp):
    # XXX
    return True


def update_payment_url(request, order, project):
    timestamp = int(time.time())
    sig = generate_update_token(order.id, project.id, timestamp)
    params = dict(order_id=order.id,
                  project_id=project.id,
                  timestamp=timestamp,
                  sig=sig)
    return request.route_url('update-payment', _query=params)


def capture_order(registry, project, order):
    """
    Ensure that the specified order has captured payments for all crowdfunding
    projects which are successful or pre-order/stock items.
    """
    log.info('capture_order start: %d', order.id)
    # - get most recent payment method on order.

    # - figure out amount owed.

    # - get payment gateway.

    # - get payment profile.

    # - try to run transaction.

    # - if failed, update cart item statuses and send payment failure email.

    # - if successful, update cart item statuses, record payment, and send
    #   payment confirmation email.

    # - commit transaction immediately.

    log.info('capture_order done: %d', order.id)


def capture_funds(registry, project):
    """
    Capture payments for all orders for a now-successful project.
    """
    assert project.successful, "project must be successful to capture funds"
    log.warn('capture_funds start: %d - %s', project.id, project.name)
    q = model.Session.query(model.Order).\
        join(model.Order.cart).\
        join(model.Cart.items).\
        join(model.CartItem.product).\
        filter(model.Product.project == project).\
        filter(model.CartItem.status != 'cancelled')
    count = failures = 0
    for order in q:
        success = capture_order(registry, order)
        count += 1
        if not success:
            failures += 1
    log.warn('capture_funds done: %d - %s / %d failed of %d',
             project.id, project.name, failures, count)
