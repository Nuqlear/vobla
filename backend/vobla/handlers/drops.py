import os
import itertools
from datetime import datetime

import magic
from sqlalchemy import and_, select, desc, exists

from vobla import errors, tasks
from vobla.handlers import BaseHandler
from vobla.utils import jwt_auth
from vobla.utils import api_spec_exists
from vobla.db import models
from vobla.schemas.serializers.drops import (
    DropFileFirstChunkUploadSchema,
    UserDropsSchema
)


def utcnow2ms(utcnow: datetime):
    return int((utcnow - datetime(1970, 1, 1)).total_seconds() * 1000)


def get_dropfiles_paths(dropfiles):
    for dropfile in dropfiles:
        yield dropfile.file_path
        yield dropfile.temp_folder_path


@api_spec_exists
class UserDropsHandler(BaseHandler):

    @jwt_auth.jwt_needed
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
            - in: query
              name: cursor
              required: false
        responses:
            200:
                decsription: OK
                schema: UserDropsSchema
            401:
                description: Invalid/Missing authorization header
                schema: ValidationErrorSchema
        '''
        cursor = self.get_argument('cursor', None)
        if not cursor:
            created_at = datetime.utcnow()
        else:
            created_at = datetime.fromtimestamp(int(cursor)/1000.0)
        query = (
            models.Drop.t.select()
            .where(and_(
                models.Drop.c.owner_id == self.user.id,
                models.Drop.c.created_at < created_at
            ))
            .limit(80)
            .order_by(desc(models.Drop.c.created_at))
        )
        cursor = await self.pgc.execute(query)
        res = await cursor.fetchall()
        drops = []
        for row in res:
            drop = models.Drop._construct_from_row(row)
            drop.owner = self.user
            drop.dropfiles = await models.DropFile.select(
                self.pgc,
                and_(
                    models.DropFile.c.drop_id == drop.id,
                    models.DropFile.c.uploaded_at.isnot(None)
                ),
                return_list=True
            )
            drops.append(drop)
        data_for_dump = dict(drops=drops)
        if drops:
            next_cursor = utcnow2ms(drops[-1].created_at)
            cursor = await self.pgc.execute(
                select([
                    exists()
                    .where(models.Drop.c.created_at < drops[-1].created_at)
                ])
            )
            next_cursor_exists = await cursor.scalar()
            if next_cursor_exists:
                data_for_dump['next_cursor'] = next_cursor
            else:
                data_for_dump['next_cursor'] = -1
        self.set_status(200)
        self.finish(UserDropsSchema().dump(data_for_dump).data)

    @jwt_auth.jwt_needed
    async def delete(self):
        '''
        ---
        description: Delete User's Drops
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
        drops = await models.Drop.fetch(
            self.pgc,
            models.Drop.c.owner_id == self.user.id
        )
        if drops:
            await models.Drop.delete(
                self.pgc,
                models.Drop.c.owner_id == self.user.id
            )
            tasks.rmtree.delay(
                *itertools.chain(*[
                    get_dropfiles_paths(drop.dropfiles)
                    for drop in drops
                ])
            )
        self.set_status(200)
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
                schema: DropSchema
            404:
                description: Drop with such hash is not found
                schema: VoblaHTTPErrorSchema
        '''
        drop = await models.Drop.select(
            self.pgc, models.Drop.c.id == models.hashids.decode(drop_hash)[0]
        )
        if drop is None:
            raise errors.http.VoblaHTTPError(
                404, 'Drop with such hash is not found.'
            )
        data = await drop.serialize(self.pgc)
        self.set_status(200)
        self.finish(data)

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
            403:
                decsription: Drop is not owned by current user
            404:
                decsription: Drop not found
            401:
                description: Invalid/Missing authorization header
                schema: ValidationErrorSchema
        '''
        drops = await models.Drop.fetch(
            self.pgc,
            models.Drop.c.id == models.hashids.decode(drop_hash)[0]
        )
        if drops:
            drop = drops[0]
            if drop.owner_id != self.user.id:
                self.set_status(403)
            else:
                await models.Drop.delete(
                    self.pgc,
                    models.Drop.c.id == models.hashids.decode(drop_hash)[0]
                )
                self.set_status(200)
                tasks.rmtree.delay(*get_dropfiles_paths(drop.dropfiles))
        else:
            self.set_status(404)
        self.finish()


@api_spec_exists
class DropPreviewHandler(BaseHandler):

    async def get(self, drop_hash):
        '''
        ---
        description: Get Drop preview
        tags:
            - drops
        parameters:
            - in: path
              name: drop_hash
              type: string
        responses:
            200:
                decsription: OK
            404:
                description: Drop with such hash or its preview is not found
                schema: VoblaHTTPErrorSchema
        '''
        drop = await models.Drop.select(
            self.pgc,
            and_(
                models.Drop.c.id == models.hashids.decode(drop_hash)[0],
                models.Drop.c.is_preview_ready.is_(True)
            )
        )
        if drop is None:
            raise errors.http.VoblaHTTPError(
                404, 'Drop with such hash is not found.'
            )
        with open(drop.preview_path, 'rb') as f:
            preview_buffer = f.read()
            self.write(preview_buffer)
            self.set_header('Content-Type', magic.from_buffer(
                preview_buffer, mime=True
            ))
        self.set_status(200)
        self.finish()


@api_spec_exists
class DropFileHandler(BaseHandler):

    @jwt_auth.jwt_needed
    async def get(self, drop_file_hash):
        '''
        ---
        description: Delete User's DropFile
        tags:
            - drops
        parameters:
            - in: header
              name: 'Authorization'
              type: string
              required: true
            - in: path
              name: drop_file_hash
              type: string
        responses:
            200:
                decsription: OK
                schema: DropFileSchema
            404:
                decsription: DropFile not found
        '''
        dropfile = await models.DropFile.select(
            self.pgc,
            models.DropFile.c.id == models.hashids.decode(drop_file_hash)[0]
        )
        if dropfile is None:
            self.set_status(404)
        else:
            self.set_status(200)
            self.finish(dropfile.serializer.dump(dropfile).data)

    @jwt_auth.jwt_needed
    async def delete(self, drop_file_hash):
        '''
        ---
        description: Delete User's DropFile
        tags:
            - drops
        parameters:
            - in: header
              name: 'Authorization'
              type: string
              required: true
            - in: path
              name: drop_file_hash
              type: string
        responses:
            200:
                decsription: OK
            401:
                description: Invalid/Missing authorization header
                schema: ValidationErrorSchema
        '''
        async with self.pgc.begin():
            user_drops_cte = (
                select([models.Drop.c.id]).where(
                    models.Drop.c.owner_id == self.user.id
                ).cte('user_drops')
            )
            dropfile = await models.DropFile.select(
                self.pgc,
                and_(
                    models.DropFile.c.id == models.hashids.decode(drop_file_hash)[0],
                    models.DropFile.c.drop_id.in_(
                        select([user_drops_cte.c.id])
                    )
                )
            )
            await self.pgc.execute(
                models.DropFile.t.delete()
                .where(models.DropFile.c.id == dropfile.id)
            )
            await self.pgc.execute(
                models.Drop.t.update()
                .values(is_preview_ready=False)
                .where(models.Drop.c.id == dropfile.drop_id)
            )
            tasks.rmtree.delay(*get_dropfiles_paths([dropfile]))
        tasks.generate_previews.delay(dropfile.drop_id)
        self.set_status(200)
        self.finish()


@api_spec_exists
class DropUploadHandler(BaseHandler):

    def set_default_headers(self):
        super(DropUploadHandler, self).set_default_headers()
        self.set_header(
            'Access-Control-Allow-Headers',
            (
                'Origin, X-Requested-With, Content-Type, Accept, '
                'Authorization, Drop-File-Name, File-Total-Size, '
                'Chunk-Number, Chunk-Size, Drop-File-Hash, Drop-Hash'
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
                schema: DropFileFirstChunkUploadSchema
            401:
                description: Invalid/Missing authorization header
                schema: ValidationErrorSchema
            422:
                description: Invalid input data
                schema: ValidationErrorSchema
        '''
        async with self.pgc.begin():
            headers = self.request.headers
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
            chunk_number = int(headers.get('Chunk-Number'))
            chunk_size = int(headers.get('Chunk-Size'))
            file_total_size = int(headers.get('File-Total-Size'))
            drop_file_hash = headers.get('Drop-File-Hash', None)
            drop_hash = headers.get('Drop-Hash', None)
            drop = None
            drop_file = None
            if drop_file_hash is None:
                if drop_hash is None:
                    drop = await models.Drop.create(
                        self.pgc, self.user, drop_file_name
                    )
                else:
                    drop = await models.Drop.select(
                        self.pgc, models.Drop.c.id == models.hashids.decode(drop_hash)[0]
                    )
                    if drop is None:
                        raise errors.validation.VoblaValidationError(
                            404, **{
                                'Drop-Hash': (
                                    'Drop with such hash is not found.'
                                )
                            }
                        )
                    elif drop.owner_id != self.user.id:
                        raise errors.validation.VoblaValidationError(
                            403, **{
                                'Drop-Hash': (
                                    'Drop with such hash is not yours.'
                                )
                            }
                        )
                drop_file = await models.DropFile.create(
                    self.pgc, drop, drop_file_name
                )
            else:
                drop_file = await models.DropFile.select(
                    self.pgc, models.DropFile.c.hash == drop_file_hash
                )
                if drop_file is None:
                    raise errors.validation.VoblaValidationError(
                        404, **{
                            'Drop-File-Hash': (
                                'DropFile with such hash is not found.'
                            )
                        }
                    )
                drop = await models.Drop.select(
                    self.pgc, models.Drop.c.id == drop_file.drop_id
                )
                drop.is_preview_ready = False
                await drop.update(self.pgc)
                if drop.owner_id != self.user.id:
                    raise errors.validation.VoblaValidationError(
                        403, **{
                            'Drop-File-Hash': (
                                'DropFile with such hash is not yours.'
                            )
                        }
                    )
            chunks_dir = drop_file.temp_folder_path
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
                with open(drop_file.file_path, "ba+") as target_file:
                    for i in range(1, 1 + chunk_number):
                        stored_chunk_file_name = os.path.join(
                            chunks_dir,
                            "{}.part{}".format(drop_file.hash, str(i))
                        )
                        try:
                            stored_chunk_file = open(
                                stored_chunk_file_name, 'rb'
                            )
                        except FileNotFoundError:
                            raise errors.validation.VoblaValidationError(
                                **{
                                    'Chunk-Number': (
                                        f'Previous chunk #{i} not found.'
                                    )
                                }

                            )
                        target_file.write(stored_chunk_file.read())
                        stored_chunk_file.close()
                        os.unlink(stored_chunk_file_name)
                    target_file.seek(0)
                    drop_file.mimetype = magic.from_buffer(
                        target_file.read(1024), mime=True
                    )
                drop_file.uploaded_at = datetime.utcnow()
                await drop_file.update(self.pgc)
                self.set_status(201)
            else:
                self.set_status(200)
            if chunk_number == 1:
                serializer = DropFileFirstChunkUploadSchema()
                self.write(
                    serializer.dump({
                        'drop_file_hash': drop_file.hash,
                        'drop_hash': drop.hash
                    }).data
                )
        if progress >= 1:
            tasks.generate_previews.delay(drop.id)
        self.finish()


@api_spec_exists
class DropFileContentHandler(BaseHandler):

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
                schema: VoblaHTTPErrorSchema
        '''
        dropfile = await models.DropFile.select(
            self.pgc,
            and_(
                models.DropFile.c.id == models.hashids.decode(drop_file_hash)[0],
                models.DropFile.c.uploaded_at.isnot(None)
            )
        )
        if not dropfile:
            raise errors.http.VoblaHTTPError(
                404, 'DropFile with such hash is not found.'
            )
        self.set_header('Content-Type', dropfile.mimetype)
        with open(dropfile.file_path, 'rb') as f:
            self.write(f.read())
        self.set_status(200)
        self.finish()
