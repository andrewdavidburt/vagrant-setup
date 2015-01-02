from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_config
from formencode import Schema, NestedVariables, validators

from pyramid_uniform import Form, FormRenderer

from ... import model


class UpdateForm(Schema):
    "Schema for validating project update form."
    pre_validators = [NestedVariables()]
    name = validators.UnicodeString(max=255, not_empty=True)
    body = validators.UnicodeString()
    loaded_time = validators.Number(not_empty=True)
    listed = validators.Bool()
    published = validators.Bool()
    use_custom_paths = validators.Bool()
    creator_id = validators.Int(not_empty=True)
    teaser = validators.UnicodeString(max=255)
    vimeo_id = validators.Int()
    target = validators.Number()
    start_time = validators.DateConverter()
    # Remember we probably want to add a day to this value.
    end_time = validators.DateConverter()
    gravity = validators.Int(not_empty=True)


class ProjectsView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='admin:projects', renderer='admin/projects.html',
                 permission='authenticated')
    def index(self):
        q = model.Session.query(model.Project)
        return dict(projects=q.all())

    @view_config(route_name='admin:project', renderer='admin/project.html',
                 permission='authenticated')
    def edit(self):
        request = self.request
        project = model.Project.get(request.matchdict['id'])

        form = Form(request, schema=UpdateForm)
        if form.validate():
            # XXX do shit
            pass

        return dict(project=project, renderer=FormRenderer(form))
