import json

from vobla.utils import jwt_auth
from vobla.utils import api_spec_exists
from vobla.handlers import BaseHandler


@api_spec_exists
class SharexUploader(BaseHandler):

    @jwt_auth.jwt_needed
    async def get(self):
        '''
        ---
        description: Get vobla's custom uploader for Sharex
        tags:
            - sharex
        responses:
            200:
                description: OK
            401:
                description: Invalid/Missing authorization header
                schema: ValidationErrorSchema
            404:
                description: DropFile with such hash is not found
                schema: VoblaHTTPErrorSchema
        '''
        self.set_status(200)
        data = {
            'Name': 'vobla',
            'DestinationType': 'ImageUploader',
            'RequestURL': 'https://vobla.olegshigor.in/api/drops/upload/blob',
            'FileFormName': 'blob',
            'Headers': {
                'Authorization': f'Bearer {self.user.make_jwt()}'
            },
            'URL': 'https://vobla.olegshigor.in/f/$json:drop_file_hash$'
        }
        self.set_header('Content-Disposition', 'attachment; filename=vobla.sxcu')
        self.finish(json.dumps(data))
