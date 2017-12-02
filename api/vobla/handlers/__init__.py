import traceback

from webargs.tornadoparser import parser
from tornado import gen
from torndsession.sessionhandler import SessionBaseHandler

from vobla import errors


@parser.error_handler
def handle_error(error):
    raise errors.validation.VoblaValidationError(**error.messages)


class BaseHandler(SessionBaseHandler):

    def __init__(self, *ar, **kw):
        super(BaseHandler, self).__init__(*ar, **kw)

    @gen.coroutine
    def _execute(self, *ar, **kw):
        exception_occuired = False
        self.pgc = yield self.application.pg.acquire()
        try:
            yield super(BaseHandler, self)._execute(*ar, **kw)
        except Exception as e:
            exception_occuired = True
        yield self.pgc.close()
        if exception_occuired:
            raise

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header(
            'Access-Control-Allow-Headers',
            'Origin, X-Requested-With, Content-Type, Accept, Authorization'
        )
        self.set_header("Access-Control-Allow-Credentials", "true")
        self.set_header(
            'Access-Control-Allow-Methods', 'POST, GET, OPTIONS, DELETE, PUT'
        )
        self.set_header('Content-Type', 'application/json')

    async def options(self, *ar, **kw):
        self.set_status(204)
        self.finish()

    def write_error(self, status_code=500, **kwargs):
        resp_inner = {
            'message': self._reason
        }
        err_cls, err, tb = kwargs['exc_info']
        if issubclass(err_cls, errors.validation.VoblaValidationError):
            resp_inner['validation'] = err.messages
        if status_code == 500 and self.settings.get('serve_traceback'):
            resp_inner['traceback'] = traceback.format_exception(
                err_cls, err, tb
            )
        self.set_status(status_code)
        self.finish({
            'error': resp_inner
        })
