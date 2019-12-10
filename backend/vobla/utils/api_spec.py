from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.tornado import TornadoPlugin

api_spec = APISpec(
    title="Vobla",
    version="0.0.1",
    openapi_version="2.0",
    info=dict(description="Vobla alpha API"),
    plugins=[MarshmallowPlugin(), TornadoPlugin()],
)


def api_spec_exists(handler_class):
    handler_class.api_spec_exists = True
    return handler_class
