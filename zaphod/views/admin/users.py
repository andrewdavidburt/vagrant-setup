from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_defaults
from venusian import lift
from formencode import Schema, validators

from ... import mail, model, custom_validators

from ...admin import BaseEditView, BaseListView, BaseCreateView


@view_defaults(route_name='admin:user', renderer='admin/user.html',
               permission='admin')
@lift()
class UserEditView(BaseEditView):
    cls = model.User

    class UpdateForm(Schema):
        allow_extra_fields = False
        name = validators.UnicodeString(not_empty=True)
        email = validators.Email(not_empty=True)
        password = validators.UnicodeString()
        password2 = validators.UnicodeString()
        enabled = validators.Bool()
        admin = validators.Bool()
        show_admin_bars = validators.Bool()
        show_in_backers = validators.Bool()
        show_location = validators.UnicodeString()
        show_name = validators.UnicodeString()
        timezone = validators.String()
        url_path = custom_validators.URLString()
        twitter_username = custom_validators.TwitterUsername()
        chained_validators = [validators.FieldsMatch('password', 'password2')]
        new_comment = custom_validators.CommentBody()


@view_defaults(route_name='admin:users', renderer='admin/users.html',
               permission='admin')
@lift()
class UserListView(BaseListView):
    cls = model.User
    paginate = True


@view_defaults(route_name='admin:users:new',
               renderer='admin/users_new.html', permission='admin')
@lift()
class UserCreateView(BaseCreateView):
    cls = model.User
    obj_route_name = 'admin:user'

    class CreateForm(Schema):
        allow_extra_fields = False
        name = validators.UnicodeString(not_empty=True)
        email = validators.Email(not_empty=True)
        password = validators.UnicodeString()
        password2 = validators.UnicodeString()
        admin = validators.Bool()
        send_welcome_email = validators.Bool()
        chained_validators = [validators.FieldsMatch('password', 'password2')]

    def _create_object(self, form):
        request = self.request
        del form.data['password2']
        send_email = form.data.pop('send_welcome_email')
        obj = BaseCreateView._create_object(self, form)
        if send_email:
            token = obj.set_reset_password_token()
            mail.send_welcome_email(request, obj, token)
        return obj
