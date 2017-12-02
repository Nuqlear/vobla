import json

from vobla.handlers import BaseHandler
from vobla.utils import api_spec


class OpenAPI2(BaseHandler):

    def get(self):
        return self.write(
            json.dumps(api_spec.to_dict())
        )
