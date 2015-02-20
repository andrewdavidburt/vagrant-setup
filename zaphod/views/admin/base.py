from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from formencode import Schema, NestedVariables, ForEach, validators
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.view import view_config, view_defaults

from pyramid_uniform import Form, FormRenderer
from pyramid_es import get_client

from ... import model, custom_validators
from ...helpers.paginate import Page


@view_defaults(route_name='admin:base_edit', renderer='admin/base_edit.html')
class BaseEditView(object):
    def __init__(self, request):
        self.request = request

    def _get_object(self):
        request = self.request
        obj = self.cls.get(request.matchdict['id'])
        if not obj:
            raise HTTPNotFound
        return obj

    def _handle_images(self, form, obj):
        for image_params in form.data.pop('images'):
            pass

    @view_config(permission='authenticated')
    def edit(self):
        request = self.request
        obj = self._get_object()

        form = Form(request, schema=self.UpdateForm)
        if form.validate():
            if 'images' in form.data:
                self._handle_images(form, obj)
            form.bind(obj)
            request.flash('Saved changes.', 'success')
            return HTTPFound(location=request.current_route_url())

        return dict(obj=obj, renderer=FormRenderer(form))


@view_defaults(route_name='admin:base_list', renderer='admin/base_list.html')
class BaseListView(object):
    paginate = False

    def __init__(self, request):
        self.request = request

    @view_config(permission='authenticated')
    def index(self):
        request = self.request

        if 'q' in request.params:
            client = get_client(request)
            results = client.query(self.cls, q=request.params['q']).execute()
            return dict(results=results)
        else:
            q = model.Session.query(self.cls)
            final_q = q.order_by(self.cls.id.desc())
        if self.paginate:
            item_count = final_q.count()

            page = Page(request, final_q,
                        page=int(request.params.get('page', 1)),
                        items_per_page=20,
                        item_count=item_count)

            return dict(page=page)
        else:
            return dict(objs=final_q.all())


@view_defaults(route_name='admin:base_create',
               renderer='admin/base_create.html')
class BaseCreateView(object):

    def __init__(self, request):
        self.request = request

    @view_config(permission='authenticated')
    def create(self):
        request = self.request

        form = Form(request, schema=self.CreateForm)
        if form.validate():
            obj = self.cls(**form.data)
            model.Session.add(obj)
            model.Session.flush()
            request.flash("Created.", 'success')
            return HTTPFound(location=request.route_url(self.obj_route_name,
                                                        id=obj.id))

        return {'renderer': FormRenderer(form)}


class NodeUpdateForm(Schema):
    allow_extra_fields = False
    pre_validators = [NestedVariables()]

    name = validators.UnicodeString(max=255, not_empty=True)
    override_path = custom_validators.URLString(if_missing=None)

    keywords = validators.UnicodeString()
    teaser = validators.UnicodeString()
    body = validators.UnicodeString()

    listed = validators.Bool()
    published = validators.Bool()

    new_comment = custom_validators.CommentBody()
    images = ForEach(custom_validators.ImageAssociation())


class NodeEditView(BaseEditView):
    UpdateForm = NodeUpdateForm


class NodeListView(BaseListView):
    pass


class NodeCreateForm(Schema):
    allow_extra_fields = False
    name = validators.UnicodeString(max=255, not_empty=True)


class NodeCreateView(BaseCreateView):
    CreateForm = NodeCreateForm
