from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging

from sqlalchemy import Column, ForeignKey, types, orm

from . import custom_types, utils
from .base import Base, Session
from .item import Acquisition, Item

log = logging.getLogger(__name__)


class Cart(Base):
    """
    A user's shopping cart. This object is used for tracking added items prior
    to and after checkout. After checkout, it will be associated with an Order.
    """
    __tablename__ = 'carts'
    id = Column(types.Integer, primary_key=True)
    updated_time = Column(types.DateTime, nullable=False,
                          default=utils.utcnow, index=True,
                          doc='Time this cart was refreshed by a user action.')

    order = orm.relationship('Order', uselist=False, backref='cart')
    items = orm.relationship('CartItem', backref='cart',
                             cascade='all, delete, delete-orphan')

    @property
    def total(self):
        return sum(ci.total for ci in self.items if ci.status != 'cancelled')

    @property
    def items_total(self):
        return sum((ci.price_each * ci.qty_desired) for ci in self.items
                   if ci.status != 'cancelled')

    @property
    def shipping_total(self):
        return sum(ci.shipping_price for ci in self.items
                   if ci.status != 'cancelled')

    @property
    def non_physical(self):
        """
        Return True if this cart is entirely non-physical.
        """
        return all(ci.product.non_physical for ci in self.items)

    @property
    def international_available(self):
        """
        Return True if international shipping is available for all items in
        this cart.
        """
        return all(ci.product.international_available
                   for ci in self.items)

    @property
    def international_surcharge_total(self):
        """
        Return total international shipping price for this cart.
        """
        return sum((ci.product.international_surcharge * ci.qty_desired)
                   for ci in self.items)

    def set_international_shipping(self):
        """
        Set shipping prices for all items in this cart to international
        surcharges.
        """
        for item in self.items:
            item.shipping_price = (item.product.international_surcharge *
                                   item.qty_desired)

    def set_initial_statuses(self):
        """
        Set initial item statuses for a new order.

        For a crowdfunding project, set to 'unfunded' or 'payment pending'
        depending on whether or not the project is successful.

        For a pre-order or stock project, set to 'in process'.
        """
        for item in self.items:
            project = item.product.project
            if item.stage == item.CROWDFUNDING:
                if project.successful:
                    item.update_status('payment pending')
                else:
                    item.update_status('unfunded')
            else:
                item.update_status('in process')

    def refresh(self):
        """
        Refresh item statuses and reservations.
        """
        self.updated_time = utils.utcnow()
        for item in self.items:
            item.refresh()


CROWDFUNDING = 0
PREORDER = 1
STOCK = 2


class CartItem(Base):
    """
    An item in a user's cart. After checkout, this object is used for tracking
    order fulfillment state.
    """
    __tablename__ = 'cart_items'
    id = Column(types.Integer, primary_key=True)
    cart_id = Column(None, ForeignKey('carts.id'), nullable=False)
    product_id = Column(None, ForeignKey('products.id'),
                        nullable=False)
    sku_id = Column(None, ForeignKey('skus.id'), nullable=False)
    batch_id = Column(None, ForeignKey('batches.id'), nullable=True)
    price_each = Column(custom_types.Money, nullable=False)
    qty_desired = Column(types.Integer, nullable=False, default=1)
    shipping_price = Column(custom_types.Money, nullable=False)
    stage = Column(types.Integer, nullable=False)

    expected_ship_time = Column(types.DateTime, nullable=True)
    shipped_time = Column(types.DateTime, nullable=True)
    shipment_id = Column(None, ForeignKey('shipments.id'), nullable=True)

    status = Column(types.CHAR(16), nullable=False, default='cart')

    product = orm.relationship('Product', backref='cart_items')
    batch = orm.relationship('Batch', backref='cart_items')
    sku = orm.relationship('SKU', backref='cart_items')

    CROWDFUNDING = 0
    PREORDER = 1
    STOCK = 2

    available_statuses = [
        ('cart', 'Pre-checkout'),
        ('unfunded', 'Project Not Yet Funded'),
        ('failed', 'Project Failed To Fund'),
        ('waiting', 'Waiting for Items'),
        ('payment pending', 'Payment Not Yet Processed'),
        ('payent failed', 'Payment Failed'),
        ('cancelled', 'Cancelled'),
        ('shipped', 'Shipped'),
        ('abandoned', 'Abandoned'),
        ('in process', 'In Process'),
        ('being packed', 'Being Packed'),
    ]

    @property
    def status_description(self):
        """
        Human-readable description of this item's status.
        """
        return dict(self.available_statuses)[self.status]

    def update_status(self, new_value):
        """
        Update the status of this item. Validates acceptable transitions.
        """
        valid_transitions = {
            'cart': ('unfunded', 'payment pending', 'in process'),
            'unfunded': ('failed', 'cancelled', 'payment pending'),
            'payment pending': ('cancelled', 'waiting', 'payment failed'),
            'payment failed': ('waiting', 'cancelled', 'abandoned'),
            'waiting': ('cancelled', 'in process', 'being packed', 'shipped'),
            'in process': ('cancelled', 'being packed', 'shipped'),
            'being packed': ('shipped',),
        }
        valid_next_statuses = valid_transitions.get(self.status, ())
        assert new_value in valid_next_statuses, \
            "invalid next cart item status: cannot %r -> %r" % (self.status,
                                                                new_value)
        self.status = new_value

    def calculate_price(self):
        """
        Calculate the price of this item including selected product option
        values.
        """
        price = self.product.price
        for ov in self.sku.option_values:
            price += ov.price_increase
        return price

    @property
    def total(self):
        """
        Total price of this line item, including shipping.
        """
        return (self.price_each + self.shipping_price) * self.qty_desired

    @property
    def qty_reserved(self):
        """
        Qty of product that is 'reserved' to this order.
        """
        if self.stage == STOCK:
            return Session.query(Item).filter_by(cart_item=self).count()
        else:
            return self.qty_desired

    @property
    def closed(self):
        """
        True if this item is in a final, resolved state.
        """
        return self.status in ('cancelled', 'shipped', 'abandoned', 'failed')

    def release_stock(self):
        """
        Release any reserved stock associated with this item.

        FIXME This is a very naive approach with no protection against race
        conditions.
        """
        q = Session.query(Item).filter_by(cart_item=self)
        for item in q:
            item.cart_item = None
        Session.flush()

    def reserve_stock(self):
        """
        Reserve stock associated with this item.

        FIXME This is a very naive approach with no protection against race
        conditions.
        """
        q = Session.query(Item).\
            join(Item.acquisition).\
            filter(Acquisition.sku == self.sku,
                   Item.destroy_time == None,
                   Item.cart_item_id == None).\
            limit(self.qty_desired)
        items = q.all()
        assert len(items) == self.qty_desired, \
            "only got %d items, wanted %d" % (len(items), self.qty_desired)
        for item in items:
            item.cart_item = self

    def refresh(self):
        """
        Refresh status and reservations. For a stock item, ensure that
        qty_reserved is up to date. For a preorder or crowdfunding item,
        allocate to a product batch. Note that since adding this cart item, the
        project may have changed status.

        This method may update .qty_desired, .stage, .batch,
        .expected_ship_time, and associated Item instances.

        Before doing anything, make sure that this cart item has no associated
        order.

        If insufficient qty is available, the .qty_desired will be decremented
        accordingly, and False will be returned. Otherwise, True will be
        returned.
        """
        log.info('refresh %s: begin', self.id)
        assert not self.cart.order, \
            "cannot refresh cart item that has a placed order"

        # XXX Lock existing items.

        # XXX The batch allocation needs to take into account qty-- e.g. if
        # there is only a certain qty available in crowdfunding, decrement the
        # qty.

        self.price_each = self.calculate_price()

        project = self.product.project
        if project.status == 'crowdfunding':
            log.info('refresh %s: selecting crowdfunding', self.id)
            self.stage = CROWDFUNDING
            self.batch = self.product.select_batch(self.qty_desired)
            assert self.batch
            self.expected_ship_time = self.batch.ship_time
            self.release_stock()
            log.info('refresh %s: good', self.id)
            return True
        else:
            self.release_stock()
            # Make sure that the product is available.
            accepts_preorders = (project.accepts_preorders and
                                 self.product.accepts_preorders)
            stock_available = self.sku.qty_available

            if accepts_preorders and self.product.batches:
                preorder_available = self.product.qty_remaining
                if preorder_available is None:
                    # This means a non-qty-limited product
                    preorder_available = self.qty_desired
            else:
                preorder_available = 0

            log.info('refresh %s: preorder_available: %s', self.id,
                     preorder_available)
            log.info('refresh %s: stock_available: %s', self.id,
                     stock_available)

            if stock_available >= self.qty_desired:
                log.info('refresh %s: selecting stock', self.id)
                self.reserve_stock()
                self.stage = STOCK
                self.batch = None
                self.expected_ship_time = utils.shipping_day()
                log.info('refresh %s: good', self.id)
                return True

            if stock_available >= preorder_available:
                log.info('refresh %s: selecting stock', self.id)
                self.qty_desired = stock_available
                self.reserve_stock()
                self.stage = STOCK
                self.batch = None
                self.expected_ship_time = utils.shipping_day()
                log.info('refresh %s: partial', self.id)
                return False

            if preorder_available > 0:
                log.info('refresh %s: selecting preorder', self.id)
                if preorder_available < self.qty_desired:
                    self.qty_desired = preorder_available
                    log.info('refresh %s: partial', self.id)
                    partial = True
                else:
                    log.info('refresh %s: good', self.id)
                    partial = False
                self.batch = self.product.select_batch(self.qty_desired)
                assert self.batch
                self.stage = PREORDER
                self.expected_ship_time = self.batch.ship_time
                self.release_stock()
                return (not partial)

            # This thing is no longer available.
            log.info('refresh %s: unavailable', self.id)
            self.qty_desired = 0
            self.batch = None
            self.expected_ship_time = None
            self.release_stock()
            log.info('refresh %s: fail', self.id)
            return False
