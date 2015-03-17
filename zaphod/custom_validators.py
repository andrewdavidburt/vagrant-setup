from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import re
import itertools
import copy
from datetime import datetime, timedelta, time

import pytz
from formencode import validators, Schema, national, compound
from formencode.api import FancyValidator
from formencode.validators import Invalid, _


class URLString(validators.Regex):
    """
    Check if a string is a valid ('valid' for use in our URL conventions) URL
    slug.
    """
    regex = '^[a-z0-9\-\/]+$'


class TwitterUsername(validators.Regex):
    """
    Check if a string is a valid Twitter username.
    """
    regex = '^[a-zA-Z0-9\_]+$'


class SelectValidator(validators.FancyValidator):
    """
    A pre_validator that selects between two schema based on their 'selector'
    fields.

    E.g. inside a Schema:
        foo = SelectValidator({'a': ValidatorA(), 'b': ValidatorB()},
                              default=ValidatorDefault())

    If selector == 'a', ValidatorA will be used, if selector == 'b'
    ValidatorB will be used.
    """
    accept_iterator = True

    def __init__(self, validator_dict, default, selector_field='selector',
                 **kw):
        validators.FancyValidator.__init__(self, **kw)
        self.selector_field = selector_field
        self.validator_dict = validator_dict
        self.default = default

    def empty_value(self, value):
        return self._to_python(value, {})

    def _to_python(self, value, state):
        selector_field = value.pop(self.selector_field, None)
        if selector_field in self.validator_dict:
            v = self.validator_dict[selector_field]
        else:
            v = self.default
        return v.to_python(value)


class WildcardSchema(Schema):
    "A schema that doesn't do anything, so you can use it as a wildcard."
    allow_extra_fields = True
    filter_extra_fields = False
    if_missing = None


class BetterUSPhoneNumber(FancyValidator):
    messages = dict(
        phoneDigits=_('Please a number with exactly 10 digits, '
                      'e.g.  ###-###-####'))

    def strip_non_digits(self, value):
        return re.sub('[^0-9]', '', value)

    def strip_country_code(self, value):
        if (len(value) == 11) and (value[0] == '1'):
            return value[1:]
        else:
            return value

    def _to_python(self, value, state):
        self.assert_string(value, state)
        value = self.strip_non_digits(value)
        value = self.strip_country_code(value)
        if (len(value) != 10) or (value[0] == '0'):
            raise Invalid(self.message('phoneDigits', state),
                          value, state)
        return '%s-%s-%s' % (value[0:3], value[3:6], value[6:])

    _from_python = _to_python


class PhoneNumberInCountryFormat(FancyValidator):
    country_field = 'country'
    phone_field = 'phone'

    __unpackargs__ = ('country_field', 'phone_field')

    messages = dict(
        badFormat="Given phone number does not match the country's format.")

    _vd = {
        'US': BetterUSPhoneNumber,
    }

    # Switch to national.InternationalPhoneNumber to be more strict.
    default_validator = None

    def validate_python(self, fields_dict, state):
        country = fields_dict[self.country_field].upper()
        phone_validator = self._vd.get(country, self.default_validator)
        if phone_validator:
            try:
                fields_dict[self.phone_field] = phone_validator.to_python(
                    fields_dict[self.phone_field])
            except Invalid as e:
                message = self.message('badFormat', state)
                raise Invalid(
                    message, fields_dict, state,
                    error_dict={
                        self.phone_field: e.msg,
                        self.country_field: message,
                    })


class AddressSchema(Schema):
    "Validates a standard set of address fields."
    allow_extra_fields = True
    chained_validators = [
        national.PostalCodeInCountryFormat('country_code', 'postal_code'),
        PhoneNumberInCountryFormat('country_code', 'phone')]

    first_name = validators.UnicodeString(not_empty=True)
    last_name = validators.UnicodeString(not_empty=True)
    company = validators.UnicodeString()
    phone = validators.UnicodeString(not_empty=True)
    address1 = validators.UnicodeString(not_empty=True)
    address2 = validators.UnicodeString()
    city = validators.UnicodeString(not_empty=True)
    state = validators.UnicodeString(not_empty=True)
    postal_code = validators.UnicodeString(not_empty=True)
    country_code = validators.UnicodeString(not_empty=True)


class CreditCardValidator(validators.CreditCardValidator):
    __unpackargs__ = ('cc_number_field')

    def validate_partial(self, field_dict, state):
        if not field_dict.get(self.cc_number_field, None):
            return None
        self.validate_python(field_dict, state)

    def _validateReturn(self, field_dict, state):
        if self.cc_number_field not in field_dict:
            raise Invalid(
                self.message('missing_key', state, key=self.cc_number_field),
                "", state)

        number = field_dict[self.cc_number_field].strip()
        number = number.replace(' ', '').replace('-', '')
        try:
            int(number)
        except ValueError:
            return {self.cc_number_field: self.message('notANumber', state)}

        valid_type, valid_prefix = False, False
        for p, l in itertools.chain.from_iterable(self._cardInfo.values()):
            if number.startswith(p):
                valid_prefix = True
                if len(number) == l:
                    valid_type = True
                    break

        if not valid_type and valid_prefix:
            return {self.cc_number_field: self.message('badLength', state)}
        if not valid_type:
            return {self.cc_number_field: self.message('invalidNumber', state)}
        if not self._validateMod10(number):
            return {self.cc_number_field: self.message('invalidNumber', state)}
        return None


class CreditCardSecurityCode(validators.CreditCardSecurityCode):
    cc_number_field = 'ccNumber'

    __unpackargs__ = ('cc_number_field', 'cc_code_field')

    def validate_partial(self, field_dict, state):
        if (not field_dict.get(self.cc_type_field, None) or
                (not field_dict.get(self.cc_number_field, None))):
            return None
        self.validate_python(field_dict, state)

    def _validateReturn(self, field_dict, state):
        cc_code = str(field_dict[self.cc_code_field]).strip()

        cc_number = str(field_dict[self.cc_number_field]).strip()
        cc_number = re.sub(r"[^\d]", "", cc_number)
        cc_type = next((t for p, t in self._card_prefixes
                        if cc_number.startswith(p)), None)

        try:
            int(cc_code)
        except ValueError:
            return {self.cc_code_field: self.message('notANumber', state)}

        length = self._cardInfo[cc_type]
        validLength = False
        if len(cc_code) == length:
            validLength = True
        if not validLength:
            return {self.cc_code_field: self.message('badLength', state)}

    _card_prefixes = [('51', 'mastercard'),
                      ('52', 'mastercard'),
                      ('53', 'mastercard'),
                      ('54', 'mastercard'),
                      ('55', 'mastercard'),
                      ('300', 'dinersclub'),
                      ('301', 'dinersclub'),
                      ('302', 'dinersclub'),
                      ('303', 'dinersclub'),
                      ('304', 'dinersclub'),
                      ('305', 'dinersclub'),
                      ('36', 'dinersclub'),
                      ('38', 'dinersclub'),
                      ('6011', 'discover'),
                      ('34', 'amex'),
                      ('37', 'amex'),
                      ('4', 'visa'),
                      ('4', 'visa'),
                      ('3', 'jcb'),
                      ('2131', 'jcb'),
                      ('1800', 'jcb')]

    _cardInfo = dict(visa=3, mastercard=3, discover=3, amex=4, jcb=3)


class CreditCardExpires(validators.CreditCardExpires):
    """
    Subclass FormEncode's cc expiration validator to only use on error message,
    not two.
    """
    def _validateReturn(self, field_dict, state):
        errors = validators.CreditCardExpires._validateReturn(self, field_dict,
                                                              state)
        if errors:
            errors.pop(self.cc_expires_month_field, None)
            return errors


class CreditCardSchema(Schema):
    "Validates credit card fields."
    allow_extra_fields = False
    chained_validators = [
        CreditCardValidator(
            cc_number_field='number',
            messages={
                'badLength': "Credit card number required",
            }),
        CreditCardSecurityCode(
            cc_number_field='number',
            cc_code_field='code',
            messages={
                'notANumber': 'Security code required'
            }),
        CreditCardExpires(
            cc_expires_month_field='expires_month',
            cc_expires_year_field='expires_year')]
    number = validators.String(not_empty=True,
                               messages={
                                   'empty': "Credit card number required"
                               })
    expires_month = validators.String()
    expires_year = validators.String()
    code = validators.String(not_empty=True,
                             messages={
                                 'empty': "Security code required"
                             })
    save = validators.Bool()


class CommentBody(validators.FancyValidator):
    def _to_python(self, value, state):
        s = value.strip()
        if not s:
            return
        return (state.request.user, s)


class ImageAssociation(Schema):
    allow_extra_fields = False
    id = compound.Any(validators.Int(not_empty=True),
                      validators.Regex('^[a-z0-9]+$', not_empty=True))
    name = validators.UnicodeString(if_missing=None)
    fresh = validators.Bool()
    published = validators.Bool()
    gravity = validators.Int(not_empty=True)
    caption = validators.UnicodeString()
    alt = validators.UnicodeString()
    title = validators.UnicodeString()


class UTCDateConverter(validators.DateConverter):

    def __init__(self, add_day=False, *args, **kwargs):
        self.add_day = add_day
        validators.DateConverter.__init__(self, *args, **kwargs)

    def _to_python(self, value, state):
        request = state.request
        value = validators.DateConverter._to_python(self, value, state)
        if value:
            user_tz = pytz.timezone(request.user.timezone)
            dt = datetime.combine(value, time())
            dt = user_tz.localize(dt)
            dt_utc = dt.astimezone(pytz.utc).replace(tzinfo=None)

        if self.add_day:
            dt_utc += timedelta(days=1)

        return dt_utc


class CloneFields(FancyValidator):
    """
    A pre_validator to generalize copying one field (or set of fields) to
    another field.

    E.g.
    CloneFields('from_fields', 'to_fields', when='field_same_as_field')
    ->
    CloneFields('shipping', 'billing', when='billing_same_as_shipping')
    """

    def __init__(self, from_fields, to_fields, when):
        self.from_fields = from_fields
        self.to_fields = to_fields
        self.when = when

    def _to_python(self, value, state):
        if ((self.when in value) and
                validators.Bool.to_python(value[self.when])):
            from_val = value[self.from_fields]
            value[self.to_fields] = copy.copy(from_val)
        return value
