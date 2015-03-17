from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from unittest import TestCase

from ...views.cart import CheckoutForm


class TestCheckoutValidator(TestCase):
    maxDiff = 2000

    def test_saved_cc(self):
        self.assertEqual(CheckoutForm.to_python({
            'shipping.country_code': 'us',
            'shipping.first_name': 'Ben',
            'shipping.last_name': 'Bitdiddle',
            'shipping.company': '',
            'shipping.address1': '123 Main St',
            'shipping.address2': '',
            'shipping.city': 'Portland',
            'shipping.state': 'OR',
            'shipping.postal_code': '97214',
            'shipping.phone': '555-555-1212',
            'cc.use_saved': 'yes',
            'cc.number': '',
            'cc.expires_month': '01',
            'cc.expires_year': '2015',
            'cc.code': '',
            'cc.save': '1',
            'billing.country_code': 'us',
            'billing.first_name': 'Ben',
            'billing.last_name': 'Bitdiddle',
            'billing.company': '',
            'billing.address1': '44 Bella Vista Drive',
            'billing.address2': 'Suite 14',
            'billing.city': 'Portland',
            'billing.state': 'OR',
            'billing.postal_code': '97215',
            'billing.phone': '555-555-1212',
            'email': 'ben@example.com',
            'comments': 'Hello, world.',
        }), {
            'shipping': {
                'country_code': 'us',
                'first_name': 'Ben',
                'last_name': 'Bitdiddle',
                'company': '',
                'address1': '123 Main St',
                'address2': '',
                'city': 'Portland',
                'state': 'OR',
                'postal_code': '97214',
                'phone': '555-555-1212',
            },
            'cc': 'saved',
            'billing': {
                'country_code': 'us',
                'first_name': 'Ben',
                'last_name': 'Bitdiddle',
                'company': '',
                'address1': '44 Bella Vista Drive',
                'address2': 'Suite 14',
                'city': 'Portland',
                'state': 'OR',
                'postal_code': '97215',
                'phone': '555-555-1212',

            },
            'billing_same_as_shipping': False,
            'email': 'ben@example.com',
            'comments': 'Hello, world.',
        })


    def test_unsaved_cc(self):
        self.assertEqual(CheckoutForm.to_python({
            'shipping.country_code': 'us',
            'shipping.first_name': 'Ben',
            'shipping.last_name': 'Bitdiddle',
            'shipping.company': '',
            'shipping.address1': '123 Main St',
            'shipping.address2': '',
            'shipping.city': 'Portland',
            'shipping.state': 'OR',
            'shipping.postal_code': '97214',
            'shipping.phone': '555-555-1212',
            'cc.use_saved': 'no',
            'cc.number': '4111 1111 1111 1111',
            'cc.expires_month': '05',
            'cc.expires_year': '2020',
            'cc.code': '123',
            'cc.save': '1',
            'billing.country_code': 'us',
            'billing.first_name': 'Ben',
            'billing.last_name': 'Bitdiddle',
            'billing.company': '',
            'billing.address1': '44 Bella Vista Drive',
            'billing.address2': 'Suite 14',
            'billing.city': 'Portland',
            'billing.state': 'OR',
            'billing.postal_code': '97215',
            'billing.phone': '555-555-1212',
            'email': 'ben@example.com',
            'comments': 'Hello, world.',
        }), {
            'shipping': {
                'country_code': 'us',
                'first_name': 'Ben',
                'last_name': 'Bitdiddle',
                'company': '',
                'address1': '123 Main St',
                'address2': '',
                'city': 'Portland',
                'state': 'OR',
                'postal_code': '97214',
                'phone': '555-555-1212',
            },
            'cc': {
                'number': '4111 1111 1111 1111',
                'expires_month': '05',
                'expires_year': '2020',
                'code': '123',
                'save': True,
            },
            'billing': {
                'country_code': 'us',
                'first_name': 'Ben',
                'last_name': 'Bitdiddle',
                'company': '',
                'address1': '44 Bella Vista Drive',
                'address2': 'Suite 14',
                'city': 'Portland',
                'state': 'OR',
                'postal_code': '97215',
                'phone': '555-555-1212',

            },
            'billing_same_as_shipping': False,
            'email': 'ben@example.com',
            'comments': 'Hello, world.',
        })

