import os
import magic
from datetime import datetime

import psycopg2
from webargs.tornadoparser import use_args
from sqlalchemy import and_

from vobla import schemas
from vobla import errors
from vobla.handlers import BaseHandler
from vobla.utils import jwt_auth
from vobla.utils import api_spec_exists
from vobla.db import User, UserInvite, Drop, DropFile


@api_spec_exists
class UserDropsHandler(BaseHandler):

    async def get(self):
        '''
        ---
        description: Fetch information about User's Drops
        tags:
            - drops
        parameters:
            - in: header
              name: 'Authorization'
              type: string
              required: true
        responses:
            200:
                decsription: OK
            401:
                description: Invalid/Missing authorization header
                schema: ValidationErrorSchema
        '''
        drops = await Drop.select(
            self.pgc, Drop.c.owner_id==self.user.id
        )
        data = {
            'drops': []
        }
        self.set_status(200)
        self.write(data)
        self.finish()


@api_spec_exists
class DropHandler(BaseHandler):

    async def get(self, drop_hash):
        '''
        ---
        description: Fetch information about Drop
        tags:
            - drops
        parameters:
            - in: path
              name: drop_hash
              type: string
        responses:
            200:
                decsription: OK
        '''
        drop = await Drop.select(
            self.pgc, Drop.c.hash==drop_hash
        )
        data = {
        }
        self.set_status(200)
        self.write(data)
        self.finish()

    @jwt_auth.jwt_needed
    async def delete(self, drop_hash):
        '''
        ---
        description: Delete User's Drop
        tags:
            - drops
        parameters:
            - in: header
              name: 'Authorization'
              type: string
              required: true
            - in: path
              name: drop_hash
              type: string
        responses:
            200:
                decsription: OK
            401:
                description: Invalid/Missing authorization header
                schema: ValidationErrorSchema
        '''
        await Drop.delete(
            self.pgc,
            and_(
                Drop.c.hash==drop_hash,
                Drop.c.owner_id==self.user.id
            )
        )
        self.set_status(200)
        self.finish()


@api_spec_exists
class DropFilesHandler(BaseHandler):

    @jwt_auth.jwt_needed
    async def delete(self, drop_file_hash):
        '''
        ---
        description: Delete User's Drop
        tags:
            - drops
        parameters:
            - in: header
              name: 'Authorization'
              type: string
              required: true
            - in: path
              name: drop_hash
              type: string
        responses:
            200:
                decsription: OK
            401:
                description: Invalid/Missing authorization header
                schema: ValidationErrorSchema
        '''
        await DropFile.select(
            self.pgc,
            and_(
                DropFile.c.hash==drop_file_hash,
                DropFile.c.owner_id==self.user.id
            )
        )
        self.set_status(200)
        self.finish()

    async def get(self, drop_file_hash):
        '''
        ---
        description: Delete User's Drop
        tags:
            - drops
        parameters:
            - in: header
              name: 'Authorization'
              type: string
              required: true
            - in: path
              name: drop_hash
              type: string
        responses:
            200:
                decsription: OK
            401:
                description: Invalid/Missing authorization header
                schema: ValidationErrorSchema
        '''
        drop_file = await DropFile.select(
            self.pgc, DropFile.c.hash==drop_file_hash
        )
        data = {
        }
        self.set_status(200)
        self.write(data)
        self.finish()


@api_spec_exists
class DropsUploadHandler(BaseHandler):

    def set_default_headers(self):
        super(DropsUploadHandler, self).set_default_headers()
        self.set_header(
            'Access-Control-Allow-Headers',
            (
                'Origin, X-Requested-With, Content-Type, Accept, '
                'Authorization, Drop-File-Name, File-Total-Size, '
                'Chunk-Number, Chunk-Size, Drop-File-Hash'
            )
        )

    @jwt_auth.jwt_needed
    async def post(self):
        '''
        ---
        description: Upload a DropFile by chunks
        tags:
            - drops
        consumes:
            - multipart/form-data
        produces:
            - application/json
        parameters:
            - in: header
              name: 'Authorization'
              type: string
              required: true
            - in: header
              name: 'Drop-File-Name'
              description: If not provided will be the same as Drop's Hash
              type: string
              required: false
            - in: header
              name: 'Drop-Hash'
              description: If not provided new Drop will be created
              type: string
              required: false
            - in: header
              name: 'Drop-File-Hash'
              description: Not required for first upload
              type: string
              required: false
            - in: header
              name: 'Chunk-Number'
              type: integer
              required: true
            - in: header
              name: 'Chunk-Size'
              type: integer
              required: true
            - in: header
              name: 'File-Total-Size'
              type: integer
              required: true
            - in: formData
              name: chunk
              type: file
              required: true
        responses:
            201:
                description: DropFile uploaded
            200:
                description: Chunk uploaded
            200:
                description: First chunk uploaded
                schema: DropFileUploadedSchema
            401:
                description: Invalid/Missing authorization header
                schema: ValidationErrorSchema
            422:
                description: Invalid input data
                schema: ValidationErrorSchema
        '''
        async with self.pgc.begin():
            headers = self.request.headers
            data = {}
            for header in [
                'Chunk-Number',
                'Chunk-Size',
                'File-Total-Size'
            ]:
                if header not in headers:
                    raise errors.validation.VoblaValidationError(
                        header='%s header is missing' % header
                    )
            drop_file_name = headers.get('Drop-File-Name', None)
            chunk_number = headers.get('Chunk-Number', None)
            chunk_number = int(chunk_number)
            chunk_size = headers.get('Chunk-Size', None)
            chunk_size = int(chunk_size)
            file_total_size = headers.get('File-Total-Size', None)
            file_total_size = int(file_total_size)
            drop_file_hash = headers.get('Drop-File-Hash', None)
            drop_hash = headers.get('Drop-File', None)
            drop = None
            drop_file = None
            if drop_file_hash is None:
                if drop_hash is None:
                    drop = await Drop.create(
                        self.pgc, self.user, drop_file_name
                    )
                else:
                    drop = await Drop.select(self.pgc, Drop.c.hash==drop_hash)
                    if drop is None:
                        raise errors.validation.VoblaValidationError(
                            404, drop_hash='Drop with such hash is not found.'
                        )
                    elif drop.owner_id != self.user.id:
                        raise errors.validation.VoblaValidationError(
                            404, drop_hash='Drop with such hash is not yours.'
                        )
                drop_file = await DropFile.create(
                    self.pgc, drop, drop_file_name
                )
            else:
                drop_file = await DropFile.select(
                    self.pgc, DropFile.c.hash==drop_file_hash
                )
                if drop_file is None:
                    raise errors.validation.VoblaValidationError(
                        404,
                        drop_file_hash='DropFile with such hash is not found.'
                    )
                drop = await Drop.select(
                    self.pgc, Drop.c.id==drop_file.drop_id
                )
                if drop.owner_id != self.user.id:
                    raise errors.validation.VoblaValidationError(
                        404,
                        drop_file_hash='DropFile with such hash is not yours.'
                    )
            chunks_dir = drop_file.tmp_folder_path
            chunk_file_full_path = os.path.join(
                chunks_dir, "{}.part{}".format(drop_file.hash, chunk_number)
            )
            chunk = self.request.files.get('chunk', None)
            if chunk is None:
                raise errors.validation.VoblaValidationError(
                    chunk='Request does not contain DropFile\'s chunk.'
                )
            chunk = chunk[0]
            with open(chunk_file_full_path, 'wb+') as file:
                file.write(chunk.body)
            current_chunk_size = os.stat(chunk_file_full_path).st_size
            current_total_size = (chunk_number - 1) * chunk_size
            progress = (
                (current_total_size + current_chunk_size) / file_total_size
            )
            if progress >= 1:
                with open(drop_file.file_path, "ab") as target_file:
                    for i in range(1, 1 + chunk_number):
                        stored_chunk_file_name = os.path.join(
                            chunks_dir,
                            "{}.part{}".format(drop_file.hash, str(i))
                        )
                        stored_chunk_file = open(stored_chunk_file_name, 'rb')
                        target_file.write(stored_chunk_file.read())
                        stored_chunk_file.close()
                        os.unlink(stored_chunk_file_name)
                target_file.close()
                drop_file.mimetype = chunk['content_type']
                drop_file.uploaded_at = datetime.utcnow()
                await drop_file.update(self.pgc)
                self.set_status(201)
            else:
                self.set_status(200)
            if chunk_number == 1:
                self.write({
                    'drop_file_hash': drop_file.hash,
                    'drop_hash': drop.hash
                })
        self.finish()


@api_spec_exists
class DropFilesContentHandler(BaseHandler):

    async def get(self, drop_file_hash):
        '''
        ---
        description: Download a DropFile
        tags:
            - drops
        parameters:
            - in: path
              name: drop_file_hash
              type: string
              required: true
        responses:
            200:
                description: OK
            404:
                description: DropFile with such hash is not found
        '''
        async with self.pgc.begin():
            df = await DropFile.select(
                self.pgc,
                and_(
                    DropFile.c.hash==drop_file_hash,
                    DropFile.c.uploaded_at.isnot(None)
                )
            )
            if not df:
                self.set_status(404)
                self.finish()
            self.set_header('Content-Type', df.mimetype)
            with open(df.file_path, 'rb') as f:
                self.write(f.read())
            self.set_status(200)
            self.finish()
