import logging
from datetime import date, timedelta

from itsdangerous import TimestampSigner

from . import model, payment, mail
from .payment.exc import TransactionDeclinedException

log = logging.getLogger(__name__)


def update_payment_url(request, order):
    settings = request.registry.settings
    signer = TimestampSigner(settings['payment.secret'])
    token = signer.sign(str(order.id))
    return request.route_url('update-payment', token=token)


def update_item_statuses(project, order, new_status):
    for item in order.cart.items:
        if ((item.status.key != 'cancelled') and
                (item.product.project == project)):
            item.update_status(new_status)


def update_unfunded(project, order):
    for item in order.cart.items:
        if ((item.status.key == 'unfunded') and
                (item.product.project == project)):
            item.update_status('payment pending')
    model.Session.flush()


def capture_order(request, project, order):
    """
    Ensure that the specified order has captured payments for all crowdfunding
    projects which are successful or pre-order/stock items.
    """
    registry = request.registry
    log.info('capture_order start: %d', order.id)

    update_unfunded(project, order)

    # - get most recent payment method on order.
    method = order.active_payment_method

    # - figure out amount owed.
    amount = order.current_due_amount - order.authorized_amount

    # - get payment gateway.
    iface = payment.get_payment_interface(registry, method.gateway.id)

    # - get payment profile.
    profile = iface.get_profile(method.reference)

    # - make descriptor
    descriptor = payment.make_descriptor(registry, order.id)

    # - try to run transaction.
    try:
        resp = profile.auth_capture(amount=amount,
                                    description='order-%d' % order.id,
                                    statement_descriptor=descriptor,
                                    ip=method.remote_addr,
                                    user_agent=request.user_agent,
                                    referrer=request.route_url('cart'))

    except TransactionDeclinedException:
        # - if failed, update cart item statuses and send payment failure
        # email.
        due_date = date.today() + timedelta(days=7)
        link = update_payment_url(request, order)
        mail.send_update_payment(request, project, order, due_date, link)
        update_item_statuses(project, order, 'payment failed')
        success = False

    else:
        # - if successful, update cart item statuses, record payment, and send
        # payment confirmation email.
        mail.send_payment_confirmation(request, project, order, amount)
        update_item_statuses(project, order, 'waiting')
        order.payments.append(model.CreditCardPayment(
            method=method,
            transaction_id=resp['transaction_id'],
            invoice_number=descriptor,
            authorized_amount=amount,
            amount=amount,
            avs_address1_result=resp['avs_address1_result'],
            avs_zip_result=resp['avs_zip_result'],
            ccv_result=resp['ccv_result'],
            card_type=resp['card_type'],
            created_by=request.user,
            descriptor=descriptor,
        ))
        success = True

    # - XXX commit transaction asap after this??

    log.info('capture_order done: %d', order.id)
    return success


def capture_funds(request, project, limit=5):
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
        filter(model.CartItem.status.in_(['payment pending', 'unfunded'])).\
        limit(limit)
    count = failures = 0
    for order in q:
        success = capture_order(request, project, order)
        count += 1
        if not success:
            failures += 1
    log.warn('capture_funds done: %d - %s / %d failed of %d',
             project.id, project.name, failures, count)
    return failures, count
