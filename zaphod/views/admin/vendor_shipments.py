from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_defaults, view_config
from venusian import lift
from formencode import Schema, ForEach, NestedVariables, validators
from pyramid.httpexceptions import HTTPFound
from pyramid_uniform import Form, FormRenderer

from ... import model

from ...admin import BaseEditView


class ItemSchema(Schema):
    allow_extra_fields = False
    qty = validators.Int(not_empty=True, min=0)
    id = validators.Int(not_empty=True, min=0)


class ShipmentForm(Schema):
    "Schema for validating vendor shipment update form."
    allow_extra_fields = False
    pre_validators = [NestedVariables()]
    description = validators.UnicodeString()
    items = ForEach(ItemSchema)


@view_defaults(route_name='admin:vendor-shipment',
               renderer='admin/vendor_shipment.html', permission='admin')
@lift()
class VendorShipmentEditView(BaseEditView):
    cls = model.VendorShipment

    UpdateForm = ShipmentForm

    def _update_object(self, form, obj):
        request = self.request
        for item_params in form.data.pop('items'):
            vsi = model.VendorShipmentItem.get(item_params['id'])
            vsi.adjust_qty(item_params['qty'])
        form.bind(obj)
        request.flash('Saved changes.', 'success')

    @view_config(route_name='admin:vendor-order:receive-shipment',
                 renderer='admin/vendor_shipment_receive.html')
    def receive_shipment(self):
        request = self.request
        vendor_order = model.VendorOrder.get(request.matchdict['id'])

        form = Form(request, ShipmentForm)
        if form.validate():
            vendor_shipment = self.cls(vendor_order=vendor_order)
            for item_params in form.data.pop('items'):
                # create VSI
                pass
            form.bind(vendor_shipment)
            model.Session.flush()
            request.flash("Received shipment.", 'success')
            return HTTPFound(
                location=request.route_url('admin:vendor-shipment',
                                           id=vendor_shipment.id))

        return {
            'vendor_order': vendor_order,
            'renderer': FormRenderer(form),
        }
