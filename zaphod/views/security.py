from pyramid.view import view_config


@view_config(route_name='security', renderer='security.html')
def security_view(request):
    return {}
