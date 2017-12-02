from apispec import APISpec


api_spec = APISpec(
    title='Vobla',
    version='0.0.1',
    info=dict(
        description='Vobla alpha API'
    ),
    plugins=['vobla.utils.api_spec.ext', 'apispec.ext.marshmallow']
)


def api_spec_exists(handler_class):
    handler_class.api_spec_exists = True
    return handler_class
