from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

try:
    from scrappy import model as scrappy_model
    from crowdsupply import model as cs_model
    from scrappy.model import meta as scrappy_meta
except ImportError:
    scrappy_meta = scrappy_model = cs_model = None

from ... import model


def migrate_inventory_adjustments():
    for old_adj in \
            scrappy_meta.Session.query(scrappy_model.InventoryAdjustment):
        print("  inventory adjustment %s" % old_adj.id)
        adj = model.InventoryAdjustment(
            id=old_adj.id,
            sku_id=old_adj.sku_id,
            acquisition_time=old_adj.acquisition_time,
            qty_diff=old_adj.qty_diff,
            user_id=old_adj.account_id,
            reason=old_adj.reason,
        )
        model.Session.add(adj)
    model.Session.flush()


def migrate_items(cart_item_map):
    for old_item in scrappy_meta.Session.query(scrappy_model.Item):
        print("  item %s" % old_item.id)
        if old_item.cart_item in cart_item_map:
            cart_item = cart_item_map[old_item.cart_item]
        else:
            cart_item = None
        item = model.Item(
            id=old_item.id,
            acquisition_id=old_item.acquisition_id,
            create_time=old_item.create_time,
            cost=old_item.cost,
            destroy_time=old_item.destroy_time,
            destroy_adjustment_id=old_item.destroy_adjustment_id,
            cart_item=cart_item,
        )
        model.Session.add(item)
    model.Session.flush()


def update_stock_flags():
    for product in model.Session.query(model.Product):
        product.update_in_stock()
