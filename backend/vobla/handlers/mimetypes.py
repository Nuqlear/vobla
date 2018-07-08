from vobla.utils import api_spec_exists
from vobla.handlers import BaseHandler

from vobla.utils.mimetypes import get_mimetype_preview


@api_spec_exists
class MimetypePreview(BaseHandler):
    async def get(self, mimetype):
        """
        ---
        description: Get mimetype preview image
        tags:
            - mimetypes
        parameters:
            - in: path
              name: mimetype
              type: string
        responses:
            200:
                description: OK
        """
        self.set_header("Content-Type", "image/png")
        with open(get_mimetype_preview(mimetype), "rb") as mimetype_preview:
            self.write(mimetype_preview.read())
        self.set_status(200)
        self.finish()
