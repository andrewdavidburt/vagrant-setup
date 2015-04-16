from pyramid.view import view_defaults
from venusian import lift

from ... import model

from ...admin import NodeEditView


@view_defaults(route_name='admin:update', renderer='admin/update.html',
               permission='admin')
@lift()
class UpdateEditView(NodeEditView):
    cls = model.ProjectUpdate

    def _update_object(self, form, obj):
        NodeEditView._update_object(self, form, obj)
        self.request.theme.invalidate_project(obj.project.id)
